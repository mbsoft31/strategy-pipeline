"""Quick verification script for Stage 7 implementation.

Run this to verify Stage 7 is properly integrated.
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all new components can be imported."""
    print("Testing imports...")
    try:
        from src.stages.query_execution import QueryExecutionStage
        print("✅ QueryExecutionStage imported")
    except Exception as e:
        print(f"❌ Failed to import QueryExecutionStage: {e}")
        return False
    
    try:
        from src.models import SearchResults
        print("✅ SearchResults model imported")
    except Exception as e:
        print(f"❌ Failed to import SearchResults: {e}")
        return False
    
    try:
        from src.services.search_service import SearchService, SearchResultsSummary
        print("✅ SearchService imported")
    except Exception as e:
        print(f"❌ Failed to import SearchService: {e}")
        return False
    
    return True


def test_registration():
    """Test that Stage 7 is registered in the orchestrator."""
    print("\nTesting stage registration...")
    try:
        from src.controller import PipelineController
        from src.services.simple_model_service import SimpleModelService
        from src.services.persistence_service import FilePersistenceService
        
        controller = PipelineController(
            SimpleModelService(),
            FilePersistenceService(base_dir="./test_data")
        )
        
        stages = controller.stage_orchestrator.list_registered_stages()
        
        if "query-execution" in stages:
            print(f"✅ Stage 7 registered (total stages: {len(stages)})")
            print(f"   All stages: {', '.join(stages)}")
            return True
        else:
            print(f"❌ Stage 7 not found in registered stages")
            print(f"   Available: {', '.join(stages)}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to check registration: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_service():
    """Test SearchService project scoping."""
    print("\nTesting SearchService enhancements...")
    try:
        from src.services.search_service import SearchService
        
        # Test project-scoped initialization
        service = SearchService(base_dir="./test_data", project_id="test_project")
        
        expected_dir = Path("./test_data/test_project/search_results")
        actual_dir = service.results_dir
        
        if str(expected_dir) == str(actual_dir):
            print(f"✅ Project-scoped storage working: {actual_dir}")
        else:
            print(f"❌ Expected {expected_dir}, got {actual_dir}")
            return False
        
        # Test legacy mode (no project_id)
        service_legacy = SearchService(base_dir="./test_data")
        expected_legacy = Path("./test_data/search_results")
        
        if str(expected_legacy) == str(service_legacy.results_dir):
            print(f"✅ Backward compatibility maintained: {service_legacy.results_dir}")
        else:
            print(f"❌ Legacy mode broken: expected {expected_legacy}, got {service_legacy.results_dir}")
            return False
        
        # Check if save_deduplicated_results method exists
        if hasattr(service, 'save_deduplicated_results'):
            print("✅ save_deduplicated_results() method exists")
        else:
            print("❌ save_deduplicated_results() method missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ SearchService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_artifact_model():
    """Test SearchResults artifact structure."""
    print("\nTesting SearchResults artifact model...")
    try:
        from src.models import SearchResults, ModelMetadata, ApprovalStatus
        from datetime import datetime, UTC
        
        # Create test artifact
        artifact = SearchResults(
            project_id="test_123",
            total_results=100,
            deduplicated_count=85,
            databases_searched=["arxiv", "openalex"],
            result_file_paths=["data/test/results1.json", "data/test/results2.json"],
            deduplication_stats={"duplicates_removed": 15},
            execution_time_seconds=12.5,
            model_metadata=ModelMetadata(model_name="SearchService", mode="execution", generated_at=datetime.now(UTC))
        )
        
        # Verify attributes
        assert artifact.project_id == "test_123"
        assert artifact.total_results == 100
        assert artifact.deduplicated_count == 85
        assert len(artifact.databases_searched) == 2
        assert len(artifact.result_file_paths) == 2
        assert artifact.deduplication_stats["duplicates_removed"] == 15
        assert artifact.execution_time_seconds == 12.5
        assert hasattr(artifact, 'created_at')
        assert hasattr(artifact, 'status')
        
        print("✅ SearchResults artifact structure validated")
        print(f"   - project_id: {artifact.project_id}")
        print(f"   - total_results: {artifact.total_results}")
        print(f"   - deduplicated_count: {artifact.deduplicated_count}")
        print(f"   - databases: {artifact.databases_searched}")
        
        return True
        
    except Exception as e:
        print(f"❌ SearchResults artifact test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Stage 7: Query Execution - Verification Script")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Registration", test_registration),
        ("SearchService", test_search_service),
        ("Artifact Model", test_artifact_model),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Stage 7 implementation verified!")
        print("\nNext steps:")
        print("1. Run pytest tests: pytest tests/test_stage7_query_execution.py -v")
        print("2. Test with real pipeline execution")
        print("3. Proceed to Stage 5 enhancement")
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
        print("\nPlease fix issues before proceeding.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

