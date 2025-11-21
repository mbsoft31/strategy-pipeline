import pytest
from src.controller import PipelineController
from src.services import FilePersistenceService, SimpleModelService
from src.models import ProjectContext, ProblemFraming, ResearchQuestionSet, ApprovalStatus

RAW_IDEA = "Exploring dataset curation practices for training domain-adapted language models in clinical decision support."

@pytest.fixture
def controller():
    return PipelineController(model_service=SimpleModelService(), persistence_service=FilePersistenceService(base_dir="./data"))


def test_research_question_stage_happy_path(controller):
    stage0 = controller.start_project(raw_idea=RAW_IDEA)
    ctx: ProjectContext = stage0.draft_artifact
    controller.approve_artifact(ctx.id, "ProjectContext", ProjectContext, edits={})

    stage1 = controller.run_stage("problem-framing", project_id=ctx.id)
    framing: ProblemFraming = stage1.draft_artifact
    concept_model = stage1.extra_data.get("concept_model")
    controller.approve_artifact(ctx.id, "ProblemFraming", ProblemFraming, edits={})
    controller.approve_artifact(ctx.id, "ConceptModel", type(concept_model), edits={})

    stage2 = controller.run_stage("research-questions", project_id=ctx.id)
    rq_set: ResearchQuestionSet = stage2.draft_artifact
    assert rq_set is not None
    assert len(rq_set.questions) >= 3


def test_research_question_stage_requires_prior_artifacts(controller):
    # Attempt stage 2 without prior artifacts
    with pytest.raises(ValueError):
        controller.run_stage("research-questions", project_id="nonexistent")

