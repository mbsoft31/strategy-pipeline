"""Basic CLI for the HITL research strategy pipeline.

This provides simple commands to start projects, run stages, and approve artifacts.
No external dependencies - uses only Python stdlib argparse.
"""
import argparse
import sys
import json
import re
from pathlib import Path

from src.controller import PipelineController
from src.models import ProjectContext, ProblemFraming, ConceptModel, ApprovalStatus
from src.services import FilePersistenceService, SimpleModelService


PROJECT_ID_PATTERN = re.compile(r"project_[0-9a-f]{8}")


def _build_controller(data_dir: str) -> PipelineController:
    return PipelineController(SimpleModelService(), FilePersistenceService(data_dir))


def cmd_start(args):
    controller = _build_controller(args.data_dir)
    result = controller.start_project(raw_idea=args.idea, project_id=args.project_id)

    if result.validation_errors:
        print("\nERROR: validation errors:")
        for err in result.validation_errors:
            print(f"  - {err}")
        return 1

    ctx = result.draft_artifact
    print(json.dumps({
        "project_id": ctx.id,
        "title": ctx.title,
        "keywords": ctx.initial_keywords,
        "prompts": result.prompts,
        "artifact_path": f"{args.data_dir}/{ctx.id}/ProjectContext.json"
    }, indent=2))
    return 0


def cmd_run_stage(args):
    controller = _build_controller(args.data_dir)
    try:
        result = controller.run_stage(args.stage, args.project_id)
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        return 1

    if result.validation_errors:
        print(json.dumps({"validation_errors": result.validation_errors}, indent=2))
        return 1

    artifact_type = result.draft_artifact.__class__.__name__ if result.draft_artifact else None
    extra = {}
    for k, v in result.extra_data.items():
        extra[k] = v.__class__.__name__ if hasattr(v, "__class__") else str(v)

    print(json.dumps({
        "stage": args.stage,
        "project_id": args.project_id,
        "artifact_type": artifact_type,
        "prompts": result.prompts,
        "extra_artifacts": extra,
        "artifact_path": f"{args.data_dir}/{args.project_id}/{artifact_type}.json" if artifact_type else None
    }, indent=2))
    return 0


def cmd_approve(args):
    controller = _build_controller(args.data_dir)

    artifact_classes = {
        "ProjectContext": ProjectContext,
        "ProblemFraming": ProblemFraming,
        "ConceptModel": ConceptModel,
    }

    if args.artifact_type not in artifact_classes:
        print(json.dumps({"error": f"Unknown artifact type {args.artifact_type}"}))
        return 1

    edits = {}
    if args.edits:
        try:
            edits = json.loads(args.edits)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON in --edits: {e}"}))
            return 1

    try:
        controller.approve_artifact(
            project_id=args.project_id,
            artifact_type=args.artifact_type,
            artifact_class=artifact_classes[args.artifact_type],
            edits=edits,
            approval_status=ApprovalStatus.APPROVED,
            user_notes=args.notes,
        )
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        return 1

    print(json.dumps({
        "project_id": args.project_id,
        "artifact_type": args.artifact_type,
        "status": "APPROVED",
        "applied_edits": list(edits.keys()),
        "notes": args.notes,
    }, indent=2))
    return 0


def cmd_list(args):
    controller = _build_controller(args.data_dir)
    projects = controller.list_projects()
    summary = []
    for pid in projects:
        ctx = controller.get_artifact(pid, "ProjectContext", ProjectContext)
        summary.append({
            "project_id": pid,
            "title": ctx.title if ctx else None,
            "status": ctx.status.value if ctx else None,
        })
    print(json.dumps({"projects": summary}, indent=2))
    return 0


def cmd_show(args):
    controller = _build_controller(args.data_dir)
    if not controller.persistence_service.project_exists(args.project_id):
        print(json.dumps({"error": f"Project '{args.project_id}' not found"}))
        return 1

    project_dir = Path(args.data_dir) / args.project_id
    artifacts = [f.stem for f in project_dir.glob("*.json")]
    ctx = controller.get_artifact(args.project_id, "ProjectContext", ProjectContext)
    framing = controller.get_artifact(args.project_id, "ProblemFraming", ProblemFraming)
    concept_model = controller.get_artifact(args.project_id, "ConceptModel", ConceptModel)
    next_stages = controller.get_next_available_stages(args.project_id)

    print(json.dumps({
        "project_id": args.project_id,
        "artifacts": artifacts,
        "context": {
            "title": ctx.title if ctx else None,
            "status": ctx.status.value if ctx else None,
            "keywords": ctx.initial_keywords[:10] if ctx else None,
        },
        "problem_framing": {
            "problem_statement": framing.problem_statement if framing else None,
            "goals": framing.goals if framing else None,
            "status": framing.status.value if framing else None,
        } if framing else None,
        "concept_model": {
            "concept_count": len(concept_model.concepts) if concept_model else 0,
            "status": concept_model.status.value if concept_model else None,
        } if concept_model else None,
        "next_stages": next_stages,
    }, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description="HITL Research Strategy Pipeline CLI")
    parser.add_argument("--data-dir", default="./data", help="Data directory for projects")

    subparsers = parser.add_subparsers(dest="command")

    start_parser = subparsers.add_parser("start", help="Start a new project (Stage 0)")
    start_parser.add_argument("idea", help="Raw research idea (text)")
    start_parser.add_argument("--project-id", help="Optional project ID (auto-generated if omitted)")

    run_parser = subparsers.add_parser("run-stage", help="Run a specific pipeline stage")
    run_parser.add_argument("stage", help="Stage name (e.g., 'problem-framing')")
    run_parser.add_argument("project_id", help="Project ID")

    approve_parser = subparsers.add_parser("approve", help="Approve an artifact")
    approve_parser.add_argument("project_id", help="Project ID")
    approve_parser.add_argument("artifact_type", help="Artifact type (e.g., 'ProjectContext')")
    approve_parser.add_argument("--edits", help="JSON object with field edits")
    approve_parser.add_argument("--notes", help="User notes")

    list_parser = subparsers.add_parser("list", help="List all projects")

    show_parser = subparsers.add_parser("show", help="Show project details")
    show_parser.add_argument("project_id", help="Project ID")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "start": cmd_start,
        "run-stage": cmd_run_stage,
        "approve": cmd_approve,
        "list": cmd_list,
        "show": cmd_show,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
