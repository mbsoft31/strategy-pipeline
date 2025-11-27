"""Tests for ProjectNavigator class."""

import unittest
from unittest.mock import Mock, MagicMock
from datetime import datetime, UTC

from src.orchestration.project_navigator import ProjectNavigator
from src.models import (
    ApprovalStatus,
    ProjectContext,
    ProblemFraming,
    ResearchQuestionSet,
    SearchConceptBlocks,
    DatabaseQueryPlan,
    ScreeningCriteria,
    StrategyExportBundle,
)


class TestProjectNavigator(unittest.TestCase):
    """Test suite for ProjectNavigator."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_artifact_manager = Mock()
        self.navigator = ProjectNavigator(self.mock_artifact_manager)
        self.project_id = "test_project_123"

    def test_initialization(self):
        """Test ProjectNavigator initializes correctly."""
        self.assertIsNotNone(self.navigator.artifact_manager)
        self.assertEqual(
            self.navigator.artifact_manager, self.mock_artifact_manager
        )

    def test_get_next_available_stages_no_context(self):
        """When no ProjectContext exists, should return project-setup."""
        self.mock_artifact_manager.get_artifact.return_value = None

        result = self.navigator.get_next_available_stages(self.project_id)

        self.assertEqual(result, ["project-setup"])
        self.mock_artifact_manager.get_artifact.assert_called_once_with(
            self.project_id, "ProjectContext", ProjectContext
        )

    def test_get_next_available_stages_context_not_approved(self):
        """When ProjectContext is not approved, should return project-setup."""
        mock_context = Mock(spec=ProjectContext)
        mock_context.status = ApprovalStatus.DRAFT
        self.mock_artifact_manager.get_artifact.return_value = mock_context

        result = self.navigator.get_next_available_stages(self.project_id)

        self.assertEqual(result, ["project-setup"])

    def test_get_next_available_stages_context_approved_no_framing(self):
        """When ProjectContext approved but no ProblemFraming, return problem-framing."""
        def get_artifact_side_effect(proj_id, artifact_type, artifact_class):
            if artifact_class == ProjectContext:
                mock_ctx = Mock(spec=ProjectContext)
                mock_ctx.status = ApprovalStatus.APPROVED
                return mock_ctx
            return None

        self.mock_artifact_manager.get_artifact.side_effect = (
            get_artifact_side_effect
        )

        result = self.navigator.get_next_available_stages(self.project_id)

        self.assertEqual(result, ["problem-framing"])

    def test_get_next_available_stages_framing_approved_no_rq(self):
        """When ProblemFraming approved but no ResearchQuestionSet, return research-questions."""
        def get_artifact_side_effect(proj_id, artifact_type, artifact_class):
            if artifact_class == ProjectContext:
                mock_ctx = Mock(spec=ProjectContext)
                mock_ctx.status = ApprovalStatus.APPROVED
                return mock_ctx
            elif artifact_class == ProblemFraming:
                mock_framing = Mock(spec=ProblemFraming)
                mock_framing.status = ApprovalStatus.APPROVED
                return mock_framing
            return None

        self.mock_artifact_manager.get_artifact.side_effect = (
            get_artifact_side_effect
        )

        result = self.navigator.get_next_available_stages(self.project_id)

        self.assertEqual(result, ["research-questions"])

    def test_get_next_available_stages_all_approved_to_search_expansion(self):
        """Test progression to search-concept-expansion."""
        def get_artifact_side_effect(proj_id, artifact_type, artifact_class):
            if artifact_class in [
                ProjectContext,
                ProblemFraming,
                ResearchQuestionSet,
            ]:
                mock_artifact = Mock()
                mock_artifact.status = ApprovalStatus.APPROVED
                return mock_artifact
            return None

        self.mock_artifact_manager.get_artifact.side_effect = (
            get_artifact_side_effect
        )

        result = self.navigator.get_next_available_stages(self.project_id)

        self.assertEqual(result, ["search-concept-expansion"])

    def test_get_next_available_stages_all_approved_to_query_plan(self):
        """Test progression to database-query-plan."""
        def get_artifact_side_effect(proj_id, artifact_type, artifact_class):
            if artifact_class in [
                ProjectContext,
                ProblemFraming,
                ResearchQuestionSet,
                SearchConceptBlocks,
            ]:
                mock_artifact = Mock()
                mock_artifact.status = ApprovalStatus.APPROVED_WITH_NOTES
                return mock_artifact
            return None

        self.mock_artifact_manager.get_artifact.side_effect = (
            get_artifact_side_effect
        )

        result = self.navigator.get_next_available_stages(self.project_id)

        self.assertEqual(result, ["database-query-plan"])

    def test_get_next_available_stages_all_approved_to_screening(self):
        """Test progression to screening-criteria."""
        def get_artifact_side_effect(proj_id, artifact_type, artifact_class):
            if artifact_class in [
                ProjectContext,
                ProblemFraming,
                ResearchQuestionSet,
                SearchConceptBlocks,
                DatabaseQueryPlan,
            ]:
                mock_artifact = Mock()
                mock_artifact.status = ApprovalStatus.APPROVED
                return mock_artifact
            return None

        self.mock_artifact_manager.get_artifact.side_effect = (
            get_artifact_side_effect
        )

        result = self.navigator.get_next_available_stages(self.project_id)

        self.assertEqual(result, ["screening-criteria"])

    def test_get_next_available_stages_all_approved_to_export(self):
        """Test progression to strategy-export."""
        def get_artifact_side_effect(proj_id, artifact_type, artifact_class):
            if artifact_class in [
                ProjectContext,
                ProblemFraming,
                ResearchQuestionSet,
                SearchConceptBlocks,
                DatabaseQueryPlan,
                ScreeningCriteria,
            ]:
                mock_artifact = Mock()
                mock_artifact.status = ApprovalStatus.APPROVED
                return mock_artifact
            return None

        self.mock_artifact_manager.get_artifact.side_effect = (
            get_artifact_side_effect
        )

        result = self.navigator.get_next_available_stages(self.project_id)

        self.assertEqual(result, ["strategy-export"])

    def test_get_next_available_stages_pipeline_complete(self):
        """When all stages approved, should return empty list."""
        def get_artifact_side_effect(proj_id, artifact_type, artifact_class):
            # All artifacts exist and are approved
            mock_artifact = Mock()
            mock_artifact.status = ApprovalStatus.APPROVED
            return mock_artifact

        self.mock_artifact_manager.get_artifact.side_effect = (
            get_artifact_side_effect
        )

        result = self.navigator.get_next_available_stages(self.project_id)

        self.assertEqual(result, [])

    def test_get_project_status_no_stages_complete(self):
        """Test project status when no stages are complete."""
        self.mock_artifact_manager.get_artifact.return_value = None

        status = self.navigator.get_project_status(self.project_id)

        self.assertEqual(status["project_id"], self.project_id)
        self.assertEqual(status["completed_stages"], [])
        self.assertEqual(status["current_stage"], "project-setup")
        self.assertEqual(status["total_stages"], 7)
        self.assertEqual(status["progress_percentage"], 0.0)
        self.assertFalse(status["is_complete"])

    def test_get_project_status_two_stages_complete(self):
        """Test project status with two stages complete."""
        def get_artifact_side_effect(proj_id, artifact_type, artifact_class):
            if artifact_class in [ProjectContext, ProblemFraming]:
                mock_artifact = Mock()
                mock_artifact.status = ApprovalStatus.APPROVED
                return mock_artifact
            return None

        self.mock_artifact_manager.get_artifact.side_effect = (
            get_artifact_side_effect
        )

        status = self.navigator.get_project_status(self.project_id)

        self.assertEqual(
            status["completed_stages"], ["project-setup", "problem-framing"]
        )
        self.assertEqual(status["current_stage"], "research-questions")
        self.assertEqual(status["progress_percentage"], 28.6)  # 2/7 * 100
        self.assertFalse(status["is_complete"])

    def test_get_project_status_all_stages_complete(self):
        """Test project status when pipeline is complete."""
        def get_artifact_side_effect(proj_id, artifact_type, artifact_class):
            mock_artifact = Mock()
            mock_artifact.status = ApprovalStatus.APPROVED
            return mock_artifact

        self.mock_artifact_manager.get_artifact.side_effect = (
            get_artifact_side_effect
        )

        status = self.navigator.get_project_status(self.project_id)

        self.assertEqual(len(status["completed_stages"]), 7)
        self.assertIsNone(status["current_stage"])
        self.assertEqual(status["progress_percentage"], 100.0)
        self.assertTrue(status["is_complete"])

    def test_validate_stage_transition_valid(self):
        """Test valid stage transition."""
        self.mock_artifact_manager.get_artifact.return_value = None

        result = self.navigator.validate_stage_transition(
            self.project_id, "project-setup"
        )

        self.assertTrue(result)

    def test_validate_stage_transition_invalid(self):
        """Test invalid stage transition."""
        self.mock_artifact_manager.get_artifact.return_value = None

        result = self.navigator.validate_stage_transition(
            self.project_id, "problem-framing"
        )

        self.assertFalse(result)

    def test_validate_stage_transition_valid_mid_pipeline(self):
        """Test valid transition in middle of pipeline."""
        def get_artifact_side_effect(proj_id, artifact_type, artifact_class):
            if artifact_class in [ProjectContext, ProblemFraming]:
                mock_artifact = Mock()
                mock_artifact.status = ApprovalStatus.APPROVED
                return mock_artifact
            return None

        self.mock_artifact_manager.get_artifact.side_effect = (
            get_artifact_side_effect
        )

        result = self.navigator.validate_stage_transition(
            self.project_id, "research-questions"
        )

        self.assertTrue(result)

    def test_approved_with_notes_counts_as_approved(self):
        """Test that APPROVED_WITH_NOTES status allows progression."""
        def get_artifact_side_effect(proj_id, artifact_type, artifact_class):
            if artifact_class == ProjectContext:
                mock_ctx = Mock(spec=ProjectContext)
                mock_ctx.status = ApprovalStatus.APPROVED_WITH_NOTES
                return mock_ctx
            return None

        self.mock_artifact_manager.get_artifact.side_effect = (
            get_artifact_side_effect
        )

        result = self.navigator.get_next_available_stages(self.project_id)

        self.assertEqual(result, ["problem-framing"])


if __name__ == "__main__":
    unittest.main()

