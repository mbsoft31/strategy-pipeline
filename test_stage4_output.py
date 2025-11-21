"""Test Stage 4 output for revision."""
import logging
from src.controller import PipelineController
from src.services import FilePersistenceService, IntelligentModelService
from src.models import DatabaseQueryPlan

logging.basicConfig(level=logging.WARNING)

controller = PipelineController(
    model_service=IntelligentModelService(), 
    persistence_service=FilePersistenceService(base_dir='./data')
)

print("\n=== TESTING STAGE 4 OUTPUT ===\n")

result = controller.run_stage(
    'database-query-plan', 
    project_id='project_f9eafccf',
    target_databases=['openalex', 'arxiv', 'pubmed', 'scopus'],
    estimate_hits=False
)

plan: DatabaseQueryPlan = result.draft_artifact

if plan:
    print(f"Generated {len(plan.queries)} database queries\n")
    for q in plan.queries:
        print(f"\n{'='*60}")
        print(f"DATABASE: {q.database_name.upper()}")
        print(f"{'='*60}")
        print(f"Query:")
        # Handle multi-line queries
        lines = q.boolean_query_string.split('\n')
        for line in lines:
            print(f"  {line}")
        if q.notes:
            print(f"\nNotes: {q.notes}")
        if q.hit_count_estimate:
            print(f"Est. Hits: {q.hit_count_estimate:,}")
        print()
else:
    print("Failed to generate queries:")
    print(result.validation_errors)

print("\n=== END ===\n")

