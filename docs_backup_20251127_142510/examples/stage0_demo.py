"""Example: programmatic usage of Stage 0 (Project Setup).
Run with: python -m docs.examples.stage0_demo
"""
from src.controller import PipelineController
from src.models import ProjectContext
from src.services import FilePersistenceService, SimpleModelService


def main() -> None:
    controller = PipelineController(SimpleModelService(), FilePersistenceService("./data"))
    res = controller.start_project(
        raw_idea="Investigating social robots in elder care: impacts on loneliness and care workflows"
    )
    ctx: ProjectContext = res.draft_artifact
    print("Project:", ctx.id)
    print("Title:", ctx.title)
    print("Keywords:", ctx.initial_keywords)


if __name__ == "__main__":
    main()

