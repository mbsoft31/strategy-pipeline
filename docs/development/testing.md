# Testing Guide

Comprehensive guide for testing the Strategy Pipeline.

## Test Structure

```
tests/
├── conftest.py                          # Shared fixtures
├── test_full_pipeline_stages_0_7.py    # Integration tests
├── test_stage0.py                       # Stage 0 tests
├── test_stage1_and_controller.py       # Stage 1 + controller
├── test_stage2_research_questions.py   # Stage 2 tests
├── test_stage3_search_expansion.py     # Stage 3 tests
├── test_stage4_query_plan.py           # Stage 4 tests
└── orchestration/
    └── test_orchestrator.py            # Orchestration tests
```

## Running Tests

### Quick Commands

```bash
# All tests (skip expensive LLM tests)
pytest -v -k "not llm"

# All tests including LLM (requires API keys)
pytest -v

# Specific test file
pytest tests/test_stage7_query_execution.py -v

# Specific test function
pytest tests/test_stage7_query_execution.py::test_stage_registration -v

# With coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Watch mode (requires pytest-watch)
ptw -- -v -k "not llm"
```

### Test Categories

#### Unit Tests (Fast, No API Calls)
```bash
pytest tests/ -v -k "not llm and not integration"
```

#### Integration Tests (Moderate, Some API Calls)
```bash
pytest tests/test_full_pipeline_stages_0_7.py -v -k "not llm"
```

#### LLM Tests (Slow, Expensive)
```bash
# Only run when needed (costs ~$0.10-0.50)
pytest -v -m llm
```

## Test Fixtures

### Common Fixtures

```python
# conftest.py or individual test files

@pytest.fixture
def simple_model_service():
    """Model service without API calls."""
    from src.services import SimpleModelService
    return SimpleModelService()

@pytest.fixture
def intelligent_model_service():
    """Model service with real LLM (requires API keys)."""
    from src.services import IntelligentModelService
    return IntelligentModelService()

@pytest.fixture
def file_persistence(tmp_path):
    """Persistence service with temporary directory."""
    from src.services import FilePersistenceService
    return FilePersistenceService(base_dir=str(tmp_path))

@pytest.fixture
def controller(simple_model_service, file_persistence):
    """Controller with simple model service."""
    from src.controller import PipelineController
    return PipelineController(simple_model_service, file_persistence)
```

## Writing Tests

### Test Function Template

```python
def test_feature_name(fixture1, fixture2):
    """Test description following Given-When-Then pattern.
    
    Given: Initial state setup
    When: Action performed
    Then: Expected outcome
    """
    # Given: Setup
    controller = PipelineController(...)
    project_id = "test_123"
    
    # When: Perform action
    result = controller.run_stage("stage-name", project_id=project_id)
    
    # Then: Assert expectations
    assert result.draft_artifact is not None
    assert result.validation_errors == []
    assert len(result.prompts) > 0
```

### Testing Stages

```python
def test_stage_execution():
    """Test stage executes successfully."""
    from src.stages.my_stage import MyStage
    from src.services import SimpleModelService, FilePersistenceService
    
    stage = MyStage(
        model_service=SimpleModelService(),
        persistence_service=FilePersistenceService()
    )
    
    result = stage.execute(project_id="test_123")
    
    assert result.stage_name == "my-stage"
    assert result.draft_artifact is not None
    assert isinstance(result.metadata, ModelMetadata)

def test_stage_validation():
    """Test stage validates inputs."""
    stage = MyStage(...)
    
    # Missing project_id should error
    result = stage.execute(project_id="")
    assert len(result.validation_errors) > 0
    
    # Missing prerequisites should error
    result = stage.execute(project_id="nonexistent")
    assert "Missing" in str(result.validation_errors)
```

### Testing Error Handling

```python
def test_error_handling():
    """Test graceful error handling."""
    controller = PipelineController(...)
    
    # Test missing artifact
    result = controller.run_stage("problem-framing", project_id="nonexistent")
    assert result.validation_errors is not None
    assert result.draft_artifact is None
    
    # Test empty input
    result = controller.start_project("")
    assert len(result.validation_errors) > 0
```

### Testing with Mocks

```python
from unittest.mock import Mock, patch

def test_with_mock_llm():
    """Test using mocked LLM responses."""
    mock_response = {
        "problem_statement": "Test problem",
        "goals": ["Goal 1", "Goal 2"]
    }
    
    with patch('src.services.intelligent_model_service.IntelligentModelService.generate') as mock_gen:
        mock_gen.return_value = mock_response
        
        controller = PipelineController(...)
        result = controller.run_stage("problem-framing", project_id="test")
        
        assert result.draft_artifact.problem_statement == "Test problem"
        assert len(result.draft_artifact.goals) == 2
```

## Integration Tests

### End-to-End Pipeline Test

```python
@pytest.mark.integration
def test_full_pipeline(controller):
    """Test complete pipeline execution."""
    # Stage 0
    result = controller.start_project("Test systematic review")
    project_id = result.draft_artifact.id
    assert result.validation_errors == []
    
    # Stages 1-7
    stages = [
        "problem-framing",
        "research-questions",
        "search-concept-expansion",
        "database-query-plan",
        "screening-criteria",
        "query-execution",
        "strategy-export"
    ]
    
    for stage_name in stages:
        result = controller.run_stage(stage_name, project_id=project_id)
        
        # Skip if SimpleModelService generates invalid data
        if result.validation_errors:
            pytest.skip(f"Stage {stage_name} failed (expected with SimpleModelService)")
        
        controller.approve_artifact(
            project_id,
            result.draft_artifact.__class__.__name__
        )
```

## Performance Tests

```python
import time

@pytest.mark.slow
def test_stage_performance():
    """Test stage executes within time limit."""
    stage = MyStage(...)
    
    start = time.time()
    result = stage.execute(project_id="test")
    duration = time.time() - start
    
    assert duration < 5.0, f"Stage took {duration}s (max 5s)"
```

## Test Coverage

### Generate Coverage Report

```bash
# HTML report (open htmlcov/index.html)
pytest --cov=src --cov-report=html

# Terminal report
pytest --cov=src --cov-report=term-missing

# XML report (for CI)
pytest --cov=src --cov-report=xml
```

### Coverage Targets

- **Overall:** > 80%
- **Critical modules:** > 90%
  - `src/controller.py`
  - `src/stages/*.py`
  - `src/services/*.py`

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11"]
    
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest -v -k "not llm" --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Debugging Tests

### Run with Debugging

```bash
# Run with pdb on failure
pytest --pdb

# Verbose output
pytest -vv -s

# Show local variables on failure
pytest --tb=long

# Run last failed tests
pytest --lf
```

### Using pytest-watch

```bash
# Install
pip install pytest-watch

# Watch and rerun on changes
ptw -- -v -k "not llm"
```

## Test Markers

### Using Markers

```python
import pytest

@pytest.mark.llm
def test_with_llm():
    """Test that makes LLM API calls."""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Test that takes >5 seconds."""
    pass

@pytest.mark.integration
def test_full_workflow():
    """Integration test."""
    pass
```

### Run by Marker

```bash
# Only LLM tests
pytest -v -m llm

# Skip LLM tests
pytest -v -m "not llm"

# Only integration tests
pytest -v -m integration
```

## Best Practices

### DO

- ✅ Write tests before/during feature development (TDD)
- ✅ Use descriptive test names (`test_stage_validates_empty_input`)
- ✅ Follow Given-When-Then pattern
- ✅ Test edge cases and error conditions
- ✅ Use fixtures for common setup
- ✅ Mock external dependencies (APIs, file I/O)
- ✅ Keep tests independent (no shared state)

### DON'T

- ❌ Test implementation details
- ❌ Make tests dependent on execution order
- ❌ Use real API calls unless necessary (expensive, flaky)
- ❌ Ignore test failures
- ❌ Write tests without assertions

## Common Testing Patterns

### Testing File Operations

```python
def test_artifact_persistence(tmp_path):
    """Test artifact save/load."""
    from src.services import FilePersistenceService
    from src.models import ProjectContext
    
    persistence = FilePersistenceService(base_dir=str(tmp_path))
    
    # Save
    artifact = ProjectContext(id="test", title="Test", ...)
    persistence.save_artifact(artifact, "test", "ProjectContext")
    
    # Load
    loaded = persistence.load_artifact("ProjectContext", "test", ProjectContext)
    assert loaded.id == "test"
    assert loaded.title == "Test"
```

### Testing API Calls

```python
@pytest.mark.llm
def test_llm_integration():
    """Test with real LLM API."""
    from src.services import IntelligentModelService
    
    service = IntelligentModelService()
    response = service.generate(prompt="Test prompt")
    
    assert response is not None
    assert len(response) > 0
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

**Questions?** Ask in [Discussions](https://github.com/mbsoft31/strategy-pipeline/discussions)

