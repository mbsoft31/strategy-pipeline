"""Stage execution and registry management.

This module handles stage registration, execution, and result persistence.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING
import uuid

from ..services.model_service import ModelService
from ..stages.base import StageResult, BaseStage
from ..stages.project_setup import ProjectSetupStage
from ..stages.problem_framing import ProblemFramingStage
from ..stages.research_questions import ResearchQuestionStage
from ..stages.search_concept_expansion import SearchConceptExpansionStage
from ..stages.database_query_plan import DatabaseQueryPlanStage
from ..stages.screening_criteria import ScreeningCriteriaStage
from ..stages.strategy_export import StrategyExportStage

if TYPE_CHECKING:
    from .artifact_manager import ArtifactManager


class StageOrchestrator:
    """Executes pipeline stages and manages stage registry.

    This class is responsible for:
    - Maintaining a registry of available pipeline stages
    - Executing stages with proper dependency injection
    - Persisting stage results and artifacts
    - Validating stage execution preconditions

    It coordinates between the ModelService (for LLM operations) and
    ArtifactManager (for persistence).
    """

    def __init__(
        self,
        model_service: ModelService,
        artifact_manager: "ArtifactManager",
    ):
        """Initialize the StageOrchestrator.

        Args:
            model_service: The model service for LLM operations.
            artifact_manager: The artifact manager for persistence.
        """
        self.model_service = model_service
        self.artifact_manager = artifact_manager
        self._stages_registry: Dict[str, Any] = {}
        self._register_default_stages()

    def _register_default_stages(self) -> None:
        """Register all built-in pipeline stages."""
        self.register_stage("project-setup", ProjectSetupStage)
        self.register_stage("problem-framing", ProblemFramingStage)
        self.register_stage("research-questions", ResearchQuestionStage)
        self.register_stage("search-concept-expansion", SearchConceptExpansionStage)
        self.register_stage("database-query-plan", DatabaseQueryPlanStage)
        self.register_stage("screening-criteria", ScreeningCriteriaStage)
        self.register_stage("strategy-export", StrategyExportStage)

    def register_stage(self, stage_name: str, stage_class: Any) -> None:
        """Register a stage class in the registry.

        Args:
            stage_name: The name/identifier for the stage (e.g., "project-setup").
            stage_class: The stage class (must inherit from BaseStage).

        Example:
            >>> orchestrator.register_stage("custom-stage", CustomStage)
        """
        self._stages_registry[stage_name] = stage_class

    def get_stage_class(self, stage_name: str) -> Optional[Any]:
        """Get a registered stage class.

        Args:
            stage_name: The name of the stage to retrieve.

        Returns:
            The stage class if registered, None otherwise.
        """
        return self._stages_registry.get(stage_name)

    def list_registered_stages(self) -> list[str]:
        """List all registered stage names.

        Returns:
            List of stage names in the registry.

        Example:
            >>> orchestrator.list_registered_stages()
            ['project-setup', 'problem-framing', ...]
        """
        return list(self._stages_registry.keys())

    def start_project(
        self, raw_idea: str, project_id: Optional[str] = None
    ) -> StageResult:
        """Initialize a new project (runs project-setup stage).

        This is a convenience method that generates a project ID if needed
        and runs the project-setup stage.

        Args:
            raw_idea: The user's raw research idea/description.
            project_id: Optional project ID (auto-generated if not provided).

        Returns:
            StageResult containing the ProjectContext artifact.

        Example:
            >>> result = orchestrator.start_project("Investigating AI in healthcare")
            >>> project_id = result.draft_artifact.id
        """
        if project_id is None:
            project_id = f"project_{uuid.uuid4().hex[:8]}"

        stage_class = self._stages_registry.get("project-setup")
        if stage_class is None:
            raise ValueError("project-setup stage is not registered.")

        # Create stage instance with dependencies
        # Note: Stages need persistence_service, not artifact_manager
        # We'll pass artifact_manager's persistence_service
        stage: BaseStage = stage_class(
            self.model_service,
            self.artifact_manager.persistence_service,
        )

        # Execute the stage
        result = stage.execute(raw_idea=raw_idea, project_id=project_id)

        # Persist the draft artifact
        if result.draft_artifact:
            self.artifact_manager.save_artifact(
                result.draft_artifact,
                project_id,
                result.draft_artifact.__class__.__name__,
            )

        return result

    def run_stage(
        self, stage_name: str, project_id: str, **inputs: Any
    ) -> StageResult:
        """Execute a pipeline stage and persist results.

        This method:
        1. Validates the stage exists and project exists
        2. Instantiates the stage with dependencies
        3. Executes the stage with provided inputs
        4. Persists all artifacts (draft_artifact and extra_data)

        Args:
            stage_name: The name of the stage to execute.
            project_id: The ID of the project.
            **inputs: Additional keyword arguments passed to stage.execute().

        Returns:
            StageResult containing artifacts and execution metadata.

        Raises:
            ValueError: If stage is not registered or project doesn't exist.

        Example:
            >>> result = orchestrator.run_stage(
            ...     "problem-framing",
            ...     project_id="proj_123"
            ... )
        """
        # Validate stage exists
        if stage_name not in self._stages_registry:
            raise ValueError(f"Stage '{stage_name}' is not registered.")

        # Validate project exists
        if not self.artifact_manager.project_exists(project_id):
            raise ValueError(
                f"Project '{project_id}' does not exist or has no artifacts yet."
            )

        # Get stage class and instantiate
        stage_class = self._stages_registry[stage_name]
        stage: BaseStage = stage_class(
            self.model_service,
            self.artifact_manager.persistence_service,
        )

        # Execute the stage
        result = stage.execute(project_id=project_id, **inputs)

        # Persist the primary draft artifact
        if result.draft_artifact:
            artifact_type = result.draft_artifact.__class__.__name__
            self.artifact_manager.save_artifact(
                result.draft_artifact, project_id, artifact_type
            )

        # Persist any extra artifacts in extra_data
        for key, val in result.extra_data.items():
            if hasattr(val, "__class__"):
                self.artifact_manager.save_artifact(
                    val, project_id, val.__class__.__name__
                )

        return result

