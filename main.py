"""HITL Research Strategy Pipeline - Entry Point

Small runnable demo for Stage 0 (Project Setup). This uses a simple local
model service and file-based persistence so you can test end-to-end without
external dependencies.
"""

from src.controller import PipelineController
from src.models import ProjectContext
from src.services import FilePersistenceService, SimpleModelService


def _demo() -> None:
    print("\n▶ Running Stage 0 demo (Project Setup)...\n")

    model = SimpleModelService()
    store = FilePersistenceService(base_dir="./data")
    controller = PipelineController(model_service=model, persistence_service=store)

    idea = (
        "Exploring how lightweight language models can support literature review "
        "workflows in healthcare informatics, focusing on query formulation and "
        "screening criteria design."
    )

    result = controller.start_project(raw_idea=idea)
    ctx: ProjectContext = result.draft_artifact

    print(f"Created project: {ctx.id}")
    print(f"Title: {ctx.title}")
    print(f"Keywords: {', '.join(ctx.initial_keywords) if ctx.initial_keywords else '-'}")
    print("\nPrompts for user review:")
    for p in result.prompts:
        print(f" - {p}")

    # Simulate an approval with a tiny edit
    controller.approve_artifact(
        project_id=ctx.id,
        artifact_type="ProjectContext",
        artifact_class=ProjectContext,
        edits={"title": ctx.title + " (pilot)"},
    )

    approved = controller.get_artifact(ctx.id, "ProjectContext", ProjectContext)
    print("\n✓ Saved and approved ProjectContext.")
    print(f"Updated title: {approved.title}")
    print("Data saved under ./data/", ctx.id)


if __name__ == "__main__":
    _demo()
