# Services

Core services for LLM interaction, persistence, and academic database search.

## SearchService

Execute database searches and manage search results across multiple academic databases.

**Supported Databases:**
- arXiv
- OpenAlex
- Crossref
- Semantic Scholar

**Example:**

```python
from src.services import SearchService

service = SearchService(project_id="project_123")

# Execute search
result = service.execute_search(
    database="openalex",
    query_string="machine learning healthcare",
    max_results=100
)

# Load results
papers = service.load_results(result.file_path)

# Deduplicate
deduplicated = service.deduplicate_results(papers)
```

::: src.services.search_service.SearchService
    options:
      show_source: true
      heading_level: 3
      show_signature_annotations: true
      members_order: source

---

## ModelService

Abstract interface for LLM/SLM services. Provides the contract that all model services must implement.

::: src.services.model_service.ModelService
    options:
      show_source: false
      heading_level: 3
      show_signature_annotations: true
      members:
        - generate
        - model_name
        - mode

---

## IntelligentModelService

Production LLM service with validation. Uses OpenAI or Anthropic APIs.

**Example:**

```python
from src.services import IntelligentModelService

# Using OpenAI
service = IntelligentModelService(
    model_name="gpt-4",
    temperature=0.7
)

# Using Anthropic
service = IntelligentModelService(
    model_name="claude-3-opus-20240229",
    temperature=0.7
)
```

::: src.services.intelligent_model_service.IntelligentModelService
    options:
      show_source: true
      heading_level: 3
      show_signature_annotations: true
      members_order: source

---

## SimpleModelService

Fast heuristic-based service that doesn't make LLM API calls. Useful for testing.

**Example:**

```python
from src.services import SimpleModelService

# No API key needed
service = SimpleModelService()

# Fast, deterministic responses
response = service.generate(prompt="Test prompt")
```

::: src.services.simple_model_service.SimpleModelService
    options:
      show_source: true
      heading_level: 3
      show_signature_annotations: true
      members_order: source

---

## FilePersistenceService

File-based artifact persistence service. Handles serialization and storage of all pipeline artifacts.

**Example:**

```python
from src.services import FilePersistenceService
from src.models import ProjectContext

persistence = FilePersistenceService(base_dir="./data")

# Save artifact
artifact = ProjectContext(...)
persistence.save_artifact(artifact, "project_123", "ProjectContext")

# Load artifact
loaded = persistence.load_artifact("ProjectContext", "project_123", ProjectContext)
```

::: src.services.persistence_service.FilePersistenceService
    options:
      show_source: true
      heading_level: 3
      show_signature_annotations: true
      members_order: source

---

## PersistenceService

Abstract base class for persistence services.

::: src.services.persistence_service.PersistenceService
    options:
      show_source: false
      heading_level: 3
      show_signature_annotations: true

