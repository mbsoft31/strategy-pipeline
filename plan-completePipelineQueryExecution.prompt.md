# Plan: Complete Pipeline with Query Execution & Production-Ready Export

**TL;DR:** With `SearchService` already implemented and handling SLR provider abstraction + file storage, Stage 7 becomes a clean integration layer. Load `DatabaseQueryPlan`, execute via `SearchService` (project-scoped), auto-deduplicate multi-database results, save lightweight `SearchResults` artifact pointing to JSON files. Stage 5 uses deterministic PICO extraction (no LLM), Stage 6 exports to `.bib`/`.ris`/`.nbib`/CSV formats. Graceful degradation for unsupported databases (warn, don't fail). TDD approach with end-to-end test validates Stages 0→7.

## Steps

### 1. Add `SearchResults` artifact to `src/models.py` with file-pointer pattern

Define dataclass with `project_id: str`, `total_results: int`, `deduplicated_count: int`, `databases_searched: List[str]`, `result_file_paths: List[str]` (relative paths to JSON files like `"project_123/search_results/arxiv_20251127.json"`), `deduplication_stats: Dict[str, int]` containing `{"original_count": N, "duplicates_removed": M}`, `execution_time_seconds: float`, standard artifact fields (`status`, `model_metadata`)

### 2. Modify `src/services/search_service.py` for project-scoped storage

Add `project_id: Optional[str] = None` parameter to `SearchService.__init__()`, update `_save_results()` to use `Path(base_dir) / project_id / "search_results"` when `project_id` provided (else use `base_dir / "search_results"` for backward compatibility), ensure `mkdir(parents=True, exist_ok=True)` creates project directories

### 3. Create `src/stages/query_execution.py` with graceful degradation

Load `DatabaseQueryPlan` artifact, instantiate `SearchService(base_dir=persistence_service.base_dir, project_id=project_id)`, iterate `query_plan.queries` calling `execute_search(query.database_name.lower(), query.boolean_query_string)`, collect warnings for unsupported databases (check against `SearchService.PROVIDERS.keys()`), if `auto_deduplicate=True` and multiple result files exist: load all papers via `load_results()`, deduplicate using `Deduplicator`, save merged file, return `SearchResults` artifact with aggregated stats, partial success handling (some databases failed = warnings in `StageResult.prompts`, all failed = validation errors)

### 4. Register Stage 7 in `src/orchestration/stage_orchestrator.py`

Import `QueryExecutionStage`, add `self.register_stage("query-execution", QueryExecutionStage)` to `_register_default_stages()` method after `database-query-plan` registration

### 5. Upgrade `src/stages/screening_criteria.py` with deterministic extraction

Replace placeholder logic with `_extract_pico_criteria()` helper extracting population from `ConceptModel` (filter `concept.type == "population"`), intervention/method concepts, outcomes from `ResearchQuestionSet`, build inclusion criteria via template concatenation (e.g., `f"Target population: {', '.join(population_labels)}"`), add PRISMA defaults ("Peer-reviewed publications", "Published in English", "Full-text available"), generate exclusion criteria ("Non-scholarly sources", "Duplicate publications", "Outside research scope")

### 6. Enhance `src/stages/strategy_export.py` with multi-format export

Add `_export_queries_bibtex()`, `_export_queries_ris()`, `_export_queries_nbib()` methods generating database-specific query formats, if `SearchResults` artifact exists: load papers from `result_file_paths`, export CSV with columns (title, authors, abstract, DOI, year, venue, citations) using `SearchService.load_results()`, save all exports to `data/{project_id}/export/` directory, update `StrategyExportBundle.exported_files` list with relative paths

### 7. Create TDD integration test `tests/test_full_pipeline_stages_0_to_7.py`

Initialize `PipelineController`, run `start_project()`, sequentially execute and approve stages 1-4 (problem-framing, research-questions, search-concept-expansion, database-query-plan), execute stage 7 (query-execution), assert `SearchResults` artifact exists with `total_results > 0`, verify all `result_file_paths` point to existing non-empty files, validate deduplication stats if multiple databases, load one result file to confirm paper structure (has title/abstract/DOI fields)

### 8. Add results API endpoints to `interfaces/web_app.py`

Implement `GET /api/projects/{id}/results?page=1&limit=50` loading `SearchResults` artifact, paginating through papers loaded from `result_file_paths` via `SearchService.load_results()`, `GET /api/projects/{id}/export/{format}` supporting `bibtex`/`csv`/`ris` formats, `GET /api/projects/{id}/stats` returning deduplication metrics and per-database counts

## Further Considerations

### 1. Query execution timeout handling

Individual database queries may hang (slow APIs, network issues)—should `SearchService.execute_search()` have configurable timeout (default 60s) with automatic skip + warning for long-running queries?

### 2. Result file retention policy

Projects accumulate JSON files in `data/{project_id}/search_results/`—should we implement auto-cleanup of intermediate files after deduplication (keep only `deduplicated_all.json` + original files deleted after 30 days)?

### 3. Incremental search support

If user approves Stage 7 results then adds new database to Stage 4 and re-runs Stage 7—should it skip already-executed databases or re-fetch everything (potential: add `executed_queries: List[str]` to `SearchResults` for incremental execution)?

## Implementation Timeline

### ✅ Day 1: SearchResults Model + Stage 7 Skeleton - COMPLETE

**Completed:**
- ✅ Added `SearchResults` dataclass to `src/models.py`
- ✅ Modified `SearchService.__init__()` to accept `project_id` parameter (backward compatible)
- ✅ Updated `SearchService` for project-scoped directories
- ✅ Created `src/stages/query_execution.py` with full implementation
- ✅ Implemented query loading from `DatabaseQueryPlan`
- ✅ Added `SearchService` integration (multi-query execution)
- ✅ Registered stage in `StageOrchestrator`
- ✅ Created integration test suite in `tests/test_stage7_query_execution.py`
- ✅ Added `save_deduplicated_results()` method to `SearchService`
- ✅ Implemented graceful degradation for unsupported databases
- ✅ Added auto-deduplication logic

**Status:** Stage 7 is fully implemented and ready for testing. All files created:
- `src/stages/query_execution.py` (283 lines)
- `src/models.py` (SearchResults artifact added)
- `src/services/search_service.py` (enhanced with deduplication)
- `src/orchestration/stage_orchestrator.py` (Stage 7 registered)
- `tests/test_stage7_query_execution.py` (comprehensive test suite)

**Next:** Test with real pipeline execution, then move to Stage 5 enhancement.

### Day 1: SearchResults Model + Stage 7 Skeleton (ORIGINAL PLAN)

**Morning (2-3 hours):**
- Add `SearchResults` dataclass to `src/models.py`
- Modify `SearchService.__init__()` to accept `project_id` parameter
- Update `SearchService._save_results()` for project-scoped directories
- Write failing test in `tests/test_stage7_query_execution.py`

**Afternoon (3-4 hours):**
- Create `src/stages/query_execution.py` skeleton
- Implement query loading from `DatabaseQueryPlan`
- Add basic `SearchService` integration (single query execution)
- Register stage in `StageOrchestrator`

**End of Day 1 Goal:** Basic Stage 7 executes one query, saves results, test passes for single-database scenario

### Day 2: Stage 7 Full Implementation

**Morning (2-3 hours):**
- Implement multi-query execution loop
- Add unsupported database warning handling
- Implement graceful degradation (partial success logic)
- Add execution time tracking

**Afternoon (3-4 hours):**
- Implement auto-deduplication for multi-database results
- Load papers from all result files
- Call `Deduplicator.deduplicate()`
- Save merged `deduplicated_all.json`
- Populate `deduplication_stats` in artifact

**End of Day 2 Goal:** Stage 7 fully functional, handles multiple databases, auto-deduplicates, test suite passes

### Day 3: Stage 5 Enhancement (Deterministic)

**Morning (2-3 hours):**
- Create `_extract_pico_criteria()` helper method
- Extract population concepts from `ConceptModel`
- Extract intervention/method concepts
- Extract outcomes from `ResearchQuestionSet`

**Afternoon (2-3 hours):**
- Build inclusion criteria via template logic
- Add PRISMA-aligned defaults
- Generate exclusion criteria
- Write tests for deterministic criteria generation

**End of Day 3 Goal:** Stage 5 generates professional screening criteria without LLM calls

### Day 4-5: Stage 6 Export Suite

**Day 4 Morning (3-4 hours):**
- Implement `_export_queries_bibtex()` method
- Implement `_export_queries_ris()` method  
- Implement `_export_queries_nbib()` method
- Generate PRISMA protocol Markdown from all artifacts

**Day 4 Afternoon (2-3 hours):**
- Implement `_export_results_csv()` method
- Load papers from `SearchResults.result_file_paths`
- Format CSV with all required columns
- Handle missing fields gracefully

**Day 5 (3-4 hours):**
- Create `data/{project_id}/export/` directory structure
- Bundle all export files
- Update `StrategyExportBundle` with file paths
- Write integration tests for export functionality

**End of Day 5 Goal:** Stage 6 generates publication-ready exports in multiple formats

### Week 2: Frontend Integration

**Day 1-2: Backend API Endpoints (6-8 hours total)**
- Implement `GET /api/projects/{id}/results` with pagination
- Implement `GET /api/projects/{id}/export/{format}` endpoints
- Implement `GET /api/projects/{id}/stats` for deduplication metrics
- Add error handling for missing artifacts
- Write API integration tests

**Day 3-5: Frontend Display (10-12 hours total)**
- Add "Results" tab to project detail view
- Display papers table with title, authors, abstract preview
- Add pagination controls
- Implement export buttons (CSV, BibTeX, RIS)
- Show deduplication statistics
- Add DOI/URL links to external sources

**End of Week 2 Goal:** Full pipeline visible in web UI, users can execute searches and download results

### Week 3: Polish & Beta Testing

**Day 1-2: Documentation (4-6 hours)**
- Update README with Stage 7 documentation
- Document export formats and file structure
- Create "Getting Started" tutorial
- Add troubleshooting guide for unsupported databases

**Day 3-5: Beta User Testing (8-10 hours)**
- Recruit 5-10 beta users from academic community
- Conduct moderated user testing sessions
- Log pain points and feature requests
- Fix critical bugs discovered during testing
- Prioritize feedback for next sprint

**End of Week 3 Goal:** 10 real users tested pipeline, feedback documented, roadmap defined

## Key Architectural Decisions

### 1. Use Existing SearchService (Don't Reinvent)

**Rationale:** `src/services/search_service.py` already exists and wraps SLR providers. Stage 7 should orchestrate this service, not bypass it.

**Pattern:**
```python
# Stage 7 calls existing service
search_service = SearchService(project_id=project_id)
result = search_service.execute_search(database, query)
```

### 2. File-Pointer Artifact Pattern (Avoid Bloat)

**Rationale:** Storing 500+ papers in `SearchResults` artifact would create 5-15MB JSON files, breaking persistence service memory model.

**Pattern:**
```python
@dataclass
class SearchResults:
    result_file_paths: List[str]  # ✅ Pointers to files
    # NOT: papers: List[Document]  # ❌ Would bloat artifact
```

### 3. Graceful Degradation (Warn, Don't Fail)

**Rationale:** User selects 4 databases, only 2 are supported. Return partial results with warnings rather than complete failure.

**Pattern:**
```python
executed = []
warnings = []
for query in queries:
    if database not in SUPPORTED:
        warnings.append(f"Database {database} not yet supported")
        continue
    executed.append(execute_search(...))

if not executed:
    return StageResult(validation_errors=warnings)  # Total failure
else:
    return StageResult(artifact=..., prompts=warnings)  # Partial success
```

### 4. Auto-Deduplicate by Default (Manual Review Later)

**Rationale:** Deduplication is deterministic (DOI matching, title similarity). Auto-run in Stage 7, add manual review UI in Week 3 if users request it.

**Pattern:**
```python
def execute(self, *, project_id: str, auto_deduplicate: bool = True):
    if auto_deduplicate and len(results) > 1:
        deduplicated = deduplicator.deduplicate(all_papers)
        # Save merged file
```

### 5. Deterministic Stage 5 (No LLM Overhead)

**Rationale:** Screening criteria generation is template-based extraction from PICO elements, not creative task requiring LLM.

**Pattern:**
```python
def _extract_pico_criteria(self, concept_model, rq_set):
    population = [c.label for c in concepts if c.type == "population"]
    inclusion = [f"Target population: {', '.join(population)}"]
    # Template-based, fast, predictable
```

### 6. Project-Scoped Storage (Backward Compatible)

**Rationale:** Multiple projects sharing `data/search_results/` causes collision risk. Scope to project while maintaining backward compatibility.

**Pattern:**
```python
class SearchService:
    def __init__(self, project_id: Optional[str] = None):
        if project_id:
            self.results_dir = base_dir / project_id / "search_results"
        else:
            self.results_dir = base_dir / "search_results"  # Legacy
```

## Testing Strategy

### Unit Tests

**`tests/test_stage7_execution.py`:**
- Test query loading from `DatabaseQueryPlan`
- Test unsupported database warning generation
- Test result file path generation
- Test deduplication stats calculation
- Test partial success handling

**`tests/test_screening_criteria_deterministic.py`:**
- Test PICO extraction from `ConceptModel`
- Test inclusion criteria generation
- Test PRISMA defaults inclusion
- Test exclusion criteria generation

**`tests/test_strategy_export_formats.py`:**
- Test BibTeX export format validity
- Test RIS export format validity
- Test NBIB export format validity
- Test CSV column structure

### Integration Tests

**`tests/test_full_pipeline_stages_0_to_7.py`:**
```python
def test_full_pipeline_stages_0_to_7():
    controller = PipelineController(...)
    
    # Stage 0
    ctx_result = controller.start_project("LLM hallucination mitigation")
    project_id = ctx_result.draft_artifact.id
    controller.approve_artifact(project_id, "ProjectContext")
    
    # Stages 1-4 (abbreviated)
    for stage in ["problem-framing", "research-questions", 
                  "search-concept-expansion", "database-query-plan"]:
        result = controller.run_stage(stage, project_id=project_id)
        assert result.validation_errors == []
        controller.approve_artifact(project_id, result.draft_artifact.__class__.__name__)
    
    # Stage 7: Execute queries
    exec_result = controller.run_stage("query-execution", project_id=project_id)
    
    # Assertions
    assert exec_result.validation_errors == []
    search_results = exec_result.draft_artifact
    assert isinstance(search_results, SearchResults)
    assert search_results.total_results > 0
    assert len(search_results.result_file_paths) > 0
    
    # Verify files exist
    for path_str in search_results.result_file_paths:
        path = Path(path_str)
        assert path.exists()
        assert path.stat().st_size > 0
    
    # Verify deduplication
    if len(search_results.databases_searched) > 1:
        assert search_results.deduplication_stats["duplicates_removed"] >= 0
        assert "deduplicated_all.json" in str(search_results.result_file_paths[-1])
```

### API Tests

**`tests/test_api_results_endpoints.py`:**
- Test `GET /api/projects/{id}/results` returns papers
- Test pagination (page=1, page=2 different results)
- Test export endpoints return valid files
- Test stats endpoint returns deduplication metrics

## Success Criteria

### Week 1 Complete When:
- ✅ Stage 7 executes queries across multiple databases
- ✅ Results saved to project-scoped directories
- ✅ Auto-deduplication removes duplicates
- ✅ Unsupported databases generate warnings (not errors)
- ✅ Stage 5 generates PRISMA-aligned criteria
- ✅ Stage 6 exports to BibTeX/RIS/NBIB/CSV
- ✅ Integration test passes (Stages 0→7)

### Week 2 Complete When:
- ✅ API endpoints return search results
- ✅ Frontend displays papers in table
- ✅ Export buttons download files
- ✅ Deduplication stats visible in UI
- ✅ Live demo shows end-to-end workflow

### Week 3 Complete When:
- ✅ 10 beta users tested pipeline
- ✅ Feedback documented in issues
- ✅ Critical bugs fixed
- ✅ Documentation updated
- ✅ Roadmap for next sprint defined

## Risk Mitigation

### Risk 1: SearchService API Changes Needed

**Mitigation:** Modify `SearchService` to accept `project_id` as optional parameter, maintaining backward compatibility. Existing code without `project_id` continues working.

### Risk 2: Deduplication Performance on Large Result Sets

**Mitigation:** `Deduplicator` already handles 1000+ papers efficiently (tested in SLR module). If performance issues arise, add progress callback for UI feedback.

### Risk 3: Unsupported Database Handling Confuses Users

**Mitigation:** Clear warning messages explaining which databases need setup: "PubMed requires E-utilities authentication. See docs/setup-pubmed.md"

### Risk 4: Export Format Validation

**Mitigation:** Use existing export implementations from `src/slr/export/` module. BibTeX/CSV exporters already tested. Only need query-format exporters (RIS/NBIB) which are template-based.

### Risk 5: File Storage Growth

**Mitigation:** Document expected storage (100 papers ≈ 200KB). Add cleanup utility in Week 3 if users report disk issues. Consider compression for archived projects.

## Post-Week 3 Enhancements (Deferred)

### Quick Mode Implementation
- Skip PICO framing (Stages 1-2)
- Run minimal workflow: Stage 0 → 3 → 4 → 7
- For users who just want papers, not formal SLR protocol
- **Defer until users request simplified workflow**

### Manual Deduplication Review UI
- Show side-by-side comparison of duplicates
- Let users choose which version to keep
- Add "Mark as not duplicate" override
- **Defer until users report auto-dedup accuracy issues**

### Incremental Search Support
- Track executed queries in `SearchResults`
- Skip already-executed databases on re-run
- Merge new results with existing
- **Defer until users report re-execution pain**

### Advanced Export Options
- PDF protocol generation (using reportlab/weasyprint)
- PRISMA flowchart generation (using matplotlib/graphviz)
- Word document export (.docx)
- **Defer until users request specific formats**

### Query Execution Monitoring
- Real-time progress updates via WebSocket
- Cancel long-running queries
- Retry failed queries individually
- **Defer until users report timeout issues**

