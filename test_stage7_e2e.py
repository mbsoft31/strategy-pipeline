"""End-to-end test for Stage 7: Query Execution.

This script tests the complete pipeline from Stage 0 to Stage 7.
"""
import sys
from pathlib import Path

def test_stage7_registration():
    """Verify Stage 7 is registered."""
    print("=" * 60)
    print("TEST 1: Stage 7 Registration")
    print("=" * 60)
    
    try:
        from src.controller import PipelineController
        from src.services.simple_model_service import SimpleModelService
        from src.services.persistence_service import FilePersistenceService
        
        controller = PipelineController(
            SimpleModelService(),
            FilePersistenceService(base_dir="./test_e2e_data")
        )
        
        stages = controller.stage_orchestrator.list_registered_stages()
        
        print(f"Total registered stages: {len(stages)}")
        print(f"Stages: {', '.join(stages)}")
        
        if "query-execution" in stages:
            print("\n✅ SUCCESS: Stage 7 (query-execution) is registered!")
            return True
        else:
            print("\n❌ FAIL: Stage 7 (query-execution) NOT registered")
            print(f"Available stages: {stages}")
            return False
            
    except Exception as e:
        print(f"\n❌ FAIL: Error checking registration: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stage7_execution():
    """Test running Stage 7 in a pipeline."""
    print("\n" + "=" * 60)
    print("TEST 2: Stage 7 Execution (Simplified)")
    print("=" * 60)
    
    try:
        from src.controller import PipelineController
        from src.services.simple_model_service import SimpleModelService
        from src.services.persistence_service import FilePersistenceService
        from src.models import SearchResults
        
        controller = PipelineController(
            SimpleModelService(),
            FilePersistenceService(base_dir="./test_e2e_data")
        )
        
        # Stage 0: Create project
        print("\n[Stage 0] Creating project...")
        ctx_result = controller.start_project(
            "Systematic review of transformer architecture innovations"
        )
        project_id = ctx_result.draft_artifact.id
        print(f"✓ Project created: {project_id}")
        controller.approve_artifact(project_id, "ProjectContext")
        
        # Stages 1-4: Run prerequisite stages
        prerequisite_stages = [
            "problem-framing",
            "research-questions",
            "search-concept-expansion",
            "database-query-plan"
        ]
        
        for i, stage_name in enumerate(prerequisite_stages, 1):
            print(f"\n[Stage {i}] Running {stage_name}...")
            
            try:
                result = controller.run_stage(stage_name, project_id=project_id)
                
                if result.validation_errors:
                    print(f"⚠ Stage {stage_name} has validation errors:")
                    for error in result.validation_errors[:3]:  # Show first 3
                        print(f"  - {error}")
                    print(f"⚠ Skipping remaining stages (SimpleModelService may not generate valid outputs)")
                    return False
                
                if result.draft_artifact:
                    print(f"✓ Stage {stage_name} completed")
                    controller.approve_artifact(project_id, result.draft_artifact.__class__.__name__)
                else:
                    print(f"⚠ Stage {stage_name} returned no artifact")
                    return False
                    
            except Exception as e:
                print(f"❌ Stage {stage_name} failed: {e}")
                return False
        
        # Stage 7: Query Execution
        print(f"\n[Stage 7] Running query-execution...")
        print("NOTE: This will attempt to fetch real papers from academic databases.")
        print("      It may take 10-30 seconds depending on network speed.")
        
        try:
            exec_result = controller.run_stage("query-execution", project_id=project_id)
            
            if exec_result.validation_errors:
                print(f"\n⚠ Query execution returned validation errors:")
                for error in exec_result.validation_errors:
                    print(f"  - {error}")
                
                # Check if this is total failure or partial success
                if exec_result.draft_artifact:
                    print("\n⚠ Partial success: Some databases failed, but some worked")
                else:
                    print("\n❌ Total failure: No databases executed successfully")
                    print("   This may be due to:")
                    print("   - Network connectivity issues")
                    print("   - API rate limits")
                    print("   - Invalid queries from Stage 4")
                    return False
            
            if exec_result.draft_artifact:
                search_results = exec_result.draft_artifact
                
                print(f"\n✅ SUCCESS: Query execution completed!")
                print(f"\nResults Summary:")
                print(f"  - Total papers retrieved: {search_results.total_results}")
                print(f"  - After deduplication: {search_results.deduplicated_count}")
                print(f"  - Databases searched: {', '.join(search_results.databases_searched)}")
                print(f"  - Execution time: {search_results.execution_time_seconds:.2f}s")
                print(f"  - Result files saved: {len(search_results.result_file_paths)}")
                
                # Show deduplication stats
                if search_results.deduplication_stats:
                    print(f"\nDeduplication Stats:")
                    for key, value in search_results.deduplication_stats.items():
                        print(f"  - {key}: {value}")
                
                # Verify files exist
                print(f"\nVerifying result files:")
                all_files_exist = True
                for file_path in search_results.result_file_paths:
                    path = Path(file_path)
                    if path.exists():
                        size_kb = path.stat().st_size / 1024
                        print(f"  ✓ {path.name} ({size_kb:.1f} KB)")
                    else:
                        print(f"  ❌ {path.name} (NOT FOUND)")
                        all_files_exist = False
                
                if all_files_exist:
                    print(f"\n✅ All result files verified!")
                else:
                    print(f"\n⚠ Some result files are missing")
                
                # Try to load papers from one file
                if search_results.result_file_paths:
                    print(f"\nLoading papers from first result file...")
                    try:
                        from src.services.search_service import SearchService
                        service = SearchService()
                        papers = service.load_results(search_results.result_file_paths[0])
                        
                        print(f"✓ Loaded {len(papers)} papers")
                        if papers:
                            print(f"\nFirst paper:")
                            print(f"  Title: {papers[0].get('title', 'N/A')[:80]}...")
                            print(f"  Year: {papers[0].get('year', 'N/A')}")
                            print(f"  DOI: {papers[0].get('doi', 'N/A')}")
                    except Exception as e:
                        print(f"⚠ Could not load papers: {e}")
                
                return True
            else:
                print(f"\n❌ Query execution returned no artifact")
                return False
                
        except Exception as e:
            print(f"\n❌ Query execution failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("STAGE 7: END-TO-END VERIFICATION")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Verify Stage 7 is registered")
    print("2. Run full pipeline (Stages 0-7)")
    print("3. Verify papers are retrieved and saved")
    print("\n" + "=" * 60)
    
    # Test 1: Registration
    registration_ok = test_stage7_registration()
    
    if not registration_ok:
        print("\n" + "=" * 60)
        print("❌ REGISTRATION FAILED - Cannot proceed with execution test")
        print("=" * 60)
        return 1
    
    # Test 2: Execution (only if registration passed)
    execution_ok = test_stage7_execution()
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Registration Test: {'✅ PASS' if registration_ok else '❌ FAIL'}")
    print(f"Execution Test: {'✅ PASS' if execution_ok else '❌ FAIL'}")
    print("=" * 60)
    
    if registration_ok and execution_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nStage 7 is fully operational. You can now:")
        print("  1. Run full pipeline (Stages 0-7)")
        print("  2. Retrieve real papers from academic databases")
        print("  3. Proceed to Stage 5 enhancement")
        return 0
    elif registration_ok:
        print("\n⚠️ REGISTRATION PASSED, EXECUTION FAILED")
        print("\nThis may be due to:")
        print("  - SimpleModelService not generating valid queries")
        print("  - Network connectivity issues")
        print("  - API rate limits")
        print("\nTry testing with real LLM (OpenAI/Anthropic) instead of SimpleModelService")
        return 1
    else:
        print("\n❌ CRITICAL: REGISTRATION FAILED")
        print("\nStage 7 is not properly registered. Check:")
        print("  - src/orchestration/stage_orchestrator.py")
        print("  - Verify 'query-execution' registration line exists")
        return 1


if __name__ == "__main__":
    sys.exit(main())

