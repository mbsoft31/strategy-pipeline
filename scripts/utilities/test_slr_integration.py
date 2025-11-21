"""
Test script for SLR integration - Phase 1 verification.

This script verifies that:
1. SLR providers are correctly imported
2. Search service can be instantiated
3. Basic search execution works
"""
import logging
from src.services.search_service import SearchService, get_search_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_initialization():
    """Test that search service initializes correctly."""
    print("\n" + "="*60)
    print("TEST 1: SearchService Initialization")
    print("="*60)

    try:
        service = SearchService()
        print(f"✅ SearchService initialized successfully")
        print(f"   Results directory: {service.results_dir}")
        print(f"   Available databases: {service.get_available_databases()}")
        print(f"   Syntax-only databases: {list(service.get_syntax_only_databases().keys())}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize SearchService: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_singleton():
    """Test singleton pattern."""
    print("\n" + "="*60)
    print("TEST 2: Singleton Pattern")
    print("="*60)

    try:
        service1 = get_search_service()
        service2 = get_search_service()

        if service1 is service2:
            print(f"✅ Singleton pattern works correctly")
            return True
        else:
            print(f"❌ Singleton pattern failed - got different instances")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_provider_instantiation():
    """Test that providers can be instantiated."""
    print("\n" + "="*60)
    print("TEST 3: Provider Instantiation")
    print("="*60)

    service = get_search_service()
    databases = ['openalex', 'arxiv', 'crossref', 'semanticscholar']

    all_ok = True
    for db in databases:
        try:
            provider = service._get_provider(db)
            print(f"✅ {db}: {type(provider).__name__} created successfully")
        except Exception as e:
            print(f"❌ {db}: Failed to create provider - {e}")
            all_ok = False

    return all_ok


def test_simple_search():
    """Test a simple search on OpenAlex (most reliable)."""
    print("\n" + "="*60)
    print("TEST 4: Simple Search (OpenAlex)")
    print("="*60)

    service = get_search_service()

    try:
        # Use a simple query that should return results quickly
        query = "machine learning"
        print(f"   Executing search: '{query}' on OpenAlex...")
        print(f"   (Limited to 5 results for speed)")

        result = service.execute_search(
            database='openalex',
            query=query,
            max_results=5,
            save_to_disk=True
        )

        if result.error:
            print(f"❌ Search failed: {result.error}")
            return False

        print(f"✅ Search completed successfully!")
        print(f"   Database: {result.database}")
        print(f"   Query: {result.query}")
        print(f"   Total hits: {result.total_hits}")
        print(f"   Execution time: {result.execution_time:.2f}s")
        print(f"   Results saved to: {result.result_file}")

        # Try loading the results
        if result.result_file:
            docs = service.load_results(result.result_file)
            print(f"\n   Loaded {len(docs)} documents from file")
            if docs:
                first_doc = docs[0]
                print(f"   First result:")
                print(f"      Title: {first_doc['title'][:80]}...")
                print(f"      Year: {first_doc.get('year', 'N/A')}")
                print(f"      Authors: {len(first_doc.get('authors', []))} author(s)")

        return True

    except Exception as e:
        print(f"❌ Search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("SLR INTEGRATION - PHASE 1 VERIFICATION")
    print("="*60)

    tests = [
        ("Initialization", test_initialization),
        ("Singleton", test_singleton),
        ("Provider Instantiation", test_provider_instantiation),
        ("Simple Search", test_simple_search),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results[name] = False

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! SLR integration Phase 1 is working!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review.")


if __name__ == '__main__':
    main()

