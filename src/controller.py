"""Pipeline controller facade for orchestrating stage execution and HITL checkpoints.

The controller is the main entry point for both CLI and web UI layers.
It provides a unified API that coordinates the orchestration layer components.

REFACTORED: This controller now acts as a facade pattern, delegating responsibilities
to specialized classes in the orchestration layer:
- ArtifactManager: Handles artifact persistence and approval workflows
- ProjectNavigator: Manages stage progression and project status
- StageOrchestrator: Executes pipeline stages and manages stage registry

This refactoring maintains 100% backward compatibility with existing interfaces.
"""

from typing import Any, Dict, List, Optional

from .models import ApprovalStatus
from .services.model_service import ModelService
from .services.persistence_service import PersistenceService
from .stages.base import StageResult
from .orchestration.artifact_manager import ArtifactManager
from .orchestration.project_navigator import ProjectNavigator
from .orchestration.stage_orchestrator import StageOrchestrator


class PipelineController:
    """Facade for pipeline orchestration.
    
    Coordinates ProjectNavigator, ArtifactManager, and StageOrchestrator
    to provide a unified API for CLI and web interfaces.
    
    The controller maintains the same public interface as before but delegates
    all work to specialized components for better separation of concerns.
    """

    def __init__(
        self,
        model_service: ModelService,
        persistence_service: PersistenceService,
    ):
        """Initialize the controller and its orchestration components.
        
        Args:
            model_service: The model service for LLM operations.
            persistence_service: The persistence service for data storage.
        """
        # Create specialized orchestration components
        self.artifact_manager = ArtifactManager(persistence_service)
        self.project_navigator = ProjectNavigator(self.artifact_manager)
        self.stage_orchestrator = StageOrchestrator(
            model_service,
            self.artifact_manager,
        )
        
        # Keep references to original services for backward compatibility
        self.model_service = model_service
        self.persistence_service = persistence_service

    # ===== Stage Execution Methods (delegate to StageOrchestrator) =====

    def register_stage(self, stage_name: str, stage_class: Any) -> None:
        """Register a custom stage.
        
        Args:
            stage_name: The name/identifier for the stage.
            stage_class: The stage class (must inherit from BaseStage).
        """
        return self.stage_orchestrator.register_stage(stage_name, stage_class)

    def start_project(
        self, raw_idea: str, project_id: Optional[str] = None
    ) -> StageResult:
        """Initialize a new project by running the project-setup stage.
        
        Args:
            raw_idea: The user's raw research idea/description.
            project_id: Optional project ID (auto-generated if not provided).
            
        Returns:
            StageResult containing the ProjectContext artifact.
        """
        return self.stage_orchestrator.start_project(raw_idea, project_id)

    def run_stage(
        self, stage_name: str, project_id: str, **inputs: Any
    ) -> StageResult:
        """Execute a pipeline stage.
        
        Args:
            stage_name: The name of the stage to execute.
            project_id: The ID of the project.
            **inputs: Additional keyword arguments passed to stage.execute().
            
        Returns:
            StageResult containing artifacts and execution metadata.
            
        Raises:
            ValueError: If stage is not registered or project doesn't exist.
        """
        return self.stage_orchestrator.run_stage(stage_name, project_id, **inputs)

    # ===== Artifact Management Methods (delegate to ArtifactManager) =====

    def get_artifact(
        self, project_id: str, artifact_type: str, artifact_class: Any
    ) -> Optional[Any]:
        """Load an artifact from persistence.
        
        Args:
            project_id: The ID of the project.
            artifact_type: The type/name of the artifact.
            artifact_class: The class to deserialize the artifact into.
            
        Returns:
            The loaded artifact instance, or None if not found.
        """
        return self.artifact_manager.get_artifact(
            project_id, artifact_type, artifact_class
        )

    def approve_artifact(
        self,
        project_id: str,
        artifact_type: str,
        artifact_class: Any,
        edits: Dict[str, Any],
        approval_status: ApprovalStatus = ApprovalStatus.APPROVED,
        user_notes: Optional[str] = None,
    ) -> None:
        """Apply edits, update status, and persist artifact.
        
        Args:
            project_id: The ID of the project.
            artifact_type: The type/name of the artifact.
            artifact_class: The class of the artifact.
            edits: Dictionary of field names to new values.
            approval_status: The approval status to set.
            user_notes: Optional notes from the user.
            
        Raises:
            ValueError: If the artifact is not found.
        """
        return self.artifact_manager.approve_artifact(
            project_id,
            artifact_type,
            artifact_class,
            edits,
            approval_status,
            user_notes,
        )

    def list_projects(self) -> List[str]:
        """List all available projects.
        
        Returns:
            List of project IDs.
        """
        return self.artifact_manager.list_projects()

    # ===== Navigation Methods (delegate to ProjectNavigator) =====

    def get_next_available_stages(self, project_id: str) -> List[str]:
        """Determine next stages based on approved artifacts.
        
        Args:
            project_id: The ID of the project to check.
            
        Returns:
            List of stage names that can be executed.
        """
        return self.project_navigator.get_next_available_stages(project_id)
