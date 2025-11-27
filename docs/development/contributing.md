# Contributing Guide
Thank you for contributing! 🎉

---

Be respectful, collaborative, and constructive. See [CODE_OF_CONDUCT.md](../../CODE_OF_CONDUCT.md).

## Code of Conduct

- 📧 Email: bekhouche.mouadh@univ-oeb.dz
- 🐛 [Issue Tracker](https://github.com/mbsoft31/strategy-pipeline/issues)
- 💬 [GitHub Discussions](https://github.com/mbsoft31/strategy-pipeline/discussions)

## Getting Help

5. Create GitHub release
4. Push: `git push --tags`
3. Tag release: `git tag v1.0.0`
2. Bump version
1. Update `CHANGELOG.md`

### Creating a Release

```
bumpversion major  # 1.0.0 -> 2.0.0
bumpversion minor  # 1.0.0 -> 1.1.0
bumpversion patch  # 1.0.0 -> 1.0.1
# Bump version
```bash

### Version Bumping

## Release Process

```
    pass
    # This test is skipped with: pytest -k "not llm"
    """Test that requires LLM API (expensive)."""
def test_with_llm():
@pytest.mark.llm

        my_fixture.do_something(invalid_input)
    with pytest.raises(ValueError):
    """Test error cases."""
def test_error_handling(my_fixture):

    assert result == expected
    result = my_fixture.do_something()
    """Test basic use case."""
def test_basic_functionality(my_fixture):

    return MyClass()
    """Fixture docstring."""
def my_fixture():
@pytest.fixture

from src.my_module import MyClass
import pytest
# tests/test_my_feature.py
```python

### Test Structure

- **All tests pass** before PR
- **Coverage** > 80% for new code
- **Integration tests** for new stages
- **Unit tests** for all new functions

### Test Requirements

## Testing

```
mkdocs build
# Build static site

# Visit http://localhost:8000
mkdocs serve
# Serve locally

pip install mkdocs mkdocs-material mkdocstrings[python]
# Install MkDocs
```bash

### Build Documentation Locally

4. **Add examples** to `docs/examples/`
3. **Update API reference** if needed
2. **Add docstrings** to all public functions
1. **Update relevant .md files** in `docs/`

When adding features:

### Update Documentation

## Documentation

```
]
    "MyDatabase",
    # ...existing...
SUPPORTED_DATABASES = [
# src/stages/database_query_plan.py
```python

### 3. Add to Query Generator

```
        }
            'mydatabase': MyProvider(),
            # ...existing providers...
        self.PROVIDERS = {
    def __init__(self):
class SearchService:

from ..slr.providers.my_provider import MyProvider
# src/services/search_service.py
```python

### 2. Register Provider

```
        )
            # ...
            title=result['title'],
            id=result['id'],
        return Document(
        """Parse API result to Document."""
    def _parse_result(self, result: dict) -> Document:
    
        return documents[:max_results]
        documents = [self._parse_result(r) for r in response.json()]
        # Parse response
        
        response = requests.get(f"{API_URL}?q={query}")
        # API call
        """Execute search query."""
    def search(self, query: str, max_results: int = 100) -> List[Document]:
    
    """Provider for MyDatabase API."""
class MyProvider(BaseProvider):

from ..core.models import Document
from .base import BaseProvider
# src/slr/providers/my_provider.py
```python

### 1. Create Provider

## Adding a Database Provider

```
    assert len(result.validation_errors) == 0
    assert result.draft_artifact is not None
    result = stage.execute(project_id="test_123")
    stage = MyNewStage(...)
def test_my_new_stage():
# tests/test_my_new_stage.py
```python

### 4. Add Tests

```
    self.register_stage("my-new-stage", MyNewStage)
    # ...existing stages...
def _register_default_stages(self):

from ..stages.my_new_stage import MyNewStage
# src/orchestration/stage_orchestrator.py
```python

### 3. Register Stage

```
    model_metadata: ModelMetadata
    data: List[str]
    project_id: str
    """Artifact produced by MyNewStage."""
class MyArtifact(BaseArtifact):
@dataclass
# src/models.py
```python

### 2. Add Artifact Model

```
        )
            validation_errors=[]
            prompts=["Stage complete"],
            metadata=ModelMetadata(...),
            draft_artifact=result_artifact,
            stage_name="my-new-stage",
        return StageResult(
        
        self.persistence_service.save_artifact(result_artifact, project_id, "MyArtifact")
        # Save artifact
        
        result_artifact = ...
        # Stage logic here
        
        prerequisite = self.persistence_service.load_artifact(...)
        # Load prerequisites
        """
            StageResult with artifact and metadata
        Returns:
        
            **kwargs: Additional options
            project_id: Project identifier
        Args:
        
        """Execute the stage.
    def execute(self, *, project_id: str, **kwargs) -> StageResult:
    
    """Brief description of what this stage does."""
class MyNewStage(BaseStage):

from ..models import ModelMetadata
from .base import BaseStage, StageResult
from datetime import UTC, datetime
# src/stages/my_new_stage.py
```python

### 1. Create Stage File

## Adding a New Stage

```
└── examples/            # Usage examples
├── frontend/            # React UI
├── docs/                # Documentation
├── tests/               # Test suite
│   └── orchestration/   # Orchestration layer
│   ├── controller.py    # Main controller
│   ├── models.py        # Data models
│   ├── services/        # Core services
│   ├── stages/          # Pipeline stages
├── src/
strategy-pipeline/
```

## Project Structure

5. **Respond to reviews** - Address feedback promptly
4. **Create PR** - Use the PR template
3. **Run checks** - Ensure all tests pass
2. **Update docs** - Update relevant documentation
1. **Update tests** - Add tests for new features

### Pull Request Process

```
git commit -m "docs: Update installation guide for Windows"
git commit -m "fix: Handle empty query results in Stage 7"
git commit -m "feat: Add Stage 8 for automated screening"
```bash
Examples:

```
chore: Build/config changes
perf: Performance improvements
refactor: Code refactoring
test: Add or modify tests
docs: Documentation changes
fix: Bug fix
feat: Add new feature
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):

### Commit Messages

- **Line Length:** 100 characters (black default)
- **Type Hints:** Required for all public functions
- **Docstrings:** Use Google style
- **Python:** Follow PEP 8

### Code Style

## Contribution Guidelines

```
"
print(f'Project ID: {result.draft_artifact.id}')
result = controller.start_project('Test project')
controller = PipelineController(SimpleModelService(), FilePersistenceService())

from src.services import SimpleModelService, FilePersistenceService
from src.controller import PipelineController
python -c "
# Using Python

python -m src.cli run-pipeline "Your research question"
# Using CLI
```bash

### Running the Pipeline Locally

```
mypy src/
# Type checking

pylint src/
flake8 src/ tests/
# Lint

black src/ tests/
# Format code
```bash

### Code Quality

```
pytest --cov=src --cov-report=html
# With coverage

pytest tests/test_stage7_query_execution.py -v
# Specific test file

pytest -v -k "not llm"
# All tests (skip LLM tests to avoid API costs)
```bash

### Running Tests

## Development Workflow

```
git checkout -b fix/issue-123
# or
git checkout -b feature/your-feature-name
```bash

### 3. Create a Branch

```
pre-commit install
# Install pre-commit hooks

pip install -r requirements-dev.txt  # Development tools
pip install -r requirements.txt
# Install dependencies

source venv/bin/activate  # Windows: venv\Scripts\activate
python -m venv venv
# Create virtual environment
```bash

### 2. Set Up Development Environment

```
git remote add upstream https://github.com/mbsoft31/strategy-pipeline.git
cd strategy-pipeline
git clone https://github.com/YOUR_USERNAME/strategy-pipeline.git
```bash

### 1. Fork and Clone

## Getting Started

Thank you for considering contributing to the Strategy Pipeline project!


