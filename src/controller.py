"""Pipeline controller for orchestrating stage execution and HITL checkpoints.

The controller is the main entry point for both CLI and web UI layers.
It manages pipeline state, stage transitions, and artifact approval workflow.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, UTC
import uuid

from .models import ApprovalStatus, ProjectContext, ProblemFraming
from .services.model_service import ModelService
from .services.persistence_service import PersistenceService
from .stages.base import StageResult, BaseStage
from .stages.project_setup import ProjectSetupStage
from .stages.problem_framing import ProblemFramingStage


class PipelineController:
    """Orchestrates pipeline execution across stages and manages HITL workflow.

    The controller:
    - Tracks current project state.
    - Executes stages and returns UI-agnostic results.
    - Handles artifact approval and state transitions.
    - Persists artifacts via PersistenceService.
    """

    def __init__(
        self,
        model_service: ModelService,
        persistence_service: PersistenceService,
    ):
        self.model_service = model_service
        self.persistence_service = persistence_service
        self._stages_registry: Dict[str, Any] = {}
        self._register_default_stages()

    def _register_default_stages(self) -> None:
        """Register built-in stages."""
        self.register_stage("project-setup", ProjectSetupStage)
        self.register_stage("problem-framing", ProblemFramingStage)

    def register_stage(self, stage_name: str, stage_class: Any) -> None:
        self._stages_registry[stage_name] = stage_class

    def start_project(self, raw_idea: str, project_id: Optional[str] = None) -> StageResult:
        """Initialize a new project by running the project-setup stage."""
        if project_id is None:
            project_id = f"project_{uuid.uuid4().hex[:8]}"

        stage_class = self._stages_registry.get("project-setup")
        stage: BaseStage = stage_class(self.model_service, self.persistence_service)
        result = stage.execute(raw_idea=raw_idea, project_id=project_id)

        # Ensure artifact persisted (stage already does this; safe idempotency)
        if result.draft_artifact:
            self.persistence_service.save_artifact(result.draft_artifact, project_id, result.draft_artifact.__class__.__name__)
        return result

    def run_stage(self, stage_name: str, project_id: str, **inputs: Any) -> StageResult:
        if stage_name not in self._stages_registry:
            raise ValueError(f"Stage '{stage_name}' is not registered.")
        if not self.persistence_service.project_exists(project_id):
            raise ValueError(f"Project '{project_id}' does not exist or has no artifacts yet.")

        stage_class = self._stages_registry[stage_name]
        stage: BaseStage = stage_class(self.model_service, self.persistence_service)
        result = stage.execute(project_id=project_id, **inputs)

        if result.draft_artifact:
            artifact_type = result.draft_artifact.__class__.__name__
            self.persistence_service.save_artifact(result.draft_artifact, project_id, artifact_type)

        # Persist extra artifacts if present
        for key, val in result.extra_data.items():
            if hasattr(val, "__class__"):
                self.persistence_service.save_artifact(val, project_id, val.__class__.__name__)
        return result

    def approve_artifact(
        self,
        project_id: str,
        artifact_type: str,
        artifact_class: Any,
        edits: Dict[str, Any],
        approval_status: ApprovalStatus = ApprovalStatus.APPROVED,
        user_notes: Optional[str] = None,
    ) -> None:
        artifact = self.persistence_service.load_artifact(artifact_type, project_id, artifact_class)
        if artifact is None:
            raise ValueError(f"Artifact '{artifact_type}' not found for project '{project_id}'.")

        for field_name, value in edits.items():
            if hasattr(artifact, field_name):
                setattr(artifact, field_name, value)

        artifact.status = approval_status
        artifact.updated_at = datetime.now(UTC)
        if user_notes:
            artifact.user_notes = user_notes

        self.persistence_service.save_artifact(artifact, project_id, artifact_type)

    def get_artifact(self, project_id: str, artifact_type: str, artifact_class: Any) -> Optional[Any]:
        return self.persistence_service.load_artifact(artifact_type, project_id, artifact_class)

    def list_projects(self) -> List[str]:
        return self.persistence_service.list_projects()

    def get_next_available_stages(self, project_id: str) -> List[str]:
        """Determine next stages based on approved artifacts.

        Simple logic for now:
        - If no ProjectContext approved -> only project-setup
        - If ProjectContext approved but no ProblemFraming -> problem-framing
        - Else return all registered (placeholder for future refinement)
        """
        available: List[str] = []
        context = self.get_artifact(project_id, "ProjectContext", ProjectContext)
        framing = self.get_artifact(project_id, "ProblemFraming", ProblemFraming)

        if context is None:
            available.append("project-setup")
            return available

        if context.status != ApprovalStatus.APPROVED and context.status != ApprovalStatus.APPROVED_WITH_NOTES:
            available.append("project-setup")
            return available

        if framing is None:
            available.append("problem-framing")
            return available

        # Future: logic for later stages
        return list(self._stages_registry.keys())
