"""Web UI for HITL Research Strategy Pipeline.

Modern, responsive interface using Flask + HTMX for optimal UX.
Follows progressive disclosure pattern - show users what they need, when they need it.
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pathlib import Path
import json
import sys

# Add project root to Python path to enable imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.controller import PipelineController
from src.models import ProjectContext, ProblemFraming, ConceptModel, ApprovalStatus
from src.services import FilePersistenceService, SimpleModelService

# Configure Flask with correct paths
template_dir = project_root / 'templates'
static_dir = project_root / 'static'

app = Flask(__name__,
            template_folder=str(template_dir),
            static_folder=str(static_dir))
app.config['SECRET_KEY'] = 'dev-key-change-in-production'

# Add Python built-ins to Jinja2 globals so templates can use them
app.jinja_env.globals.update({
    'hasattr': hasattr,
    'isinstance': isinstance,
    'str': str,
})

# Add custom Jinja2 filters
@app.template_filter('format_date')
def format_date(value, format_string='%B %d, %Y'):
    """Format a datetime object or string as a date."""
    if value is None:
        return ''
    if hasattr(value, 'strftime'):
        return value.strftime(format_string)
    return str(value)

# Initialize controller with absolute path for data
data_dir = project_root / 'data'
controller = PipelineController(
    SimpleModelService(),
    FilePersistenceService(base_dir=str(data_dir))
)


@app.route('/')
def index():
    """Landing page with project list and quick start."""
    projects = controller.list_projects()
    project_data = []

    for pid in projects:
        ctx = controller.get_artifact(pid, "ProjectContext", ProjectContext)
        if ctx:
            project_data.append({
                'id': pid,
                'title': ctx.title,
                'status': ctx.status.value,
                'created_at': ctx.created_at.isoformat() if hasattr(ctx.created_at, 'isoformat') else str(ctx.created_at),
            })

    return render_template('index.html', projects=project_data)


@app.route('/project/new', methods=['GET', 'POST'])
def new_project():
    """Create a new project (Stage 0)."""
    if request.method == 'POST':
        raw_idea = request.form.get('raw_idea', '').strip()

        if not raw_idea:
            return render_template('new_project.html', error="Please provide a research idea")

        # Create project
        result = controller.start_project(raw_idea=raw_idea)
        project_id = result.draft_artifact.id

        # If HTMX request, return partial
        if request.headers.get('HX-Request'):
            return redirect(url_for('project_detail', project_id=project_id))

        return redirect(url_for('project_detail', project_id=project_id))

    return render_template('new_project.html')


@app.route('/project/<project_id>')
def project_detail(project_id):
    """Project overview with stage progression."""
    if not controller.persistence_service.project_exists(project_id):
        return render_template('error.html', message="Project not found"), 404

    # Load all artifacts
    ctx = controller.get_artifact(project_id, "ProjectContext", ProjectContext)
    framing = controller.get_artifact(project_id, "ProblemFraming", ProblemFraming)
    concept_model = controller.get_artifact(project_id, "ConceptModel", ConceptModel)

    # Determine current stage and next actions
    next_stages = controller.get_next_available_stages(project_id)

    # Build stage status
    stages = [
        {
            'id': 'project-setup',
            'name': 'Project Setup',
            'number': 0,
            'status': _get_stage_status(ctx),
            'artifact': ctx,
        },
        {
            'id': 'problem-framing',
            'name': 'Problem Framing',
            'number': 1,
            'status': _get_stage_status(framing),
            'artifact': framing,
            'extra_artifacts': {'concept_model': concept_model} if concept_model else None,
        },
    ]

    return render_template(
        'project_detail.html',
        project_id=project_id,
        project=ctx,
        stages=stages,
        next_stages=next_stages,
    )


@app.route('/project/<project_id>/stage/<stage_name>', methods=['GET', 'POST'])
def stage_view(project_id, stage_name):
    """View and edit a specific stage's artifacts."""
    if request.method == 'POST':
        # Handle artifact approval/edits
        return _handle_stage_approval(project_id, stage_name)

    # Load current artifact
    artifact_map = {
        'project-setup': ('ProjectContext', ProjectContext),
        'problem-framing': ('ProblemFraming', ProblemFraming),
    }

    if stage_name not in artifact_map:
        return render_template('error.html', message="Unknown stage"), 404

    artifact_type, artifact_class = artifact_map[stage_name]
    artifact = controller.get_artifact(project_id, artifact_type, artifact_class)

    # If no artifact, run the stage
    if artifact is None:
        result = controller.run_stage(stage_name, project_id)
        artifact = result.draft_artifact
        prompts = result.prompts
    else:
        prompts = []

    # Load extra artifacts if needed
    extra = {}
    if stage_name == 'problem-framing':
        concept_model = controller.get_artifact(project_id, "ConceptModel", ConceptModel)
        if concept_model:
            extra['concept_model'] = concept_model

    return render_template(
        f'stages/{stage_name}.html',
        project_id=project_id,
        artifact=artifact,
        prompts=prompts,
        extra=extra,
    )


@app.route('/project/<project_id>/stage/<stage_name>/run', methods=['POST'])
def run_stage(project_id, stage_name):
    """Execute a stage and return the draft artifact view."""
    result = controller.run_stage(stage_name, project_id)

    # Return HTMX-friendly response
    artifact_map = {
        'project-setup': ('ProjectContext', ProjectContext),
        'problem-framing': ('ProblemFraming', ProblemFraming),
    }

    artifact_type, artifact_class = artifact_map[stage_name]
    artifact = result.draft_artifact

    extra = {}
    if stage_name == 'problem-framing' and result.extra_data:
        extra = result.extra_data

    if request.headers.get('HX-Request'):
        return render_template(
            f'partials/{stage_name}_form.html',
            artifact=artifact,
            prompts=result.prompts,
            extra=extra,
            editable=True,
        )

    return redirect(url_for('stage_view', project_id=project_id, stage_name=stage_name))


@app.route('/project/<project_id>/stage/<stage_name>/approve', methods=['POST'])
def approve_stage(project_id, stage_name):
    """Approve a stage artifact with optional edits."""
    artifact_map = {
        'project-setup': ('ProjectContext', ProjectContext),
        'problem-framing': ('ProblemFraming', ProblemFraming),
    }

    if stage_name not in artifact_map:
        return jsonify({'error': 'Unknown stage'}), 404

    artifact_type, artifact_class = artifact_map[stage_name]

    # Collect edits from form
    edits = {}
    for key in request.form:
        if key not in ['user_notes', 'action']:
            value = request.form.get(key)
            # Try to parse as JSON for list/dict fields
            if value.startswith('[') or value.startswith('{'):
                try:
                    value = json.loads(value)
                except:
                    pass
            edits[key] = value

    user_notes = request.form.get('user_notes', '').strip() or None

    # Apply approval
    controller.approve_artifact(
        project_id=project_id,
        artifact_type=artifact_type,
        artifact_class=artifact_class,
        edits=edits,
        approval_status=ApprovalStatus.APPROVED,
        user_notes=user_notes,
    )

    # Return success with next step
    if request.headers.get('HX-Request'):
        return render_template(
            'partials/approval_success.html',
            stage_name=stage_name,
            project_id=project_id,
        )

    return redirect(url_for('project_detail', project_id=project_id))


@app.route('/api/projects/<project_id>/artifacts/<artifact_type>', methods=['GET'])
def get_artifact_api(project_id, artifact_type):
    """API endpoint to get artifact as JSON."""
    artifact_classes = {
        'ProjectContext': ProjectContext,
        'ProblemFraming': ProblemFraming,
        'ConceptModel': ConceptModel,
    }

    if artifact_type not in artifact_classes:
        return jsonify({'error': 'Unknown artifact type'}), 404

    artifact = controller.get_artifact(project_id, artifact_type, artifact_classes[artifact_type])

    if artifact is None:
        return jsonify({'error': 'Artifact not found'}), 404

    # Convert to dict (simplified - would need proper serialization)
    from dataclasses import asdict
    return jsonify(asdict(artifact))


def _get_stage_status(artifact):
    """Determine stage status from artifact."""
    if artifact is None:
        return 'not_started'
    elif artifact.status == ApprovalStatus.APPROVED:
        return 'approved'
    elif artifact.status == ApprovalStatus.DRAFT:
        return 'draft'
    else:
        return 'in_progress'


def _handle_stage_approval(project_id, stage_name):
    """Handle POST request for stage approval."""
    # This is called by approve_stage route
    pass


if __name__ == '__main__':
    # Ensure all required directories exist
    template_dir.mkdir(exist_ok=True)
    (template_dir / 'stages').mkdir(exist_ok=True)
    (template_dir / 'partials').mkdir(exist_ok=True)
    static_dir.mkdir(exist_ok=True)
    (static_dir / 'css').mkdir(exist_ok=True)
    (static_dir / 'js').mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)

    print("\n" + "="*60)
    print("HITL Research Strategy Pipeline - Web UI")
    print("="*60)
    print(f"\nTemplate directory: {template_dir}")
    print(f"Static directory:   {static_dir}")
    print(f"Data directory:     {data_dir}")
    print(f"\nServer starting on: http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    print("="*60 + "\n")

    app.run(debug=True, port=5000)

