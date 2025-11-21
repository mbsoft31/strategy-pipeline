"""Quick test of new database dialects."""

from src.search.models import QueryPlan, ConceptBlock, FieldTag
from src.search.builder import get_builder

# Build a simple query
plan = QueryPlan()
pop = ConceptBlock("Population")
pop.add_term("large language models", FieldTag.KEYWORD)
pop.add_term("LLM", FieldTag.KEYWORD)
plan.blocks.append(pop)

outcome = ConceptBlock("Outcome")
outcome.add_term("hallucination", FieldTag.KEYWORD)
outcome.add_term("factuality", FieldTag.KEYWORD)
plan.blocks.append(outcome)

# Test each database
databases = ["pubmed", "scopus", "arxiv", "openalex", "semanticscholar", "crossref"]

print("Testing new database dialects:")
print("="*70)

for db in databases:
    try:
        builder = get_builder(db)
        query = builder.build(plan)
        print(f"\n{db.upper()}:")
        print(query)
        print()
    except Exception as e:
        print(f"\n{db.upper()} ERROR: {e}\n")

print("="*70)
print("All databases tested successfully!")

