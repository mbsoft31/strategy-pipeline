"""
Simple example demonstrating SLR integration capabilities.

This script shows how to:
1. Execute searches across multiple databases
2. Deduplicate results
3. Export to different formats
"""
from src.services.search_service import get_search_service
from pathlib import Path


def main():
    print("="*70)
    print("SLR INTEGRATION EXAMPLE")
    print("="*70)

    # Get the search service
    service = get_search_service()

    # 1. Execute a simple search
    print("\n1. EXECUTING SEARCH ON OPENALEX")
    print("-" * 70)

    query = "machine learning in healthcare"
    print(f"Query: {query}")
    print(f"Database: OpenAlex")
    print(f"Max results: 10")
    print()

    result = service.execute_search(
        database='openalex',
        query=query,
        max_results=10
    )

    if result.error:
        print(f"❌ Search failed: {result.error}")
        return

    print(f"✅ Search completed successfully!")
    print(f"   Total hits: {result.total_hits}")
    print(f"   Execution time: {result.execution_time:.2f}s")
    print(f"   Results file: {result.result_file}")

    # 2. Load and display results
    print("\n2. LOADING AND DISPLAYING RESULTS")
    print("-" * 70)

    documents = service.load_results(result.result_file)
    print(f"Loaded {len(documents)} documents\n")

    for i, doc in enumerate(documents[:3], 1):  # Show first 3
        print(f"Document {i}:")
        print(f"  Title: {doc['title'][:70]}...")
        print(f"  Year: {doc.get('year', 'N/A')}")

        authors = doc.get('authors', [])
        if authors:
            author_names = [f"{a.get('given_name', '')} {a['family_name']}".strip()
                          for a in authors[:3]]
            print(f"  Authors: {', '.join(author_names)}")
            if len(authors) > 3:
                print(f"           ... and {len(authors) - 3} more")

        print(f"  Citations: {doc.get('cited_by_count', 0)}")
        print(f"  DOI: {doc.get('doi', 'N/A')}")
        print()

    if len(documents) > 3:
        print(f"... and {len(documents) - 3} more documents")

    # 3. Search another database
    print("\n3. SEARCHING ARXIV")
    print("-" * 70)

    print(f"Query: {query}")
    print(f"Database: arXiv")
    print(f"Max results: 5")
    print()

    result2 = service.execute_search(
        database='arxiv',
        query=query,
        max_results=5
    )

    if result2.error:
        print(f"❌ arXiv search failed: {result2.error}")
    else:
        print(f"✅ arXiv search completed!")
        print(f"   Total hits: {result2.total_hits}")
        print(f"   Execution time: {result2.execution_time:.2f}s")

    # 4. Deduplicate results
    print("\n4. DEDUPLICATION")
    print("-" * 70)

    result_files = [result.result_file]
    if not result2.error and result2.result_file:
        result_files.append(result2.result_file)

    print(f"Deduplicating {len(result_files)} result sets...")

    total_before = sum(len(service.load_results(f)) for f in result_files)
    unique_docs = service.deduplicate_results(result_files)

    print(f"  Before deduplication: {total_before} documents")
    print(f"  After deduplication: {len(unique_docs)} documents")
    print(f"  Duplicates removed: {total_before - len(unique_docs)}")

    # 5. Export results
    print("\n5. EXPORTING RESULTS")
    print("-" * 70)

    # Create exports directory
    export_dir = Path("data/exports")
    export_dir.mkdir(parents=True, exist_ok=True)

    # Export to CSV
    csv_file = export_dir / "ml_healthcare_results.csv"
    service.export_results(unique_docs, format='csv', output_path=str(csv_file))
    print(f"✅ CSV export: {csv_file}")

    # Export to BibTeX
    bib_file = export_dir / "ml_healthcare_results.bib"
    service.export_results(unique_docs, format='bibtex', output_path=str(bib_file))
    print(f"✅ BibTeX export: {bib_file}")

    # Export to JSONL
    jsonl_file = export_dir / "ml_healthcare_results.jsonl"
    service.export_results(unique_docs, format='jsonl', output_path=str(jsonl_file))
    print(f"✅ JSONL export: {jsonl_file}")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✅ Searched {len(result_files)} database(s)")
    print(f"✅ Found {total_before} total documents")
    print(f"✅ Deduplicated to {len(unique_docs)} unique documents")
    print(f"✅ Exported to 3 formats (CSV, BibTeX, JSONL)")
    print(f"✅ All files saved to {export_dir}/")
    print()
    print("🎉 Example completed successfully!")
    print()
    print("Next steps:")
    print("  - Open the CSV file in Excel to view results")
    print("  - Import the BibTeX file into your reference manager")
    print("  - Process the JSONL file with custom scripts")
    print()


if __name__ == '__main__':
    main()

