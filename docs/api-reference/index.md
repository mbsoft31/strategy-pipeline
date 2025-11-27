# API Reference

Auto-generated API documentation from Python docstrings.

## Overview

This section contains detailed API documentation for all modules, classes, and functions in the Strategy Pipeline.

## Core Modules

### [Controller](controller.md)
Main entry point for the pipeline. Provides a facade for all pipeline operations.

- **PipelineController** - Main controller class
- Methods: `start_project()`, `run_stage()`, `approve_artifact()`, `list_projects()`

### [Stages](stages.md)
Pipeline stage implementations (Stages 0-7).

- **BaseStage** - Base class for all stages
- **ProjectSetupStage** - Stage 0: Project initialization
- **ProblemFramingStage** - Stage 1: PICO extraction
- **ResearchQuestionStage** - Stage 2: Research question generation
- **SearchConceptExpansionStage** - Stage 3: Keyword expansion
- **DatabaseQueryPlanStage** - Stage 4: Query generation
- **ScreeningCriteriaStage** - Stage 5: Inclusion/exclusion criteria
- **QueryExecutionStage** - Stage 7: Database search execution
- **StrategyExportStage** - Stage 6: Multi-format export

### [Services](services.md)
Core service layer for LLM, persistence, and search.

- **ModelService** - Base class for LLM interaction
- **IntelligentModelService** - Production LLM service (OpenAI/Anthropic)
- **SimpleModelService** - Testing service (no API calls)
- **PersistenceService** - Base class for artifact storage
- **FilePersistenceService** - File-based persistence
- **SearchService** - Academic database search integration

### [Models](models.md)
Data models and artifact schemas.

- **ProjectContext** - Project metadata
- **ProblemFraming** - PICO elements and scope
- **ConceptModel** - Extracted concepts
- **ResearchQuestionSet** - Generated research questions
- **SearchConceptBlocks** - Keyword blocks for queries
- **DatabaseQueryPlan** - Generated boolean queries
- **ScreeningCriteria** - Inclusion/exclusion criteria
- **SearchResults** - Query execution results
- **StrategyExportBundle** - Export metadata

### [Orchestration](orchestration.md)
Pipeline orchestration and artifact management.

- **StageOrchestrator** - Stage execution coordinator
- **ArtifactManager** - Artifact lifecycle management

## Quick Links

### Most Used Classes

- [PipelineController](controller.md#pipelinecontroller) - Main entry point
- [BaseStage](stages.md#basestage) - Extend to create custom stages
- [SearchService](services.md#searchservice) - Database search operations
- [FilePersistenceService](services.md#filepersistenceservice) - Save/load artifacts

### Common Operations

```python
# Initialize controller
from src.controller import PipelineController
from src.services import IntelligentModelService, FilePersistenceService

controller = PipelineController(
    IntelligentModelService(),
    FilePersistenceService()
)

# Start project
result = controller.start_project("Research question")

# Run stage
result = controller.run_stage("problem-framing", project_id=project_id)

# Approve artifact
controller.approve_artifact(project_id, "ProblemFraming")

# List projects
projects = controller.list_projects()
```

## Documentation Generation

This API reference is auto-generated from source code docstrings using:
- **Tool:** MkDocs + mkdocstrings plugin
- **Style:** Google docstring format
- **Update:** Automatically updates when code changes

### Regenerate Documentation

```bash
mkdocs build
```

## Docstring Format

All public APIs use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """Short description of the function.
    
    Longer description with more details about what the function does,
    edge cases, and usage examples.
    
    Args:
        param1: Description of first parameter.
        param2: Description of second parameter.
    
    Returns:
        Description of return value.
    
    Raises:
        ValueError: When param2 is negative.
    
    Example:
        >>> result = my_function("hello", 42)
        >>> print(result)
        True
    """
    ...
```

## Contributing to API Docs

When adding new functions/classes:

1. **Add docstrings** using Google format
2. **Include examples** in docstrings
3. **Document all parameters** with types
4. **Note exceptions** that may be raised
5. **Run mkdocs build** to verify

See [Contributing Guide](../development/contributing.md) for details.

---

**Note:** This reference documents the **public API**. Internal implementation details are subject to change.

**Version:** 1.0  
**Last Updated:** Auto-generated from source code

