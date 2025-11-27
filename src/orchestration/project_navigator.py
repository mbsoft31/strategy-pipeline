"""Project navigation and stage progression logic.

This module handles determining which stages are available to run next based on
the current state of project artifacts and their approval status.
"""

from typing import Any, Dict, List, TYPE_CHECKING

from ..models import (
    ApprovalStatus,
    ProjectContext,
    ProblemFraming,
    ResearchQuestionSet,
    SearchConceptBlocks,
    DatabaseQueryPlan,
    ScreeningCriteria,
    StrategyExportBundle,
)

if TYPE_CHECKING:
    from .artifact_manager import ArtifactManager


class ProjectNavigator:
    """Handles project status and stage progression logic.

    This class is responsible for:
    - Determining which stages can be executed next
    - Validating stage transitions
    - Providing project status information

    It uses the ArtifactManager to load artifacts and check their approval status.
    """

    def __init__(self, artifact_manager: "ArtifactManager"):
        """Initialize the ProjectNavigator.

        Args:
            artifact_manager: The ArtifactManager instance for loading artifacts.
        """
        self.artifact_manager = artifact_manager

    def get_next_available_stages(self, project_id: str) -> List[str]:
        """Determine next stages based on approved artifacts.

        This method checks which artifacts have been approved and determines
        which stage(s) should be executed next in the pipeline.

        The pipeline progression is linear:
        1. project-setup (creates ProjectContext)
        2. problem-framing (creates ProblemFraming & ConceptModel)
        3. research-questions (creates ResearchQuestionSet)
        4. search-concept-expansion (creates SearchConceptBlocks)
        5. database-query-plan (creates DatabaseQueryPlan)
        6. screening-criteria (creates ScreeningCriteria)
        7. strategy-export (creates StrategyExportBundle)

        Args:
            project_id: The ID of the project to check.

        Returns:
            List of stage names that can be executed. Typically one stage,
            but returns empty list if pipeline is complete.

        Example:
            >>> navigator = ProjectNavigator(artifact_manager)
            >>> navigator.get_next_available_stages("project_123")
            ['problem-framing']
        """
        # Check ProjectContext
        context = self.artifact_manager.get_artifact(
            project_id, "ProjectContext", ProjectContext
        )
        if context is None or context.status not in (
            ApprovalStatus.APPROVED,
            ApprovalStatus.APPROVED_WITH_NOTES,
        ):
            return ["project-setup"]

        # Check ProblemFraming
        framing = self.artifact_manager.get_artifact(
            project_id, "ProblemFraming", ProblemFraming
        )
        if framing is None or framing.status not in (
            ApprovalStatus.APPROVED,
            ApprovalStatus.APPROVED_WITH_NOTES,
        ):
            return ["problem-framing"]

        # Check ResearchQuestionSet
        rq_set = self.artifact_manager.get_artifact(
            project_id, "ResearchQuestionSet", ResearchQuestionSet
        )
        if rq_set is None or rq_set.status not in (
            ApprovalStatus.APPROVED,
            ApprovalStatus.APPROVED_WITH_NOTES,
        ):
            return ["research-questions"]

        # Check SearchConceptBlocks
        search_blocks = self.artifact_manager.get_artifact(
            project_id, "SearchConceptBlocks", SearchConceptBlocks
        )
        if search_blocks is None or search_blocks.status not in (
            ApprovalStatus.APPROVED,
            ApprovalStatus.APPROVED_WITH_NOTES,
        ):
            return ["search-concept-expansion"]

        # Check DatabaseQueryPlan
        query_plan = self.artifact_manager.get_artifact(
            project_id, "DatabaseQueryPlan", DatabaseQueryPlan
        )
        if query_plan is None or query_plan.status not in (
            ApprovalStatus.APPROVED,
            ApprovalStatus.APPROVED_WITH_NOTES,
        ):
            return ["database-query-plan"]

        # Check ScreeningCriteria
        screening_criteria = self.artifact_manager.get_artifact(
            project_id, "ScreeningCriteria", ScreeningCriteria
        )
        if screening_criteria is None or screening_criteria.status not in (
            ApprovalStatus.APPROVED,
            ApprovalStatus.APPROVED_WITH_NOTES,
        ):
            return ["screening-criteria"]

        # Check StrategyExportBundle
        export_bundle = self.artifact_manager.get_artifact(
            project_id, "StrategyExportBundle", StrategyExportBundle
        )
        if export_bundle is None or export_bundle.status not in (
            ApprovalStatus.APPROVED,
            ApprovalStatus.APPROVED_WITH_NOTES,
        ):
            return ["strategy-export"]

        # All stages complete
        return []

    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get current project status including completed stages.

        Args:
            project_id: The ID of the project to check.

        Returns:
            Dictionary containing project status information including:
            - completed_stages: List of stage names that are approved
            - current_stage: The next stage to execute (or None if complete)
            - total_stages: Total number of stages in pipeline
            - progress_percentage: Completion percentage
        """
        # Define all stages in order
        all_stages = [
            "project-setup",
            "problem-framing",
            "research-questions",
            "search-concept-expansion",
            "database-query-plan",
            "screening-criteria",
            "strategy-export",
        ]

        # Get next available stage
        next_stages = self.get_next_available_stages(project_id)
        current_stage = next_stages[0] if next_stages else None

        # Calculate completed stages
        if current_stage is None:
            completed_count = len(all_stages)
        elif current_stage in all_stages:
            completed_count = all_stages.index(current_stage)
        else:
            completed_count = 0

        completed_stages = all_stages[:completed_count]
        progress_percentage = (completed_count / len(all_stages)) * 100

        return {
            "project_id": project_id,
            "completed_stages": completed_stages,
            "current_stage": current_stage,
            "next_available_stages": next_stages,
            "total_stages": len(all_stages),
            "progress_percentage": round(progress_percentage, 1),
            "is_complete": current_stage is None,
        }

    def validate_stage_transition(
        self, project_id: str, target_stage: str
    ) -> bool:
        """Validate if a stage can be executed given current project state.

        Args:
            project_id: The ID of the project.
            target_stage: The stage name to validate.

        Returns:
            True if the stage can be executed, False otherwise.

        Example:
            >>> navigator.validate_stage_transition("project_123", "problem-framing")
            True
        """
        next_available = self.get_next_available_stages(project_id)
        return target_stage in next_available

