# Configuration Guide
**Need Help?** [Report an Issue](https://github.com/mbsoft31/strategy-pipeline/issues)

---

- 💻 [Development](../development/contributing.md) - Contributing guide
- 🏗️ [Architecture](../architecture/overview.md) - System design
- 📖 [User Guide](../user-guide/quick-reference.md) - Comprehensive reference

## Next Steps

```
controller.stage_orchestrator.register_stage("custom-stage", CustomStage)
# Register custom stage

        )
            validation_errors=[]
            prompts=["Custom stage complete"],
            ),
                generated_at=datetime.now(UTC)
                mode="custom",
                model_name="custom",
            metadata=ModelMetadata(
            draft_artifact=my_artifact,
            stage_name="custom-stage",
        return StageResult(
        
        ...
        # Custom logic
    def execute(self, *, project_id: str, **kwargs) -> StageResult:
    
    """Custom stage implementation."""
class CustomStage(BaseStage):

from datetime import datetime, UTC
from src.models import ModelMetadata
from src.stages.base import BaseStage, StageResult
```python

## Advanced: Custom Stages

```
.pytest_cache/
__pycache__/
logs/
data/
.cache/
*.env
.env
```gitignore

Ensure these are ignored:

### .gitignore

```
model = IntelligentModelService(api_key="sk-...")  # Bad!
# ❌ DON'T: Hardcode in source

OPENAI_API_KEY=sk-...
# ✅ DO: Use environment variables
```bash

### API Key Management

## Security Best Practices

```
pytest tests/test_full_pipeline_stages_0_7.py -v
# Integration tests

pytest tests/test_stages/ -v
# Only unit tests

pytest -v -k "not llm"
# All tests (skip LLM to avoid costs)
```bash

Run tests:

```
    integration: end-to-end integration tests
    slow: tests that take >5 seconds
    llm: tests that require LLM API calls
markers =
    --strict-markers
    --tb=short
    -s
    -v
addopts = 
python_functions = test_*
python_classes = Test*
python_files = test_*.py
testpaths = tests
[pytest]
```ini

Create `pytest.ini`:

### pytest Configuration

## Testing Configuration

```
            raise
            # Send notification, retry, etc.
            logger.error(f"Stage {stage_name} failed: {e}")
            # Custom error handling
        except Exception as e:
            return result
            result = super().run_stage(stage_name, **kwargs)
        try:
    def run_stage(self, stage_name, **kwargs):
class CustomController(PipelineController):

from src.controller import PipelineController
```python

### Custom Error Handlers

## Error Handling

```
NCBI_EMAIL=your.email@example.com
NCBI_TOOL=strategy-pipeline
NCBI_API_KEY=your_api_key
# .env
```bash

### PubMed E-utilities (Future)

- More detailed metadata
- Priority access
- Higher rate limits
Benefits:

```
S2_API_KEY=your_api_key_here
# .env
```bash

### Semantic Scholar API Key (Optional)

## Database-Specific Configuration

```
    results = [f.result() for f in futures]
    ]
        executor.submit(run_stage, "search-concept-expansion")
        executor.submit(run_stage, "research-questions"),
        executor.submit(run_stage, "problem-framing"),
    futures = [
    # Stages 1, 2, 3 don't depend on each other
with ThreadPoolExecutor(max_workers=3) as executor:

    return controller.run_stage(stage_name, project_id=project_id)
def run_stage(stage_name):

from concurrent.futures import ThreadPoolExecutor
# Run stages in parallel (experimental)
```python

### Parallel Execution

```
)
    cache_dir=".cache/llm"
    cache_responses=True,
model_service = IntelligentModelService(
# Enable model response caching (reduces costs)
```python

### Caching

## Performance Tuning

```
logging.getLogger('src.services').setLevel(logging.INFO)
logging.getLogger('src.stages').setLevel(logging.DEBUG)
# Per-module logging

)
    ]
        logging.StreamHandler()
        logging.FileHandler('logs/pipeline.log'),
    handlers=[
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
logging.basicConfig(
# Configure logging

import logging
```python

### Python Logging

## Logging Configuration

| Web of Science | `wos` | ⚠️ Syntax Only | Requires Clarivate key |
| Scopus | `scopus` | ⚠️ Syntax Only | Requires Elsevier API key |
| PubMed | `pubmed` | ⚠️ Syntax Only | Requires E-utilities auth |
| Semantic Scholar | `s2` or `semanticscholar` | ✅ Live | Free, optional API key |
| Crossref | `crossref` | ✅ Live | DOI registry, free |
| arXiv | `arxiv` | ✅ Live | Preprints, no auth |
| OpenAlex | `openalex` | ✅ Live | Free, no auth required |
|----------|-------------|--------|-------|
| Database | Provider Key | Status | Notes |

### Supported Databases

```
)
    save_to_disk=True          # Save results
    max_results=200,           # Default: 100
    query="machine learning healthcare",
    database="openalex",
result = search_service.execute_search(
# Execute search with options

)
    project_id="project_abc123"
    base_dir="./data",
search_service = SearchService(
# Custom configuration

from src.services import SearchService
```python

### Database Provider Settings

## Search Service Configuration

```
)
    export_formats=["csv", "bibtex", "ris"]  # Formats to export
    include_markdown=True,           # Generate PRISMA protocol
    project_id=project_id,
    "strategy-export",
result = controller.run_stage(
# Stage 6: Strategy Export

)
    max_results_per_db=100           # Limit per database
    auto_deduplicate=True,           # Merge results
    project_id=project_id,
    "query-execution",
result = controller.run_stage(
# Stage 7: Query Execution

)
    include_study_designs=True       # Add PRISMA defaults
    refine_with_queries=True,        # Use query complexity
    project_id=project_id,
    "screening-criteria",
result = controller.run_stage(
# Stage 5: Screening Criteria
```python

### Stage-Specific Options

## Stage Configuration

```
# │   └── export/
# │   ├── search_results/
# │   ├── ...
# │   ├── ProblemFraming.json
# │   ├── ProjectContext.json
# ├── project_abc123/
# my_data/
# Project structure:

)
    base_dir="./my_data"  # Default: "./data"
persistence = FilePersistenceService(
# Custom base directory

from src.services import FilePersistenceService
```python

### FilePersistenceService

## Persistence Configuration

```
model_service = SimpleModelService()
# No API calls, uses templates

from src.services import SimpleModelService
```python

### SimpleModelService (Testing)

```
)
    max_tokens=1500
    temperature=0.7,
    model_name="gpt-3.5-turbo",
model_service = IntelligentModelService(
# OpenAI GPT-3.5 (cheaper)

)
    max_tokens=4000
    temperature=0.7,
    model_name="claude-3-opus-20240229",
model_service = IntelligentModelService(
# Anthropic Claude

)
    max_tokens=2000
    temperature=0.7,
    model_name="gpt-4",
model_service = IntelligentModelService(
# OpenAI GPT-4

from src.services import IntelligentModelService
```python

### IntelligentModelService (Production)

## Model Service Configuration

```
LOG_FILE=logs/pipeline.log
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR
# Logging

ANTHROPIC_BASE_URL=https://api.anthropic.com
OPENAI_BASE_URL=https://api.openai.com/v1
# Optional: Custom endpoints

SLR_MAILTO=your.email@example.com  # Required for some APIs
# Database API Configuration

MODEL_MODE=intelligent              # or simple (testing mode)
MODEL_NAME=gpt-4                    # or claude-3-opus-20240229
# Model Selection

ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
# LLM Provider Configuration
```bash

Create a `.env` file in the project root:

## Environment Variables

Advanced configuration options for the Strategy Pipeline.


