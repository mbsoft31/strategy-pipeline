# Contributing to Strategy Pipeline

Thank you for your interest in contributing to Strategy Pipeline! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Style Guide](#style-guide)

---

## Code of Conduct

This project follows a simple code of conduct:
- Be respectful and professional
- Focus on constructive feedback
- Help create a welcoming environment
- Report issues appropriately

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Virtual environment tool (venv)
- Basic understanding of systematic literature reviews (helpful but not required)

### First Steps

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/strategy-pipeline.git
   cd strategy-pipeline
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate it
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Mac/Linux
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your settings (use mock mode for testing)
   ```

4. **Run tests to verify setup**
   ```bash
   pytest tests/ -v
   ```

---

## Development Setup

### Environment Configuration

For development, use **mock mode** to avoid API costs:

`.env` file:
```env
LLM__PROVIDER=mock
LLM__OPENAI_API_KEY=
LLM__OPENAI_MODEL=gpt-4o-mini
LLM__OPENAI_TEMPERATURE=0.7
```

### Recommended Tools

- **IDE:** VS Code, PyCharm, or similar
- **Linter:** pylint, flake8
- **Formatter:** black (optional)
- **Type checker:** mypy (optional)

---

## Project Structure

```
strategy-pipeline/
├── src/                    # Source code
│   ├── stages/            # Pipeline stages (0-6)
│   ├── services/          # LLM, model, persistence services
│   ├── search/            # Anti-Hallucination syntax engine
│   └── utils/             # Utilities and exceptions
│
├── tests/                 # Test suite
├── examples/              # Demo scripts
│   └── demos/            # Feature demonstrations
├── scripts/              # Utility scripts
│   └── utilities/        # Verification and testing scripts
├── interfaces/           # CLI and Web UI
├── docs/                 # Documentation
│   ├── stages/          # Stage-specific docs
│   ├── sprints/         # Sprint tracking
│   ├── plans/           # Implementation plans
│   ├── guides/          # Technical guides
│   └── archive/         # Historical docs
│
└── Configuration files
```

---

## Making Changes

### Branch Naming

Use descriptive branch names:
```bash
feature/add-stage-5-screening
bugfix/fix-empty-query-validation
docs/update-deployment-guide
refactor/clean-test-structure
```

### Workflow

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, focused commits
   - Follow the style guide
   - Add tests for new features
   - Update documentation

3. **Test your changes**
   ```bash
   # Run all tests
   pytest tests/ -v
   
   # Run specific test file
   pytest tests/test_stage4_query_plan.py -v
   
   # Check code coverage
   pytest tests/ --cov=src
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add Stage 5 screening criteria generation"
   ```

### Commit Message Format

Follow conventional commits:

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat: add complexity analysis to Stage 4"
git commit -m "fix: resolve empty query validation issue"
git commit -m "docs: update deployment guide with Docker instructions"
git commit -m "refactor: organize demo scripts into examples folder"
```

---

## Testing

### Writing Tests

All new features should include tests:

```python
# tests/test_new_feature.py
import pytest
from src.stages.new_stage import NewStage

def test_new_feature():
    """Test that new feature works correctly."""
    stage = NewStage()
    result = stage.execute(param="test")
    assert result is not None
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_stage4_query_plan.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_stage4_query_plan.py::test_empty_blocks_validation
```

### Test Organization

- Unit tests: `tests/test_{module}.py`
- Integration tests: Include in test files
- Demos: `examples/demos/demo_{feature}.py`
- Utilities: `scripts/utilities/verify_{feature}.py`

---

## Documentation

### When to Update Documentation

Update documentation when you:
- Add a new stage
- Add a new feature
- Change existing behavior
- Fix a bug that affects usage
- Add new configuration options

### Documentation Files

**Stage Documentation:**
- Location: `docs/stages/`
- Format: `STAGE{N}_{DESCRIPTION}.md`
- Include: Implementation details, usage examples, test results

**Guides:**
- Location: `docs/guides/`
- Include: Setup, deployment, technical references

**Plans:**
- Location: `docs/plans/`
- Format: `plan-{camelCaseName}.prompt.md`
- Include: Future implementation plans

**Update the Master Index:**
- Always update `docs/INDEX.md` with new documentation

### Docstrings

Use clear docstrings for all public functions:

```python
def generate_query(blocks: SearchConceptBlocks, database: str) -> str:
    """Generate database-specific Boolean query.
    
    Args:
        blocks: Search concept blocks with included/excluded terms
        database: Target database name (pubmed, scopus, etc.)
    
    Returns:
        Formatted Boolean query string
    
    Raises:
        ValueError: If database is not supported
    
    Example:
        >>> blocks = SearchConceptBlocks(...)
        >>> query = generate_query(blocks, "pubmed")
        >>> print(query)
        ("term1"[tiab] OR "term2"[tiab]) AND ...
    """
    # Implementation
```

---

## Submitting Changes

### Pull Request Process

1. **Update your branch**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Push to your fork**
   ```bash
   git push origin your-branch
   ```

3. **Create Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Tested manually

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)

## Related Issues
Closes #123
```

### Review Process

- Maintainers will review your PR
- Address feedback promptly
- Keep discussions focused and professional
- Be patient - reviews take time

---

## Style Guide

### Python Style

Follow PEP 8 with these additions:

**Imports:**
```python
# Standard library
import os
from typing import List, Optional

# Third-party
import pytest
import streamlit as st

# Local
from src.models import ProjectContext
from src.services import ModelService
```

**Naming:**
```python
# Classes: PascalCase
class DatabaseQueryPlan:
    pass

# Functions/variables: snake_case
def generate_query(concept_blocks):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_QUERY_LENGTH = 4000
```

**Type Hints:**
```python
def execute(
    self, 
    *, 
    project_id: str, 
    target_databases: Optional[List[str]] = None
) -> StageResult:
    """Use type hints for clarity."""
    pass
```

### File Organization

**Keep files focused:**
- One class per file (generally)
- Group related functions
- Maximum ~500 lines per file

**File naming:**
- Modules: `snake_case.py`
- Classes: Match class name in PascalCase
- Tests: `test_{module}.py`

---

## Adding New Features

### Adding a New Stage

1. **Create stage file:** `src/stages/new_stage.py`
2. **Implement BaseStage:** Extend `BaseStage` class
3. **Add tests:** `tests/test_new_stage.py`
4. **Register stage:** Update `src/controller.py`
5. **Document:** Create `docs/stages/STAGEN_COMPLETE.md`
6. **Update:** Modify `docs/INDEX.md`

### Adding a New Database Dialect

1. **Create dialect:** Add to `src/search/dialects.py`
2. **Add tests:** Update `tests/test_syntax_engine.py`
3. **Validate:** Run `scripts/utilities/validate_dialects.py`
4. **Document:** Update `docs/guides/DIALECT_EXAMPLES.md`

### Adding a New Demo

1. **Create demo:** `examples/demos/demo_{feature}.py`
2. **Add docstring:** Explain what it demonstrates
3. **Update README:** Add to `examples/README.md`
4. **Test:** Ensure it runs without errors

---

## Common Tasks

### Running the Full Pipeline

```bash
python examples/demos/demo_full_pipeline.py
```

### Testing a Single Stage

```bash
python -c "
from src.controller import PipelineController
from src.services import SimpleModelService, FilePersistenceService

controller = PipelineController(
    model_service=SimpleModelService(),
    persistence_service=FilePersistenceService()
)

result = controller.start_project(raw_idea='Test idea')
print(result.draft_artifact)
"
```

### Validating Query Generation

```bash
python scripts/utilities/validate_dialects.py
```

---

## Getting Help

- **Documentation:** Check `docs/INDEX.md`
- **Examples:** Look at `examples/demos/`
- **Issues:** Search existing issues on GitHub
- **Questions:** Open a GitHub Discussion

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md (coming soon)
- Mentioned in release notes
- Credited in relevant documentation

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License - to be added).

---

**Thank you for contributing to Strategy Pipeline!** 🚀

Your contributions help make systematic literature reviews more accessible and efficient for researchers worldwide.

