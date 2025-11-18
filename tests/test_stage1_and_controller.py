import json
import tempfile
import unittest
from pathlib import Path

from src.controller import PipelineController
from src.models import ProjectContext, ProblemFraming, ConceptModel, ApprovalStatus
from src.services import FilePersistenceService, SimpleModelService


class TestStage1ProblemFraming(unittest.TestCase):
    def test_problem_framing_stage_creates_artifacts(self):
        """Stage 1 should create both ProblemFraming and ConceptModel."""
        with tempfile.TemporaryDirectory() as tmp:
            store = FilePersistenceService(base_dir=tmp)
            controller = PipelineController(SimpleModelService(), store)

            # First create a project (Stage 0)
            idea = "Investigating the impact of AI on healthcare diagnostics"
            result0 = controller.start_project(raw_idea=idea)
            project_id = result0.draft_artifact.id

            # Approve the ProjectContext
            controller.approve_artifact(
                project_id=project_id,
                artifact_type="ProjectContext",
                artifact_class=ProjectContext,
                edits={},
            )

            # Now run Stage 1
            result1 = controller.run_stage("problem-framing", project_id)

            # Verify ProblemFraming was created
            self.assertIsNotNone(result1.draft_artifact)
            self.assertIsInstance(result1.draft_artifact, ProblemFraming)
            self.assertEqual(result1.draft_artifact.project_id, project_id)
            self.assertTrue(result1.draft_artifact.problem_statement)
            self.assertTrue(result1.draft_artifact.goals)

            # Verify ConceptModel in extra_data
            self.assertIn("concept_model", result1.extra_data)
            concept_model = result1.extra_data["concept_model"]
            self.assertIsInstance(concept_model, ConceptModel)
            self.assertEqual(concept_model.project_id, project_id)

            # Verify both artifacts were persisted
            framing_path = Path(tmp) / project_id / "ProblemFraming.json"
            concept_path = Path(tmp) / project_id / "ConceptModel.json"
            self.assertTrue(framing_path.exists())
            self.assertTrue(concept_path.exists())


class TestControllerApprovalFlow(unittest.TestCase):
    def test_approve_artifact_applies_edits_and_sets_status(self):
        """Approving should apply edits, set status, and update timestamp."""
        with tempfile.TemporaryDirectory() as tmp:
            store = FilePersistenceService(base_dir=tmp)
            controller = PipelineController(SimpleModelService(), store)

            # Create a project
            result = controller.start_project(raw_idea="Test idea for approval flow")
            project_id = result.draft_artifact.id
            original_title = result.draft_artifact.title

            # Approve with edits
            new_title = "Edited Title for Testing"
            controller.approve_artifact(
                project_id=project_id,
                artifact_type="ProjectContext",
                artifact_class=ProjectContext,
                edits={"title": new_title},
                approval_status=ApprovalStatus.APPROVED,
                user_notes="Approved after review",
            )

            # Reload and verify
            ctx = controller.get_artifact(project_id, "ProjectContext", ProjectContext)
            self.assertEqual(ctx.title, new_title)
            self.assertEqual(ctx.status, ApprovalStatus.APPROVED)
            self.assertEqual(ctx.user_notes, "Approved after review")
            self.assertIsNotNone(ctx.updated_at)

    def test_approve_nonexistent_artifact_raises_error(self):
        """Approving a missing artifact should raise ValueError."""
        with tempfile.TemporaryDirectory() as tmp:
            store = FilePersistenceService(base_dir=tmp)
            controller = PipelineController(SimpleModelService(), store)

            # Create empty project dir
            project_id = "fake_project_123"
            (Path(tmp) / project_id).mkdir()

            with self.assertRaises(ValueError) as cm:
                controller.approve_artifact(
                    project_id=project_id,
                    artifact_type="ProjectContext",
                    artifact_class=ProjectContext,
                    edits={},
                )
            self.assertIn("not found", str(cm.exception))


class TestPersistenceEdgeCases(unittest.TestCase):
    def test_list_projects_includes_created_projects(self):
        """Creating a project should make it appear in list_projects."""
        with tempfile.TemporaryDirectory() as tmp:
            store = FilePersistenceService(base_dir=tmp)
            controller = PipelineController(SimpleModelService(), store)

            # Initially empty
            self.assertEqual(controller.list_projects(), [])

            # Create two projects
            result1 = controller.start_project(raw_idea="Project 1")
            result2 = controller.start_project(raw_idea="Project 2")

            projects = controller.list_projects()
            self.assertEqual(len(projects), 2)
            self.assertIn(result1.draft_artifact.id, projects)
            self.assertIn(result2.draft_artifact.id, projects)

    def test_load_missing_artifact_returns_none(self):
        """Loading a non-existent artifact should return None."""
        with tempfile.TemporaryDirectory() as tmp:
            store = FilePersistenceService(base_dir=tmp)

            artifact = store.load_artifact("ProjectContext", "missing_project", ProjectContext)
            self.assertIsNone(artifact)

    def test_datetime_serialization_survives_save_load(self):
        """Datetimes should serialize as ISO strings and reload without crash."""
        with tempfile.TemporaryDirectory() as tmp:
            store = FilePersistenceService(base_dir=tmp)
            controller = PipelineController(SimpleModelService(), store)

            # Create and save
            result = controller.start_project(raw_idea="Datetime test")
            project_id = result.draft_artifact.id

            # Reload
            ctx = controller.get_artifact(project_id, "ProjectContext", ProjectContext)

            # Check that created_at and updated_at exist and are strings (ISO format)
            artifact_path = Path(tmp) / project_id / "ProjectContext.json"
            with open(artifact_path, "r") as f:
                data = json.load(f)

            self.assertIn("created_at", data)
            self.assertIn("updated_at", data)
            # They should be ISO strings
            self.assertIsInstance(data["created_at"], str)
            self.assertIsInstance(data["updated_at"], str)


if __name__ == "__main__":
    unittest.main()

