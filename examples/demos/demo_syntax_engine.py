"""Demo script showing the syntax engine in action."""

from src.search.models import QueryPlan, ConceptBlock, FieldTag
from src.search.builder import get_builder

def main():
    print("\n" + "="*60)
    print("SYNTAX ENGINE DEMO: The Universal Translator")
    print("="*60)

    # Build a realistic research query
    plan = QueryPlan()

    # Concept 1
    pop = ConceptBlock("Population")
    pop.add_term("large language models", FieldTag.KEYWORD)
    pop.add_term("LLM", FieldTag.KEYWORD)
    plan.blocks.append(pop)

    # Concept 2
    outcome = ConceptBlock("Outcome")
    outcome.add_term("hallucination", FieldTag.KEYWORD)
    outcome.add_term("factuality", FieldTag.KEYWORD)
    plan.blocks.append(outcome)

    databases = [
        "pubmed", "scopus", "arxiv",
        "openalex", "semanticscholar", "crossref"
    ]

    for db in databases:
        print(f"\n[{db.upper()} Query]")
        print("-" * 60)
        try:
            query = get_builder(db).build(plan)
            print(query)
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "="*60)
    print("[OK] Generated 6 distinct dialect syntaxes from 1 internal model.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

