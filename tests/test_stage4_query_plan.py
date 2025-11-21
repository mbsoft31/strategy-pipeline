"""Tests for Stage 4: DatabaseQueryPlan."""
import pytest
from src.controller import PipelineController
from src.services import FilePersistenceService, SimpleModelService
from src.models import (
    ProjectContext, ProblemFraming, ConceptModel,
    ResearchQuestionSet, SearchConceptBlocks, DatabaseQueryPlan,
    ApprovalStatus
)

RAW_IDEA = "Exploring validation techniques for reducing AI hallucinations in medical diagnosis systems."

@pytest.fixture
def controller():
    return PipelineController(
        model_service=SimpleModelService(),
        persistence_service=FilePersistenceService(base_dir="./data")
    )


def test_database_query_plan_happy_path(controller):
    """Test full pipeline through Stage 4."""
    # Run Stages 0-3
    stage0 = controller.start_project(raw_idea=RAW_IDEA)
    ctx: ProjectContext = stage0.draft_artifact
    controller.approve_artifact(ctx.id, "ProjectContext", ProjectContext, edits={})

    stage1 = controller.run_stage("problem-framing", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "ProblemFraming", ProblemFraming, edits={})
    controller.approve_artifact(ctx.id, "ConceptModel", ConceptModel, edits={})

    stage2 = controller.run_stage("research-questions", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "ResearchQuestionSet", ResearchQuestionSet, edits={})

    stage3 = controller.run_stage("search-concept-expansion", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "SearchConceptBlocks", SearchConceptBlocks, edits={})

    # Run Stage 4
    stage4 = controller.run_stage("database-query-plan", project_id=ctx.id)
    plan: DatabaseQueryPlan = stage4.draft_artifact

    assert plan is not None
    assert len(plan.queries) >= 1
    assert all(q.boolean_query_string for q in plan.queries)
    assert all(q.database_name for q in plan.queries)


def test_database_filtering(controller):
    """Test specifying subset of databases."""
    # Run Stages 0-3
    stage0 = controller.start_project(raw_idea=RAW_IDEA)
    ctx: ProjectContext = stage0.draft_artifact
    controller.approve_artifact(ctx.id, "ProjectContext", ProjectContext, edits={})

    stage1 = controller.run_stage("problem-framing", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "ProblemFraming", ProblemFraming, edits={})
    controller.approve_artifact(ctx.id, "ConceptModel", ConceptModel, edits={})

    stage2 = controller.run_stage("research-questions", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "ResearchQuestionSet", ResearchQuestionSet, edits={})

    stage3 = controller.run_stage("search-concept-expansion", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "SearchConceptBlocks", SearchConceptBlocks, edits={})

    # Run Stage 4 with specific databases
    stage4 = controller.run_stage(
        "database-query-plan",
        project_id=ctx.id,
        target_databases=["openalex", "pubmed"]
    )
    plan: DatabaseQueryPlan = stage4.draft_artifact

    assert plan is not None
    assert len(plan.queries) == 2
    db_names = [q.database_name for q in plan.queries]
    assert "openalex" in db_names
    assert "pubmed" in db_names


def test_query_syntax_validation(controller):
    """Test generated queries don't contain hallucinated operators."""
    # Run Stages 0-3
    stage0 = controller.start_project(raw_idea=RAW_IDEA)
    ctx: ProjectContext = stage0.draft_artifact
    controller.approve_artifact(ctx.id, "ProjectContext", ProjectContext, edits={})

    stage1 = controller.run_stage("problem-framing", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "ProblemFraming", ProblemFraming, edits={})
    controller.approve_artifact(ctx.id, "ConceptModel", ConceptModel, edits={})

    stage2 = controller.run_stage("research-questions", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "ResearchQuestionSet", ResearchQuestionSet, edits={})

    stage3 = controller.run_stage("search-concept-expansion", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "SearchConceptBlocks", SearchConceptBlocks, edits={})

    # Run Stage 4
    stage4 = controller.run_stage("database-query-plan", project_id=ctx.id)
    plan: DatabaseQueryPlan = stage4.draft_artifact

    # Check for Anti-Hallucination: no invalid operators
    for query in plan.queries:
        q_upper = query.boolean_query_string.upper()
        assert "NEAR" not in q_upper, f"Hallucinated NEAR operator in {query.database_name}"
        assert "ADJ" not in q_upper, f"Hallucinated ADJ operator in {query.database_name}"
        assert "PROX" not in q_upper, f"Hallucinated PROX operator in {query.database_name}"

        # Should contain valid Boolean operators
        assert any(op in q_upper for op in ["AND", "OR", "(", ")"]), \
            f"Query should contain Boolean operators: {query.boolean_query_string}"


def test_requires_prior_artifacts(controller):
    """Test that Stage 4 requires approved prior stages."""
    with pytest.raises(ValueError):
        controller.run_stage("database-query-plan", project_id="nonexistent")


def test_excluded_terms_handled(controller):
    """Test that excluded terms are properly handled with NOT operator."""
    # Run Stages 0-3
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

    # Manually add excluded term to first block
    if blocks.blocks:
        blocks.blocks[0].terms_excluded = ["animal models", "in vitro"]
        controller.persistence_service.save_artifact(blocks, ctx.id, "SearchConceptBlocks")

    controller.approve_artifact(ctx.id, "SearchConceptBlocks", SearchConceptBlocks, edits={})

    # Run Stage 4
    stage4 = controller.run_stage("database-query-plan", project_id=ctx.id)
    plan: DatabaseQueryPlan = stage4.draft_artifact

    # At least one query should contain NOT (if exclusions were processed)
    has_not = any("NOT" in q.boolean_query_string.upper() for q in plan.queries)
    if blocks.blocks and blocks.blocks[0].terms_excluded:
        assert has_not, "Queries should contain NOT operator when exclusions present"


def test_empty_blocks_validation(controller):
    """Test that Stage 4 fails gracefully when SearchConceptBlocks is empty."""
    # Run Stages 0-3
    stage0 = controller.start_project(raw_idea=RAW_IDEA)
    ctx: ProjectContext = stage0.draft_artifact
    controller.approve_artifact(ctx.id, "ProjectContext", ProjectContext, edits={})

    stage1 = controller.run_stage("problem-framing", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "ProblemFraming", ProblemFraming, edits={})
    controller.approve_artifact(ctx.id, "ConceptModel", ConceptModel, edits={})

    stage2 = controller.run_stage("research-questions", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "ResearchQuestionSet", ResearchQuestionSet, edits={})

    # Create empty SearchConceptBlocks
    from src.models import SearchConceptBlocks
    empty_blocks = SearchConceptBlocks(project_id=ctx.id, blocks=[])
    controller.persistence_service.save_artifact(empty_blocks, ctx.id, "SearchConceptBlocks")
    controller.approve_artifact(ctx.id, "SearchConceptBlocks", SearchConceptBlocks, edits={})

    # Run Stage 4 - should fail validation
    stage4 = controller.run_stage("database-query-plan", project_id=ctx.id)

    assert stage4.draft_artifact is None
    assert len(stage4.validation_errors) > 0
    assert any("empty" in err.lower() for err in stage4.validation_errors)


def test_complexity_analysis_present(controller):
    """Test that complexity analysis is calculated for each query."""
    # Run Stages 0-3
    stage0 = controller.start_project(raw_idea=RAW_IDEA)
    ctx: ProjectContext = stage0.draft_artifact
    controller.approve_artifact(ctx.id, "ProjectContext", ProjectContext, edits={})

    stage1 = controller.run_stage("problem-framing", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "ProblemFraming", ProblemFraming, edits={})
    controller.approve_artifact(ctx.id, "ConceptModel", ConceptModel, edits={})

    stage2 = controller.run_stage("research-questions", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "ResearchQuestionSet", ResearchQuestionSet, edits={})

    stage3 = controller.run_stage("search-concept-expansion", project_id=ctx.id)
    controller.approve_artifact(ctx.id, "SearchConceptBlocks", SearchConceptBlocks, edits={})

    # Run Stage 4
    stage4 = controller.run_stage("database-query-plan", project_id=ctx.id)
    plan: DatabaseQueryPlan = stage4.draft_artifact

    assert plan is not None
    # Every query should have complexity analysis
    for query in plan.queries:
        assert query.complexity_analysis is not None
        assert "complexity_level" in query.complexity_analysis
        assert "guidance" in query.complexity_analysis
        assert "expected_results" in query.complexity_analysis
        assert "total_terms" in query.complexity_analysis


