import json
import unittest
import tempfile
from pathlib import Path

from src.controller import PipelineController
from src.models import ProjectContext
from src.services import FilePersistenceService, SimpleModelService


class TestStage0ProjectSetup(unittest.TestCase):
    def test_start_project_creates_context_and_persists(self):
        idea = "Assessing the role of machine learning in climate risk forecasting"
        with tempfile.TemporaryDirectory() as tmp:
            store = FilePersistenceService(base_dir=tmp)
            controller = PipelineController(SimpleModelService(), store)

            result = controller.start_project(raw_idea=idea)
            ctx: ProjectContext = result.draft_artifact

            self.assertIsNotNone(ctx.id)
            self.assertTrue(ctx.title)
            self.assertIn("machine", " ".join(ctx.initial_keywords))

            # Persisted file should exist
            fpath = Path(tmp) / ctx.id / "ProjectContext.json"
            self.assertTrue(fpath.exists())

            # Approve with a small edit
            controller.approve_artifact(
                project_id=ctx.id,
                artifact_type="ProjectContext",
                artifact_class=ProjectContext,
                edits={"title": ctx.title + " (approved)"},
            )

            # Reload and verify
            loaded = controller.get_artifact(ctx.id, "ProjectContext", ProjectContext)
            self.assertTrue(loaded.title.endswith("(approved)"))


if __name__ == "__main__":
    unittest.main()

