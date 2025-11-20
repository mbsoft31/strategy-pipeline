"""Validation script for new database dialects."""
import sys

def validate_new_dialects():
    """Validate that all new dialects work correctly."""
    try:
        from src.search.models import QueryPlan, ConceptBlock, FieldTag
        from src.search.builder import get_builder

        # Create a test plan
        plan = QueryPlan()

        block1 = ConceptBlock("Concept1")
        block1.add_term("large language models", FieldTag.KEYWORD)
        block1.add_term("LLM", FieldTag.KEYWORD)
        plan.blocks.append(block1)

        block2 = ConceptBlock("Concept2")
        block2.add_term("hallucination", FieldTag.KEYWORD)
        block2.add_term("factuality", FieldTag.KEYWORD)
        plan.blocks.append(block2)

        databases = ["pubmed", "scopus", "arxiv", "openalex", "semanticscholar", "crossref"]

        results = {}
        errors = {}

        for db in databases:
            try:
                builder = get_builder(db)
                query = builder.build(plan)
                results[db] = query
            except Exception as e:
                errors[db] = str(e)

        # Write results to file
        with open("validation_results.txt", "w", encoding="utf-8") as f:
            f.write("="*70 + "\n")
            f.write("NEW DATABASE DIALECTS VALIDATION\n")
            f.write("="*70 + "\n\n")

            for db in databases:
                f.write(f"\n{'='*70}\n")
                f.write(f"{db.upper()} QUERY\n")
                f.write(f"{'='*70}\n")

                if db in results:
                    f.write(results[db] + "\n")
                else:
                    f.write(f"ERROR: {errors.get(db, 'Unknown error')}\n")

            f.write(f"\n{'='*70}\n")
            f.write(f"SUMMARY\n")
            f.write(f"{'='*70}\n")
            f.write(f"Successful: {len(results)}/{len(databases)}\n")
            if errors:
                f.write(f"Errors: {errors}\n")
            else:
                f.write("All dialects working correctly!\n")

        print("Validation complete! Results written to validation_results.txt")

        # Also print summary
        print(f"\nSuccessful: {len(results)}/{len(databases)}")
        if errors:
            print(f"Errors: {errors}")
            return 1
        else:
            print("All dialects working correctly!")
            return 0

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(validate_new_dialects())

