"""Full Pipeline Demo (Stages 0-4 with LLM-enabled service).

Flow:
1. Stage 0: Project Setup (ProjectContext)
2. Approve context
3. Stage 1: Problem Framing (ProblemFraming + ConceptModel)
4. Approve framing & concept model
5. Stage 2: Research Questions (ResearchQuestionSet)
6. Approve research questions
7. Stage 3: Search Concept Expansion (SearchConceptBlocks)
8. Approve search blocks
9. Stage 4: Database Query Plan (DatabaseQueryPlan)
10. Display summaries of each artifact

Assumes .env configured with LLM provider (mock or openai via OpenRouter).
"""
import logging
from src.controller import PipelineController
from src.services import FilePersistenceService, IntelligentModelService
from src.models import ProjectContext, ProblemFraming, ConceptModel, ResearchQuestionSet, SearchConceptBlocks, DatabaseQueryPlan, ApprovalStatus

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

RAW_IDEA = (
    "Investigating techniques to reduce hallucinations in large language models used for clinical decision support, "
    "focusing on uncertainty estimation, retrieval augmentation, and validation workflows in healthcare informatics."
)

def approve(controller: PipelineController, project_id: str, artifact_type: str, artifact_class, edits=None):
    edits = edits or {}
    controller.approve_artifact(
        project_id=project_id,
        artifact_type=artifact_type,
        artifact_class=artifact_class,
        edits=edits,
        approval_status=ApprovalStatus.APPROVED
    )


def run_demo():
    print("\n=== FULL PIPELINE DEMO (Stages 0-3) ===\n")
    model_service = IntelligentModelService()
    persistence = FilePersistenceService(base_dir="./data")
    controller = PipelineController(model_service=model_service, persistence_service=persistence)

    # Stage 0
    print("[Stage 0] Generating ProjectContext...")
    stage0 = controller.start_project(raw_idea=RAW_IDEA)
    ctx: ProjectContext = stage0.draft_artifact
    print(f"Project ID: {ctx.id}")
    print(f"Title: {ctx.title}")
    print(f"Keywords: {ctx.initial_keywords}\n")
    approve(controller, ctx.id, "ProjectContext", ProjectContext)

    # Stage 1
    print("[Stage 1] Generating ProblemFraming & ConceptModel...")
    stage1 = controller.run_stage("problem-framing", project_id=ctx.id)
    framing: ProblemFraming = stage1.draft_artifact
    concept_model: ConceptModel = stage1.extra_data.get("concept_model")
    if framing is None:
        print("Stage 1 failed:", stage1.validation_errors)
        return
    print("Problem Statement:\n", framing.problem_statement)
    print("Research Gap:\n", framing.research_gap)
    print("Goals:", framing.goals)
    print("Concepts:", [c.label for c in concept_model.concepts])
    approve(controller, ctx.id, "ProblemFraming", ProblemFraming)
    approve(controller, ctx.id, "ConceptModel", ConceptModel)

    # Stage 2
    print("[Stage 2] Generating ResearchQuestionSet...")
    stage2 = controller.run_stage("research-questions", project_id=ctx.id)
    rq_set: ResearchQuestionSet = stage2.draft_artifact
    if rq_set is None:
        print("Stage 2 failed:", stage2.validation_errors)
        return
    print(f"Generated {len(rq_set.questions)} research questions:")
    for q in rq_set.questions:
        print(f" - ({q.priority}) [{q.type}] {q.text}")
    approve(controller, ctx.id, "ResearchQuestionSet", ResearchQuestionSet)

    # Stage 3
    print("\n[Stage 3] Generating SearchConceptBlocks...")
    stage3 = controller.run_stage("search-concept-expansion", project_id=ctx.id)
    blocks: SearchConceptBlocks = stage3.draft_artifact
    if blocks is None:
        print("Stage 3 failed:", stage3.validation_errors)
        return
    print(f"Generated {len(blocks.blocks)} search concept blocks:")
    for block in blocks.blocks:
        print(f" - {block.label}: {len(block.terms_included)} terms included")
        print(f"   Terms: {', '.join(block.terms_included[:5])}")
        if block.terms_excluded:
            print(f"   Excluded: {', '.join(block.terms_excluded)}")
    approve(controller, ctx.id, "SearchConceptBlocks", SearchConceptBlocks)

    # Stage 4
    print("\n[Stage 4] Generating DatabaseQueryPlan...")
    stage4 = controller.run_stage(
        "database-query-plan",
        project_id=ctx.id,
        target_databases=["openalex", "arxiv", "pubmed", "scopus"],
        estimate_hits=False  # Set to True to estimate hit counts (slower)
    )
    plan: DatabaseQueryPlan = stage4.draft_artifact
    if plan is None:
        print("Stage 4 failed:", stage4.validation_errors)
        return

    print(f"Generated {len(plan.queries)} database queries:")
    for query in plan.queries:
        print(f"\n{query.database_name.upper()}:")
        # Display query with line breaks for readability
        query_lines = query.boolean_query_string.split('\n')
        if len(query_lines) > 1:
            print(f"  Query (multi-line):")
            for line in query_lines:
                print(f"    {line}")
        else:
            # Single line query
            if len(query.boolean_query_string) > 100:
                print(f"  Query: {query.boolean_query_string[:100]}...")
            else:
                print(f"  Query: {query.boolean_query_string}")

        # Display complexity analysis
        if query.complexity_analysis:
            ca = query.complexity_analysis
            print(f"  Complexity: {ca['complexity_level']} ({ca['total_terms']} terms, {ca['num_blocks']} blocks)")
            print(f"  Expected Results: {ca['expected_results']}")
            print(f"  Guidance: {ca['guidance']}")
            if ca.get('warnings'):
                for warning in ca['warnings']:
                    print(f"  ⚠️  {warning}")

        if query.hit_count_estimate:
            print(f"  Est. hits: ~{query.hit_count_estimate:,}")
        if query.notes:
            print(f"  Notes: {query.notes}")

    approve(controller, ctx.id, "DatabaseQueryPlan", DatabaseQueryPlan)

    print("\nPipeline progression now returns:")
    print(controller.get_next_available_stages(ctx.id))

    print("\nArtifacts saved under ./data/{project_id}/")
    print("Done.\n")

if __name__ == "__main__":
    run_demo()

