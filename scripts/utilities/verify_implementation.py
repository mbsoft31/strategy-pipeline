#!/usr/bin/env python
"""Final verification script - tests all 6 databases work correctly."""

def main():
    print("\n" + "="*70)
    print(" FINAL VERIFICATION: Testing All 6 Database Dialects")
    print("="*70 + "\n")

    try:
        # Import the necessary modules
        from src.search.models import QueryPlan, ConceptBlock, FieldTag
        from src.search.builder import get_builder

        # Create a test query
        plan = QueryPlan()

        block1 = ConceptBlock("Concept 1")
        block1.add_term("machine learning", FieldTag.KEYWORD)
        plan.blocks.append(block1)

        block2 = ConceptBlock("Concept 2")
        block2.add_term("healthcare", FieldTag.KEYWORD)
        plan.blocks.append(block2)

        # Test each database
        databases = ["pubmed", "scopus", "arxiv", "openalex", "semanticscholar", "crossref"]

        success_count = 0

        for db in databases:
            try:
                builder = get_builder(db)
                query = builder.build(plan)

                # Basic validation
                assert len(query) > 0, f"{db}: Empty query"
                assert "machine learning" in query or "machine learning" in query.lower(), f"{db}: Missing search term"

                print(f"✓ {db:20s} - OK")
                success_count += 1

            except Exception as e:
                print(f"✗ {db:20s} - FAILED: {e}")

        print("\n" + "="*70)
        print(f" Results: {success_count}/{len(databases)} databases working")
        print("="*70)

        if success_count == len(databases):
            print("\n SUCCESS! All database dialects are functional.\n")
            return 0
        else:
            print(f"\n PARTIAL SUCCESS: {len(databases) - success_count} database(s) failed.\n")
            return 1

    except Exception as e:
        print(f"\n FATAL ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    import sys
    sys.exit(main())

