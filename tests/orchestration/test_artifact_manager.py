"""Tests for ArtifactManager class."""

import unittest
from unittest.mock import Mock, MagicMock, call
from datetime import datetime, UTC

from src.orchestration.artifact_manager import ArtifactManager
from src.models import ApprovalStatus, ProjectContext


class TestArtifactManager(unittest.TestCase):
    """Test suite for ArtifactManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_persistence = Mock()
        self.manager = ArtifactManager(self.mock_persistence)
        self.project_id = "test_project_456"

    def test_initialization(self):
        """Test ArtifactManager initializes correctly."""
        self.assertIsNotNone(self.manager.persistence_service)
        self.assertEqual(self.manager.persistence_service, self.mock_persistence)

    def test_get_artifact_calls_persistence_service(self):
        """Test get_artifact delegates to persistence service."""
        mock_artifact = Mock(spec=ProjectContext)
        self.mock_persistence.load_artifact.return_value = mock_artifact

        result = self.manager.get_artifact(
            self.project_id, "ProjectContext", ProjectContext
        )

        self.assertEqual(result, mock_artifact)
        self.mock_persistence.load_artifact.assert_called_once_with(
            "ProjectContext", self.project_id, ProjectContext
        )

    def test_get_artifact_returns_none_when_not_found(self):
        """Test get_artifact returns None for missing artifacts."""
        self.mock_persistence.load_artifact.return_value = None

        result = self.manager.get_artifact(
            self.project_id, "ProjectContext", ProjectContext
        )

        self.assertIsNone(result)

    def test_save_artifact_calls_persistence_service(self):
        """Test save_artifact delegates to persistence service."""
        mock_artifact = Mock(spec=ProjectContext)

        self.manager.save_artifact(mock_artifact, self.project_id, "ProjectContext")

        self.mock_persistence.save_artifact.assert_called_once_with(
            mock_artifact, self.project_id, "ProjectContext"
        )

    def test_list_projects_calls_persistence_service(self):
        """Test list_projects delegates to persistence service."""
        expected_projects = ["proj1", "proj2", "proj3"]
        self.mock_persistence.list_projects.return_value = expected_projects

        result = self.manager.list_projects()

        self.assertEqual(result, expected_projects)
        self.mock_persistence.list_projects.assert_called_once()

    def test_project_exists_calls_persistence_service(self):
        """Test project_exists delegates to persistence service."""
        self.mock_persistence.project_exists.return_value = True

        result = self.manager.project_exists(self.project_id)

        self.assertTrue(result)
        self.mock_persistence.project_exists.assert_called_once_with(
            self.project_id
        )

    def test_project_exists_returns_false_when_not_exists(self):
        """Test project_exists returns False for non-existent project."""
        self.mock_persistence.project_exists.return_value = False

        result = self.manager.project_exists("nonexistent_project")

        self.assertFalse(result)

    def test_approve_artifact_loads_artifact(self):
        """Test approve_artifact loads the artifact first."""
        mock_artifact = Mock(spec=ProjectContext)
        mock_artifact.title = "Original Title"
        self.mock_persistence.load_artifact.return_value = mock_artifact

        self.manager.approve_artifact(
            self.project_id,
            "ProjectContext",
            ProjectContext,
            edits={},
        )

        self.mock_persistence.load_artifact.assert_called_once_with(
            "ProjectContext", self.project_id, ProjectContext
        )

    def test_approve_artifact_raises_error_if_not_found(self):
        """Test approve_artifact raises ValueError if artifact not found."""
        self.mock_persistence.load_artifact.return_value = None

        with self.assertRaises(ValueError) as cm:
            self.manager.approve_artifact(
                self.project_id,
                "ProjectContext",
                ProjectContext,
                edits={},
            )

        self.assertIn("not found", str(cm.exception))
        self.assertIn(self.project_id, str(cm.exception))

    def test_approve_artifact_applies_edits(self):
        """Test approve_artifact applies field edits correctly."""
        mock_artifact = Mock(spec=ProjectContext)
        mock_artifact.title = "Original Title"
        mock_artifact.description = "Original Description"
        self.mock_persistence.load_artifact.return_value = mock_artifact

        edits = {
            "title": "New Title",
            "description": "New Description",
        }

        self.manager.approve_artifact(
            self.project_id,
            "ProjectContext",
            ProjectContext,
            edits=edits,
        )

        self.assertEqual(mock_artifact.title, "New Title")
        self.assertEqual(mock_artifact.description, "New Description")

    def test_approve_artifact_ignores_nonexistent_fields(self):
        """Test approve_artifact ignores edits for fields that don't exist."""
        mock_artifact = Mock(spec=ProjectContext)
        mock_artifact.title = "Original Title"
        # Configure hasattr to return False for 'nonexistent_field'
        mock_artifact.__class__ = ProjectContext
        self.mock_persistence.load_artifact.return_value = mock_artifact

        edits = {
            "title": "New Title",
            "nonexistent_field": "Should be ignored",
        }

        # Should not raise an error
        self.manager.approve_artifact(
            self.project_id,
            "ProjectContext",
            ProjectContext,
            edits=edits,
        )

        self.assertEqual(mock_artifact.title, "New Title")

    def test_approve_artifact_sets_approval_status(self):
        """Test approve_artifact sets the approval status."""
        mock_artifact = Mock(spec=ProjectContext)
        self.mock_persistence.load_artifact.return_value = mock_artifact

        self.manager.approve_artifact(
            self.project_id,
            "ProjectContext",
            ProjectContext,
            edits={},
            approval_status=ApprovalStatus.APPROVED,
        )

        self.assertEqual(mock_artifact.status, ApprovalStatus.APPROVED)

    def test_approve_artifact_sets_approved_with_notes_status(self):
        """Test approve_artifact can set APPROVED_WITH_NOTES status."""
        mock_artifact = Mock(spec=ProjectContext)
        self.mock_persistence.load_artifact.return_value = mock_artifact

        self.manager.approve_artifact(
            self.project_id,
            "ProjectContext",
            ProjectContext,
            edits={},
            approval_status=ApprovalStatus.APPROVED_WITH_NOTES,
        )

        self.assertEqual(mock_artifact.status, ApprovalStatus.APPROVED_WITH_NOTES)

    def test_approve_artifact_updates_timestamp(self):
        """Test approve_artifact updates the updated_at timestamp."""
        mock_artifact = Mock(spec=ProjectContext)
        old_time = datetime(2024, 1, 1, tzinfo=UTC)
        mock_artifact.updated_at = old_time
        self.mock_persistence.load_artifact.return_value = mock_artifact

        before_approval = datetime.now(UTC)
        self.manager.approve_artifact(
            self.project_id,
            "ProjectContext",
            ProjectContext,
            edits={},
        )
        after_approval = datetime.now(UTC)

        # Check that updated_at was set to a recent time
        self.assertIsInstance(mock_artifact.updated_at, datetime)
        self.assertGreaterEqual(mock_artifact.updated_at, before_approval)
        self.assertLessEqual(mock_artifact.updated_at, after_approval)

    def test_approve_artifact_adds_user_notes(self):
        """Test approve_artifact adds user notes when provided."""
        mock_artifact = Mock(spec=ProjectContext)
        self.mock_persistence.load_artifact.return_value = mock_artifact

        user_notes = "This looks great!"
        self.manager.approve_artifact(
            self.project_id,
            "ProjectContext",
            ProjectContext,
            edits={},
            user_notes=user_notes,
        )

        self.assertEqual(mock_artifact.user_notes, user_notes)

    def test_approve_artifact_does_not_set_notes_if_not_provided(self):
        """Test approve_artifact doesn't modify notes if not provided."""
        mock_artifact = Mock(spec=ProjectContext)
        mock_artifact.user_notes = "Existing notes"
        self.mock_persistence.load_artifact.return_value = mock_artifact

        self.manager.approve_artifact(
            self.project_id,
            "ProjectContext",
            ProjectContext,
            edits={},
            user_notes=None,
        )

        # user_notes should not be modified
        self.assertEqual(mock_artifact.user_notes, "Existing notes")

    def test_approve_artifact_saves_artifact(self):
        """Test approve_artifact saves the artifact after modifications."""
        mock_artifact = Mock(spec=ProjectContext)
        self.mock_persistence.load_artifact.return_value = mock_artifact

        self.manager.approve_artifact(
            self.project_id,
            "ProjectContext",
            ProjectContext,
            edits={"title": "New Title"},
        )

        self.mock_persistence.save_artifact.assert_called_once_with(
            mock_artifact, self.project_id, "ProjectContext"
        )

    def test_approve_artifact_full_workflow(self):
        """Test complete approve_artifact workflow with all features."""
        mock_artifact = Mock(spec=ProjectContext)
        mock_artifact.title = "Original"
        mock_artifact.description = "Original Desc"
        self.mock_persistence.load_artifact.return_value = mock_artifact

        edits = {
            "title": "Updated Title",
            "description": "Updated Description",
        }
        user_notes = "Approved with minor changes"

        self.manager.approve_artifact(
            self.project_id,
            "ProjectContext",
            ProjectContext,
            edits=edits,
            approval_status=ApprovalStatus.APPROVED_WITH_NOTES,
            user_notes=user_notes,
        )

        # Verify all modifications
        self.assertEqual(mock_artifact.title, "Updated Title")
        self.assertEqual(mock_artifact.description, "Updated Description")
        self.assertEqual(mock_artifact.status, ApprovalStatus.APPROVED_WITH_NOTES)
        self.assertEqual(mock_artifact.user_notes, user_notes)
        self.assertIsInstance(mock_artifact.updated_at, datetime)

        # Verify save was called
        self.mock_persistence.save_artifact.assert_called_once()


if __name__ == "__main__":
    unittest.main()

