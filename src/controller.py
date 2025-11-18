"""Pipeline controller for orchestrating stage execution and HITL checkpoints.

The controller is the main entry point for both CLI and web UI layers.
It manages pipeline state, stage transitions, and artifact approval workflow.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid

from .models import ApprovalStatus
from .services.model_service import ModelService
from .services.persistence_service import PersistenceService
from .stages.base import StageResult
from .stages import ProjectSetupStage


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
        """Initialize the pipeline controller.

        Args:
            model_service: Service for LLM/SLM interactions.
            persistence_service: Service for saving/loading artifacts.
        """
        self.model_service = model_service
        self.persistence_service = persistence_service
        self._stages_registry: Dict[str, Any] = {}  # stage_name -> Stage class
        # Register default stages
        self.register_stage("project-setup", ProjectSetupStage)

    def register_stage(self, stage_name: str, stage_class: Any) -> None:
        """Register a pipeline stage.

        Args:
            stage_name: Identifier for the stage.
            stage_class: The stage class to instantiate.
        """
        self._stages_registry[stage_name] = stage_class

    def start_project(self, raw_idea: str, project_id: Optional[str] = None) -> StageResult:
        """Initialize a new project and execute Stage 0 (Project Setup).

        Args:
            raw_idea: Free-text description of the research idea.
            project_id: Optional project ID (auto-generated if not provided).

        Returns:
            StageResult containing draft ProjectContext.
        """
        if project_id is None:
            project_id = f"project_{uuid.uuid4().hex[:8]}"

        # Prefer the registered stage implementation
        stage_cls = self._stages_registry.get("project-setup", ProjectSetupStage)
        stage = stage_cls(self.model_service, self.persistence_service)
        result = stage.execute(raw_idea=raw_idea, project_id=project_id)

        # Ensure draft artifact has the chosen project_id
        if result.draft_artifact and getattr(result.draft_artifact, "id", None) != project_id:
            result.draft_artifact.id = project_id

        # Save draft artifact
        if result.draft_artifact:
            self.persistence_service.save_artifact(result.draft_artifact, project_id, "ProjectContext")

        return result

    def run_stage(self, stage_name: str, project_id: str, **inputs: Any) -> StageResult:
        """Execute a specific pipeline stage.

        Args:
            stage_name: Identifier of the stage to run.
            project_id: The project ID.
            **inputs: Stage-specific input parameters.

        Returns:
            StageResult containing draft artifacts.

        Raises:
            ValueError: If stage is not registered or project doesn't exist.
        """
        if stage_name not in self._stages_registry:
            raise ValueError(f"Stage '{stage_name}' is not registered.")

        if not self.persistence_service.project_exists(project_id):
            raise ValueError(f"Project '{project_id}' does not exist.")

        # Instantiate and execute the stage
        stage_class = self._stages_registry[stage_name]
        stage = stage_class(self.model_service, self.persistence_service)

        result = stage.execute(project_id=project_id, **inputs)

        # Save the draft artifact
        if result.draft_artifact:
            artifact_type = result.draft_artifact.__class__.__name__
            self.persistence_service.save_artifact(
                result.draft_artifact, project_id, artifact_type
            )

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
        """Apply user edits and approve an artifact.

        Args:
            project_id: The project ID.
            artifact_type: Type identifier of the artifact.
            artifact_class: The artifact class for deserialization.
            edits: Dictionary of field -> value edits to apply.
            approval_status: The approval status to set.
            user_notes: Optional notes from the user.
        """
        # Load current artifact
        artifact = self.persistence_service.load_artifact(
            artifact_type, project_id, artifact_class
        )

        if artifact is None:
            raise ValueError(f"Artifact '{artifact_type}' not found for project '{project_id}'.")

        # Apply edits
        for field_name, value in edits.items():
            if hasattr(artifact, field_name):
                setattr(artifact, field_name, value)

        # Update status and metadata
        artifact.status = approval_status
        artifact.updated_at = datetime.now(timezone.utc)
        if user_notes:
            artifact.user_notes = user_notes

        # Save updated artifact
        self.persistence_service.save_artifact(artifact, project_id, artifact_type)

    def get_artifact(
        self, project_id: str, artifact_type: str, artifact_class: Any
    ) -> Optional[Any]:
        """Retrieve an artifact from storage.

        Args:
            project_id: The project ID.
            artifact_type: Type identifier of the artifact.
            artifact_class: The artifact class for deserialization.

        Returns:
            The artifact, or None if not found.
        """
        return self.persistence_service.load_artifact(
            artifact_type, project_id, artifact_class
        )

    def list_projects(self) -> List[str]:
        """List all project IDs.

        Returns:
            List of project ID strings.
        """
        return self.persistence_service.list_projects()

    def get_next_available_stages(self, project_id: str) -> List[str]:
        """Determine which stages can be run next based on current state.

        Args:
            project_id: The project ID.

        Returns:
            List of stage names that can be executed.
        """
        # TODO: Implement logic to check which artifacts are approved
        # and return only stages whose prerequisites are met.
        # For now, return all registered stages as a placeholder.
        return list(self._stages_registry.keys())
