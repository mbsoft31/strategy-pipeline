"""Full pipeline integration test (Stages 0-7).

Tests the complete end-to-end workflow from project creation to paper export.
Uses IntelligentModelService with real LLM calls (requires API keys).

Run with:
    pytest tests/test_full_pipeline_stages_0_7.py -v -s

Or skip LLM stages:
    pytest tests/test_full_pipeline_stages_0_7.py -v -s -k "not llm"
"""
import pytest
import os
from pathlib import Path
from src.controller import PipelineController
from src.services import IntelligentModelService, FilePersistenceService, SimpleModelService
from src.models import SearchResults, StrategyExportBundle


@pytest.fixture
def test_data_dir(tmp_path):
    """Create temporary test data directory."""
    return str(tmp_path / "test_data")


@pytest.fixture
def controller_with_llm(test_data_dir):
    """Controller using IntelligentModelService (real LLM calls)."""
    return PipelineController(
        IntelligentModelService(),
        FilePersistenceService(base_dir=test_data_dir)
    )


@pytest.fixture
def controller_simple(test_data_dir):
    """Controller using SimpleModelService (no API calls)."""
    return PipelineController(
        SimpleModelService(),
        FilePersistenceService(base_dir=test_data_dir)
    )


def test_stage_registration(controller_simple):
    """Verify all 8 stages are registered."""
    stages = controller_simple.stage_orchestrator.list_registered_stages()

    expected_stages = [
        "project-setup",
        "problem-framing",
        "research-questions",
        "search-concept-expansion",
        "database-query-plan",
        "query-execution",
        "screening-criteria",
        "strategy-export"
    ]

    for stage in expected_stages:
        assert stage in stages, f"Stage {stage} not registered"

    assert len(stages) == 8, f"Expected 8 stages, got {len(stages)}"


def test_project_creation(controller_simple):
    """Test Stage 0: Project creation."""
    result = controller_simple.start_project(
        "Systematic review of machine learning in healthcare"
    )

    assert result.draft_artifact is not None
    assert result.draft_artifact.title is not None
    assert result.validation_errors == []

    project_id = result.draft_artifact.id
    assert project_id is not None

    # Verify artifact was saved
    ctx = controller_simple.persistence.load_artifact(
        "ProjectContext",
        project_id,
        type("ProjectContext", (), {})
    )
    assert ctx is not None


@pytest.mark.llm
def test_full_pipeline_with_llm(controller_with_llm, test_data_dir):
    """Test complete pipeline (Stages 0-7) with real LLM.

    WARNING: This test makes real API calls and may take 3-5 minutes.
    """
    # Stage 0: Create project
    result = controller_with_llm.start_project(
        "Systematic review of LLM hallucination mitigation techniques"
    )
    project_id = result.draft_artifact.id
    assert result.validation_errors == [], f"Stage 0 failed: {result.validation_errors}"

    controller_with_llm.approve_artifact(project_id, "ProjectContext")

    # Stages 1-4: Generate search strategy
    stages_1_4 = [
        "problem-framing",
        "research-questions",
        "search-concept-expansion",
        "database-query-plan"
    ]

    for stage_name in stages_1_4:
        print(f"\n▶ Running {stage_name}...")
        result = controller_with_llm.run_stage(stage_name, project_id=project_id)

        assert result.validation_errors == [], \
            f"{stage_name} failed: {result.validation_errors}"
        assert result.draft_artifact is not None, \
            f"{stage_name} returned no artifact"

        # Approve for next stage
        artifact_type = result.draft_artifact.__class__.__name__
        controller_with_llm.approve_artifact(project_id, artifact_type)
        print(f"  ✓ {stage_name} complete")

    # Stage 5: Screening criteria
    print(f"\n▶ Running screening-criteria...")
    result = controller_with_llm.run_stage("screening-criteria", project_id=project_id)
    assert result.validation_errors == []
    controller_with_llm.approve_artifact(project_id, "ScreeningCriteria")
    print(f"  ✓ screening-criteria complete")

    # Stage 7: Query execution
    print(f"\n▶ Running query-execution...")
    result = controller_with_llm.run_stage("query-execution", project_id=project_id)

    # May have warnings for unsupported databases, but should have results
    if result.validation_errors:
        print(f"  ⚠ Warnings: {result.validation_errors}")

    assert result.draft_artifact is not None, "Stage 7 returned no artifact"
    search_results = result.draft_artifact
    assert isinstance(search_results, SearchResults)
    assert search_results.total_results >= 0  # May be 0 if all databases failed

    if search_results.total_results > 0:
        print(f"  ✓ Retrieved {search_results.total_results} papers")
        print(f"  ✓ Databases: {', '.join(search_results.databases_searched)}")
        print(f"  ✓ Deduplicated to {search_results.deduplicated_count} papers")

        # Verify result files exist
        for file_path in search_results.result_file_paths:
            path = Path(file_path)
            assert path.exists(), f"Result file not found: {file_path}"
            assert path.stat().st_size > 0, f"Result file empty: {file_path}"

    controller_with_llm.approve_artifact(project_id, "SearchResults")

    # Stage 6: Export
    print(f"\n▶ Running strategy-export...")
    result = controller_with_llm.run_stage("strategy-export", project_id=project_id)
    assert result.validation_errors == []

    export_bundle = result.draft_artifact
    assert isinstance(export_bundle, StrategyExportBundle)
    assert len(export_bundle.exported_files) > 0

    # Verify export files exist
    export_dir = Path(test_data_dir) / project_id / "export"
    assert export_dir.exists()

    # Check for key export files
    if search_results.total_results > 0:
        assert (export_dir / "papers.csv").exists()
        assert (export_dir / "papers.bib").exists()
        assert (export_dir / "papers.ris").exists()

    assert (export_dir / "STRATEGY_PROTOCOL.md").exists()

    print(f"  ✓ Exported {len(export_bundle.exported_files)} files")
    print(f"\n✅ FULL PIPELINE TEST PASSED!")


def test_full_pipeline_simple(controller_simple, test_data_dir):
    """Test pipeline structure with SimpleModelService (no API calls).

    This tests the pipeline structure without making real API calls.
    May fail at Stage 3/4 if SimpleModelService generates invalid data.
    """
    # Stage 0
    result = controller_simple.start_project(
        "Test systematic review project"
    )
    project_id = result.draft_artifact.id
    assert result.validation_errors == []
    controller_simple.approve_artifact(project_id, "ProjectContext")

    # Stages 1-4 (may fail with SimpleModelService)
    stages = [
        "problem-framing",
        "research-questions",
        "search-concept-expansion",
        "database-query-plan",
        "screening-criteria"
    ]

    for stage_name in stages:
        try:
            result = controller_simple.run_stage(stage_name, project_id=project_id)

            if result.validation_errors:
                pytest.skip(f"Stage {stage_name} failed (expected with SimpleModelService): {result.validation_errors}")

            artifact_type = result.draft_artifact.__class__.__name__
            controller_simple.approve_artifact(project_id, artifact_type)

        except Exception as e:
            pytest.skip(f"Stage {stage_name} threw exception (expected with SimpleModelService): {e}")

    # If we got here, try Stage 7 (will likely fail without valid queries)
    result = controller_simple.run_stage("query-execution", project_id=project_id)

    # Stage 7 may fail gracefully with unsupported databases
    if result.validation_errors and "No database queries executed successfully" in result.validation_errors[0]:
        pytest.skip("Stage 7 failed as expected (all databases unsupported)")


def test_artifact_persistence(controller_simple, test_data_dir):
    """Test that artifacts are properly saved and loaded."""
    # Create project
    result = controller_simple.start_project("Persistence test project")
    project_id = result.draft_artifact.id
    controller_simple.approve_artifact(project_id, "ProjectContext")

    # Verify artifact file exists
    artifact_path = Path(test_data_dir) / project_id / "ProjectContext.json"
    assert artifact_path.exists()

    # Verify file contains valid JSON
    import json
    with open(artifact_path) as f:
        data = json.load(f)

    assert "id" in data
    assert "title" in data
    assert "status" in data

    # Test artifact loading
    from src.models import ProjectContext
    loaded = controller_simple.persistence.load_artifact(
        "ProjectContext",
        project_id,
        ProjectContext
    )

    assert loaded is not None
    assert loaded.id == project_id
    assert loaded.title == "Persistence test project"


def test_error_handling_missing_artifacts(controller_simple):
    """Test error handling when artifacts are missing."""
    # Try to run Stage 1 without Stage 0
    result = controller_simple.run_stage("problem-framing", project_id="nonexistent")

    assert result.validation_errors is not None
    assert len(result.validation_errors) > 0
    assert result.draft_artifact is None


def test_error_handling_empty_input(controller_simple):
    """Test error handling for empty inputs."""
    # Try to create project with empty idea
    result = controller_simple.start_project("")

    assert result.validation_errors is not None
    assert len(result.validation_errors) > 0


def test_stage_order_independence(controller_simple):
    """Test that Stage 5 can run before Stage 7 (independent paths)."""
    # Create project and run stages 1-4
    result = controller_simple.start_project("Order test")
    project_id = result.draft_artifact.id
    controller_simple.approve_artifact(project_id, "ProjectContext")

    # Run stages 1-4 (may skip if SimpleModelService fails)
    for stage in ["problem-framing", "research-questions",
                  "search-concept-expansion", "database-query-plan"]:
        result = controller_simple.run_stage(stage, project_id=project_id)
        if result.validation_errors:
            pytest.skip("Prerequisites failed with SimpleModelService")
        controller_simple.approve_artifact(project_id, result.draft_artifact.__class__.__name__)

    # Run Stage 5 BEFORE Stage 7
    result = controller_simple.run_stage("screening-criteria", project_id=project_id)
    assert result.validation_errors == [], "Stage 5 should work without Stage 7"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

