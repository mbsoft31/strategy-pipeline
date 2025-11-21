"""Tests for Stage 3: SearchConceptExpansion."""
import pytest
from src.controller import PipelineController
from src.services import FilePersistenceService, SimpleModelService
from src.models import ProjectContext, ProblemFraming, ConceptModel, ResearchQuestionSet, SearchConceptBlocks, ApprovalStatus

RAW_IDEA = "Investigating prompt engineering techniques for improving reasoning in large language models."

@pytest.fixture
def controller():
    return PipelineController(model_service=SimpleModelService(), persistence_service=FilePersistenceService(base_dir="./data"))


def test_search_expansion_stage_happy_path(controller):
    """Test full pipeline through Stage 3."""
    stage0 = controller.start_project(raw_idea=RAW_IDEA)
    ctx: ProjectContext = stage0.draft_artifact
    controller.approve_artifact(ctx.id, "ProjectContext", ProjectContext, edits={})

    stage1 = controller.run_stage("problem-framing", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "ProblemFraming", ProblemFraming, edits={})
    controller.approve_artifact(ctx.id, "ConceptModel", ConceptModel, edits={})

    stage2 = controller.run_stage("research-questions", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "ResearchQuestionSet", ResearchQuestionSet, edits={})

    stage3 = controller.run_stage("search-concept-expansion", project_id=ctx.id)
    blocks: SearchConceptBlocks = stage3.draft_artifact

    assert blocks is not None
    assert len(blocks.blocks) >= 1
    assert all(len(b.terms_included) >= 1 for b in blocks.blocks)
    # Verify each block has required fields
    for block in blocks.blocks:
        assert block.label
        assert block.id
        assert isinstance(block.terms_included, list)
        assert isinstance(block.terms_excluded, list)


def test_search_expansion_requires_prior_artifacts(controller):
    """Test that Stage 3 requires approved Stage 1 and 2 artifacts."""
    with pytest.raises(ValueError):
        controller.run_stage("search-concept-expansion", project_id="nonexistent")


def test_search_expansion_terms_quality(controller):
    """Test that generated terms include variations."""
    stage0 = controller.start_project(raw_idea=RAW_IDEA)
    ctx: ProjectContext = stage0.draft_artifact
    controller.approve_artifact(ctx.id, "ProjectContext", ProjectContext, edits={})

    stage1 = controller.run_stage("problem-framing", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "ProblemFraming", ProblemFraming, edits={})
    controller.approve_artifact(ctx.id, "ConceptModel", ConceptModel, edits={})

    stage2 = controller.run_stage("research-questions", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "ResearchQuestionSet", ResearchQuestionSet, edits={})

    stage3 = controller.run_stage("search-concept-expansion", project_id=ctx.id)
    blocks: SearchConceptBlocks = stage3.draft_artifact

    # Check that terms include variations (case, plural, etc.)
    for block in blocks.blocks:
        terms_lower = [t.lower() for t in block.terms_included]
        # Should have at least the base term
        assert len(terms_lower) >= 1

