"""Tests for StageOrchestrator class."""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import uuid
from datetime import datetime, UTC

from src.orchestration.stage_orchestrator import StageOrchestrator
from src.stages.base import StageResult, BaseStage
from src.models import ProjectContext, ApprovalStatus, ModelMetadata


class MockStage(BaseStage):
    """Mock stage for testing."""

    def execute(self, **kwargs):
        """Mock execute method."""
        return StageResult(
            stage_name="mock-stage",
            draft_artifact=Mock(),
            prompts=["Test prompt"],
            extra_data={},
        )


class TestStageOrchestrator(unittest.TestCase):
    """Test suite for StageOrchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model_service = Mock()
        self.mock_artifact_manager = Mock()
        self.mock_artifact_manager.persistence_service = Mock()

        self.orchestrator = StageOrchestrator(
            self.mock_model_service,
            self.mock_artifact_manager,
        )
        self.project_id = "test_project_789"

    def _create_mock_metadata(self):
        """Helper to create mock metadata."""
        return ModelMetadata(
            model_name="test-model",
            mode="test",
            prompt_version="1.0",
            generated_at=datetime.now(UTC),
            notes="Test execution",
        )

    def test_initialization(self):
        """Test StageOrchestrator initializes correctly."""
        self.assertIsNotNone(self.orchestrator.model_service)
        self.assertIsNotNone(self.orchestrator.artifact_manager)
        self.assertIsInstance(self.orchestrator._stages_registry, dict)
        # Should have registered default stages
        self.assertGreater(len(self.orchestrator._stages_registry), 0)

    def test_default_stages_registered(self):
        """Test that all default stages are registered."""
        expected_stages = [
            "project-setup",
            "problem-framing",
            "research-questions",
            "search-concept-expansion",
            "database-query-plan",
            "screening-criteria",
            "strategy-export",
        ]

        registered_stages = self.orchestrator.list_registered_stages()

        for stage in expected_stages:
            self.assertIn(stage, registered_stages)

    def test_register_stage(self):
        """Test registering a custom stage."""
        custom_stage_class = MockStage

        self.orchestrator.register_stage("custom-test-stage", custom_stage_class)

        self.assertIn("custom-test-stage", self.orchestrator._stages_registry)
        self.assertEqual(
            self.orchestrator._stages_registry["custom-test-stage"],
            custom_stage_class,
        )

    def test_get_stage_class_existing(self):
        """Test getting an existing stage class."""
        result = self.orchestrator.get_stage_class("project-setup")

        self.assertIsNotNone(result)

    def test_get_stage_class_nonexistent(self):
        """Test getting a non-existent stage class returns None."""
        result = self.orchestrator.get_stage_class("nonexistent-stage")

        self.assertIsNone(result)

    def test_list_registered_stages(self):
        """Test listing all registered stages."""
        stages = self.orchestrator.list_registered_stages()

        self.assertIsInstance(stages, list)
        self.assertGreater(len(stages), 0)
        self.assertIn("project-setup", stages)

    @patch("src.orchestration.stage_orchestrator.uuid.uuid4")
    def test_start_project_generates_id_if_not_provided(self, mock_uuid):
        """Test start_project generates a project ID if not provided."""
        mock_uuid.return_value = Mock(hex="abcdef1234567890")

        # Mock the stage execution
        mock_stage_instance = Mock(spec=BaseStage)
        mock_result = StageResult(
            stage_name="project-setup",
            draft_artifact=Mock(id="project_abcdef12"),
            metadata=self._create_mock_metadata(),
            prompts=[],
            extra_data={},
        )
        mock_stage_instance.execute.return_value = mock_result

        # Mock the stage class
        mock_stage_class = Mock(return_value=mock_stage_instance)
        self.orchestrator._stages_registry["project-setup"] = mock_stage_class

        result = self.orchestrator.start_project("Test idea")

        # Verify project ID was generated
        mock_stage_instance.execute.assert_called_once()
        call_kwargs = mock_stage_instance.execute.call_args[1]
        self.assertIn("project_id", call_kwargs)
        self.assertTrue(call_kwargs["project_id"].startswith("project_"))

    def test_start_project_uses_provided_id(self):
        """Test start_project uses provided project ID."""
        provided_id = "custom_project_id"

        # Mock the stage execution
        mock_stage_instance = Mock(spec=BaseStage)
        mock_result = StageResult(
            stage_name="project-setup",
            draft_artifact=Mock(id=provided_id),
            metadata=self._create_mock_metadata(),
            prompts=[],
            extra_data={},
        )
        mock_stage_instance.execute.return_value = mock_result

        # Mock the stage class
        mock_stage_class = Mock(return_value=mock_stage_instance)
        self.orchestrator._stages_registry["project-setup"] = mock_stage_class

        result = self.orchestrator.start_project("Test idea", project_id=provided_id)

        # Verify provided ID was used
        call_kwargs = mock_stage_instance.execute.call_args[1]
        self.assertEqual(call_kwargs["project_id"], provided_id)

    def test_start_project_saves_artifact(self):
        """Test start_project saves the draft artifact."""
        mock_artifact = Mock(spec=ProjectContext)
        mock_artifact.__class__.__name__ = "ProjectContext"

        # Mock the stage execution
        mock_stage_instance = Mock(spec=BaseStage)
        mock_result = StageResult(
            stage_name="project-setup",
            draft_artifact=mock_artifact,
            metadata=self._create_mock_metadata(),
            prompts=[],
            extra_data={},
        )
        mock_stage_instance.execute.return_value = mock_result

        # Mock the stage class
        mock_stage_class = Mock(return_value=mock_stage_instance)
        self.orchestrator._stages_registry["project-setup"] = mock_stage_class

        result = self.orchestrator.start_project("Test idea", project_id="proj_123")

        # Verify artifact was saved
        self.mock_artifact_manager.save_artifact.assert_called_once()

    def test_run_stage_raises_error_for_unregistered_stage(self):
        """Test run_stage raises ValueError for unregistered stage."""
        with self.assertRaises(ValueError) as cm:
            self.orchestrator.run_stage(
                "nonexistent-stage",
                self.project_id,
            )

        self.assertIn("not registered", str(cm.exception))
        self.assertIn("nonexistent-stage", str(cm.exception))

    def test_run_stage_raises_error_for_nonexistent_project(self):
        """Test run_stage raises ValueError if project doesn't exist."""
        self.mock_artifact_manager.project_exists.return_value = False

        with self.assertRaises(ValueError) as cm:
            self.orchestrator.run_stage(
                "problem-framing",
                self.project_id,
            )

        self.assertIn("does not exist", str(cm.exception))
        self.assertIn(self.project_id, str(cm.exception))

    def test_run_stage_executes_stage(self):
        """Test run_stage executes the stage."""
        self.mock_artifact_manager.project_exists.return_value = True

        # Mock the stage execution
        mock_stage_instance = Mock(spec=BaseStage)
        mock_artifact = Mock()
        mock_artifact.__class__.__name__ = "ProblemFraming"
        mock_result = StageResult(
            stage_name="problem-framing",
            draft_artifact=mock_artifact,
            metadata=self._create_mock_metadata(),
            prompts=[],
            extra_data={},
        )
        mock_stage_instance.execute.return_value = mock_result

        # Mock the stage class
        mock_stage_class = Mock(return_value=mock_stage_instance)
        self.orchestrator._stages_registry["problem-framing"] = mock_stage_class

        result = self.orchestrator.run_stage("problem-framing", self.project_id)

        # Verify stage was executed
        mock_stage_instance.execute.assert_called_once_with(
            project_id=self.project_id
        )
        self.assertEqual(result, mock_result)

    def test_run_stage_saves_draft_artifact(self):
        """Test run_stage saves the draft artifact."""
        self.mock_artifact_manager.project_exists.return_value = True

        mock_artifact = Mock()
        mock_artifact.__class__.__name__ = "ProblemFraming"

        # Mock the stage execution
        mock_stage_instance = Mock(spec=BaseStage)
        mock_result = StageResult(
            stage_name="problem-framing",
            draft_artifact=mock_artifact,
            metadata=self._create_mock_metadata(),
            prompts=[],
            extra_data={},
        )
        mock_stage_instance.execute.return_value = mock_result

        # Mock the stage class
        mock_stage_class = Mock(return_value=mock_stage_instance)
        self.orchestrator._stages_registry["problem-framing"] = mock_stage_class

        result = self.orchestrator.run_stage("problem-framing", self.project_id)

        # Verify artifact was saved
        self.mock_artifact_manager.save_artifact.assert_called()
        save_calls = self.mock_artifact_manager.save_artifact.call_args_list
        self.assertTrue(any(
            call[0][0] == mock_artifact
            for call in save_calls
        ))

    def test_run_stage_saves_extra_data_artifacts(self):
        """Test run_stage saves artifacts in extra_data."""
        self.mock_artifact_manager.project_exists.return_value = True

        mock_main_artifact = Mock()
        mock_main_artifact.__class__.__name__ = "ProblemFraming"

        mock_extra_artifact = Mock()
        mock_extra_artifact.__class__.__name__ = "ConceptModel"

        # Mock the stage execution
        mock_stage_instance = Mock(spec=BaseStage)
        mock_result = StageResult(
            stage_name="problem-framing",
            draft_artifact=mock_main_artifact,
            metadata=self._create_mock_metadata(),
            prompts=[],
            extra_data={"concept_model": mock_extra_artifact},
        )
        mock_stage_instance.execute.return_value = mock_result

        # Mock the stage class
        mock_stage_class = Mock(return_value=mock_stage_instance)
        self.orchestrator._stages_registry["problem-framing"] = mock_stage_class

        result = self.orchestrator.run_stage("problem-framing", self.project_id)

        # Verify both artifacts were saved
        self.assertEqual(self.mock_artifact_manager.save_artifact.call_count, 2)

    def test_run_stage_passes_extra_inputs(self):
        """Test run_stage passes extra keyword arguments to stage.execute()."""
        self.mock_artifact_manager.project_exists.return_value = True

        # Mock the stage execution
        mock_stage_instance = Mock(spec=BaseStage)
        mock_artifact = Mock()
        mock_artifact.__class__.__name__ = "TestArtifact"
        mock_result = StageResult(
            stage_name="test-stage",
            draft_artifact=mock_artifact,
            metadata=self._create_mock_metadata(),
            prompts=[],
            extra_data={},
        )
        mock_stage_instance.execute.return_value = mock_result

        # Mock the stage class
        mock_stage_class = Mock(return_value=mock_stage_instance)
        self.orchestrator.register_stage("test-stage", mock_stage_class)

        extra_param1 = "value1"
        extra_param2 = 42

        result = self.orchestrator.run_stage(
            "test-stage",
            self.project_id,
            custom_param=extra_param1,
            another_param=extra_param2,
        )

        # Verify extra parameters were passed
        mock_stage_instance.execute.assert_called_once()
        call_kwargs = mock_stage_instance.execute.call_args[1]
        self.assertEqual(call_kwargs["custom_param"], extra_param1)
        self.assertEqual(call_kwargs["another_param"], extra_param2)


if __name__ == "__main__":
    unittest.main()

