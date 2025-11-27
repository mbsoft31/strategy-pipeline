# Stage 7: Query Execution - Implementation Summary

**Date:** November 27, 2025  
**Status:** ✅ COMPLETE - Ready for Testing

***

## What Was Implemented

### 1. SearchResults Artifact Model (`src/models.py`)

Added new artifact to store **metadata only** (not full papers):

```python
@dataclass
class SearchResults:
    """Metadata for executed search results.
    
    NOTE: This artifact does NOT contain the papers themselves (too large).
    Papers are stored in separate JSON files referenced by result_file_paths.
    Use SearchService.load_results(file_path) to read papers.
    """
    project_id: str
    total_results: int  # Total papers before deduplication
    deduplicated_count: int  # Papers after deduplication
    databases_searched: List[str]  # e.g., ["arxiv", "openalex", "crossref"]
    result_file_paths: List[str]  # Paths to JSON files containing papers
    deduplication_stats: Dict[str, Any]  # {"original_count": 347, "duplicates_removed": 52, ...}
    execution_time_seconds: float
    created_at: datetime
    updated_at: datetime
    status: ApprovalStatus
    model_metadata: Optional[ModelMetadata]
    user_notes: Optional[str]
```

**Why File-Pointer Pattern:**
- Avoids artifact bloat (500+ papers = 5-15MB JSON)
- Keeps persistence service performant
- Enables streaming/pagination
- Supports incremental updates

***

### 2. SearchService Enhancements (`src/services/search_service.py`)

**A. Project-Scoped Storage (Backward Compatible)**

```python
def __init__(self, base_dir: str = "data", project_id: Optional[str] = None):
    """Initialize with optional project scoping."""
    self.base_dir = Path(base_dir)
    self.project_id = project_id
    
    # Project-scoped: data/{project_id}/search_results/
    # Legacy: data/search_results/
    if project_id:
        self.results_dir = self.base_dir / project_id / "search_results"
    else:
        self.results_dir = self.base_dir / "search_results"
```

**B. Save Deduplicated Results**

```python
def save_deduplicated_results(
    self,
    documents: List[Dict],
    databases: List[str]
) -> str:
    """Save merged deduplicated papers to JSON file."""
    filename = f"deduplicated_{db_label}_{timestamp}.json"
    # Returns path to saved file
```

**C. Updated SearchResultsSummary**

Added `file_path` alias for compatibility with Stage 7:

```python
@dataclass
class SearchResultsSummary:
    database: str
    query: str
    total_hits: int
    execution_time: float
    error: Optional[str] = None
    result_file: Optional[str] = None
    file_path: Optional[str] = None  # Alias for result_file
    timestamp: str = None
```

***

### 3. QueryExecutionStage (`src/stages/query_execution.py`)

**Key Features:**

✅ **Graceful Degradation**
- Unsupported databases (PubMed, Scopus, WoS) generate warnings, not errors
- Partial success returns results from working databases
- Complete failure returns validation errors

✅ **Auto-Deduplication**
- Runs by default when multiple databases queried
- Uses SLR's built-in deduplicator (DOI + title matching)
- Saves merged file: `deduplicated_{databases}_{timestamp}.json`
- Returns stats: `{"duplicates_removed": N, "deduplication_rate": X%}`

✅ **Database Mapping**
```python
SUPPORTED_DATABASES = {
    "arxiv": "arxiv",
    "crossref": "crossref", 
    "openalex": "openalex",
    "semantic_scholar": "s2",
    "s2": "s2",
}
```

✅ **User-Friendly Prompts**
```
Successfully retrieved 347 papers from 3 database(s): arxiv, openalex, crossref.
Deduplication removed 52 duplicate papers (15.0% reduction). Final unique papers: 295.
Result files saved to: data/project_abc123/search_results
```

**Execution Flow:**

1. Load `DatabaseQueryPlan` artifact
2. Initialize project-scoped `SearchService`
3. For each query:
   - Check if database supported
   - Execute search via provider
   - Save results to JSON
   - Collect warnings for failures
4. If multiple databases & `auto_deduplicate=True`:
   - Load all papers
   - Deduplicate via DOI/title
   - Save merged file
5. Create `SearchResults` artifact with metadata
6. Return prompts + warnings

***

### 4. Registration in Stage Orchestrator

```python
# src/orchestration/stage_orchestrator.py
from ..stages.query_execution import QueryExecutionStage

def _register_default_stages(self) -> None:
    """Register all built-in pipeline stages."""
    # ...existing stages...
    self.register_stage("query-execution", QueryExecutionStage)
    # ...remaining stages...
```

***

### 5. Comprehensive Test Suite (`tests/test_stage7_query_execution.py`)

**Test Coverage:**

- ✅ `test_query_execution_stage_registered()` - Verify registration
- ✅ `test_query_execution_stage_runs()` - End-to-end execution
- ✅ `test_search_results_structure()` - Artifact schema validation
- ✅ `test_search_results_files_exist()` - File creation verification
- ✅ `test_deduplication_runs()` - Multi-database dedup logic
- ✅ `test_project_scoped_storage()` - File organization check
- ⏸️ `test_unsupported_database_warning()` - Requires custom setup
- ⏸️ `test_partial_success_handling()` - Requires custom setup

**Test Strategy:**
- Uses `SimpleModelService` (no API costs)
- Skips tests gracefully if prerequisites fail
- Focuses on integration over unit tests

***

## How to Use Stage 7

### Basic Execution

```python
from src.controller import PipelineController
from src.services.simple_model_service import SimpleModelService
from src.services.persistence_service import PersistenceService

controller = PipelineController(
    SimpleModelService(),
    PersistenceService(base_dir="./data")
)

# Run stages 0-4 first
ctx = controller.start_project("LLM hallucination mitigation")
project_id = ctx.draft_artifact.id
controller.approve_artifact(project_id, "ProjectContext")

for stage in ["problem-framing", "research-questions", 
              "search-concept-expansion", "database-query-plan"]:
    result = controller.run_stage(stage, project_id=project_id)
    controller.approve_artifact(project_id, result.draft_artifact.__class__.__name__)

# Execute Stage 7
result = controller.run_stage("query-execution", project_id=project_id)

# Access results
search_results = result.draft_artifact
print(f"Total papers: {search_results.total_results}")
print(f"Deduplicated: {search_results.deduplicated_count}")
print(f"Databases: {search_results.databases_searched}")

# Load papers from file
from src.services.search_service import SearchService
service = SearchService()
papers = service.load_results(search_results.result_file_paths[0])
print(f"First paper: {papers[0]['title']}")
```

### Advanced Options

```python
# Disable auto-deduplication
result = controller.run_stage(
    "query-execution", 
    project_id=project_id,
    auto_deduplicate=False  # Keep separate database results
)

# Limit results per database
result = controller.run_stage(
    "query-execution", 
    project_id=project_id,
    max_results_per_db=50  # Default is 100
)
```

***

## File Organization

```
data/
└── {project_id}/
    ├── artifacts/
    │   ├── ProjectContext.json
    │   ├── DatabaseQueryPlan.json
    │   └── SearchResults.json  # ← Metadata only
    └── search_results/  # ← NEW: Project-scoped results
        ├── arxiv_machine_learning_20251127_143022.json
        ├── openalex_neural_architecture_20251127_143045.json
        ├── crossref_deep_learning_20251127_143108.json
        └── deduplicated_arxiv_openalex_crossref_20251127_143130.json
```

**Benefits:**
- Clean project isolation
- Easy cleanup (`rm -rf data/{project_id}/`)
- No global state pollution
- Supports multiple concurrent projects

***

## Implementation Statistics

| Metric | Count |
|--------|-------|
| **New Files Created** | 2 |
| **Files Modified** | 3 |
| **Total Lines Added** | ~450 |
| **New Artifact Models** | 1 |
| **New Stage Methods** | 3 |
| **Test Cases** | 8 |

***

## Known Limitations & Future Work

### Current Limitations

1. **Unsupported Databases**
   - PubMed (requires E-utilities auth)
   - Scopus (requires API key)
   - Web of Science (requires API key)
   - **Workaround:** Users can copy/paste queries from Stage 4 output

2. **No Query Timeout**
   - Slow APIs can hang indefinitely
   - **Future:** Add configurable timeout (60s default)

3. **No Incremental Execution**
   - Re-running Stage 7 re-fetches all databases
   - **Future:** Track executed queries, skip already-fetched

4. **No Real-Time Progress**
   - User doesn't see which database is running
   - **Future:** Add progress callbacks/logging

### Planned Enhancements (Week 2-3)

- [ ] Query timeout configuration
- [ ] Incremental search support
- [ ] Real-time progress updates (WebSocket)
- [ ] Manual deduplication review UI
- [ ] Result file compression
- [ ] Auto-cleanup policy

***

## Testing Checklist

### Before Committing

- [x] Stage 7 imports without errors
- [x] Registered in `StageOrchestrator`
- [x] `SearchResults` model added to `src/models.py`
- [x] `SearchService` backward compatible
- [x] Test suite created
- [ ] Tests pass with real API calls
- [ ] Integration test (Stages 0→7) passes
- [ ] Documentation updated

### Before Production

- [ ] Test with all supported databases
- [ ] Test graceful degradation (unsupported DBs)
- [ ] Test deduplication accuracy
- [ ] Test large result sets (500+ papers)
- [ ] Test concurrent project execution
- [ ] Verify file permissions/storage
- [ ] Add monitoring/logging

***

## Next Steps

### Immediate (Today)

1. **Run Integration Test**
   ```bash
   pytest tests/test_stage7_query_execution.py -v
   ```

2. **Test Full Pipeline**
   ```bash
   python -m src.cli run-pipeline "Systematic review of LLM hallucination"
   ```

3. **Verify Output**
   - Check `data/{project_id}/search_results/` directory
   - Load papers from JSON files
   - Verify deduplication stats

### Week 1 Remaining (Days 2-5)

- **Day 2:** Test Stage 7 with real queries, fix edge cases
- **Day 3:** Enhance Stage 5 (deterministic screening criteria)
- **Day 4-5:** Upgrade Stage 6 (multi-format export)

### Week 2 (Frontend Integration)

- Add `/api/projects/{id}/results` endpoint
- Display papers in React UI
- Export buttons (CSV, BibTeX, RIS)

***

## Success Criteria Met

✅ **Stage 7 Implementation Complete:**
- [x] Loads `DatabaseQueryPlan`
- [x] Executes queries via `SearchService`
- [x] Saves results to project-scoped files
- [x] Auto-deduplicates multi-database results
- [x] Returns lightweight metadata artifact
- [x] Handles unsupported databases gracefully
- [x] Provides user-friendly prompts
- [x] Registered in orchestrator
- [x] Test suite created

**Status:** ✅ **READY FOR TESTING**

The implementation follows all architectural decisions from the plan:
- File-pointer artifact pattern (no bloat)
- Project-scoped storage (backward compatible)
- Graceful degradation (warn, don't fail)
- Auto-deduplication (with opt-out)

***

**Estimated Completion:** Day 1 goals exceeded - full Stage 7 implementation delivered, not just skeleton. Ready to proceed with Stage 5 enhancement.

