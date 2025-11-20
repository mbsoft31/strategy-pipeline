# Sprint 4: SLR Integration Plan - Complete Implementation

**Goal**: Integrate existing SLR code to add query execution and result management  
**Timeline**: 3-5 days  
**Effort**: ~20 hours  
**Status**: Ready to implement  
**Date**: November 20, 2025

---

## Overview

This plan integrates the existing `slr` directory structure (located at `docs/next-steps/scratch_project/slr/`) into the strategy-pipeline project to implement **Option B: Add Critical Features**, specifically:

1. Query Execution (run searches from dashboard)
2. Result Preview (display papers with abstracts)
3. Deduplication (merge results across databases)
4. Export Formats (CSV, BibTeX, JSON)
5. Project Persistence (save/load workflows)

---

## What SLR Provides

### Existing Infrastructure Analysis

```
slr/
├── providers/              # 4 Database Connectors Ready
│   ├── arxiv.py           # arXiv API integration
│   ├── crossref.py        # CrossRef API integration
│   ├── openalex.py        # OpenAlex API integration (already used for validation!)
│   ├── s2.py              # Semantic Scholar API integration
│   ├── base.py            # Abstract base provider
│   ├── query_translator.py # Query syntax translation
│   └── normalizer.py      # Result normalization
│
├── dedup/                 # Deduplication Logic Ready
│   ├── deduplicator.py    # Main deduplication engine
│   └── strategies.py      # Similarity strategies (title, DOI, fingerprint)
│
├── export/                # 3 Export Formats Ready
│   ├── base.py            # Abstract exporter
│   ├── bibtex_exporter.py # .bib format for reference managers
│   ├── csv_exporter.py    # .csv for spreadsheets
│   └── jsonl_exporter.py  # .jsonl for data pipelines
│
├── normalization/         # Data Normalization Ready
│   └── __init__.py        # Paper model normalization
│
├── core/                  # Core Models Ready
│   ├── models.py          # Paper, SearchQuery, Author models
│   └── config.py          # Configuration management
│
├── utils/                 # Utilities Ready
│   ├── rate_limit.py      # API rate limiting
│   ├── retry.py           # Retry logic with exponential backoff
│   ├── exceptions.py      # Custom exceptions
│   ├── logging.py         # Logging setup
│   └── config.py          # Config utilities
│
└── cli/                   # CLI tools (we'll adapt for web UI)
    ├── search.py          # Search commands
    ├── deduplicate.py     # Dedup commands
    ├── export.py          # Export commands
    └── main.py            # CLI entry point
```

### Key Benefits

✅ **Proven Code** - Already tested and working  
✅ **4 Databases** - OpenAlex, arXiv, CrossRef, Semantic Scholar  
✅ **Smart Deduplication** - Multiple strategies (DOI, title similarity, fingerprint)  
✅ **Multiple Formats** - BibTeX, CSV, JSON exports  
✅ **Rate Limiting** - Built-in API protection  
✅ **Error Handling** - Retry logic and graceful failures  
✅ **Modular Design** - Easy to integrate and extend  

---

## Integration Architecture

### Current System
```
strategy-pipeline/
├── src/
│   ├── services/
│   │   ├── llm_provider.py          # OpenAI/Mock
│   │   ├── validation_service.py    # OpenAlex validation
│   │   └── intelligent_model_service.py
│   ├── search/
│   │   ├── dialects.py              # Syntax generation (6 databases)
│   │   └── builder.py               # Query builder
│   └── models.py                    # Artifacts
└── app.py                           # Streamlit UI (3 stages)
```

### New System (After Integration)
```
strategy-pipeline/
├── src/
│   ├── services/
│   │   ├── llm_provider.py          # Existing
│   │   ├── validation_service.py    # Existing
│   │   ├── intelligent_model_service.py # Existing
│   │   ├── search_service.py        # NEW: Unified search execution
│   │   └── project_service.py       # NEW: Save/load projects
│   │
│   ├── search/
│   │   ├── dialects.py              # Existing: Syntax generation
│   │   ├── builder.py               # Existing: Query builder
│   │   └── connectors.py            # NEW: Wrapper for SLR providers
│   │
│   ├── slr/                         # NEW: Copied from docs/next-steps
│   │   ├── providers/               # Database API connectors
│   │   ├── dedup/                   # Deduplication logic
│   │   ├── export/                  # Export formats
│   │   ├── normalization/           # Data normalization
│   │   ├── core/                    # Models and config
│   │   └── utils/                   # Utilities
│   │
│   ├── models.py                    # Existing: Artifacts
│   └── utils/
│       └── report_generator.py      # NEW: PDF report generation
│
└── app.py                           # Updated: 4 stages now
```

---

## Implementation Plan (REVISED)

### Strategic Improvements

**Key Changes from Original Plan:**
1. ✅ **Automated import fixes** - Script replaces manual file editing
2. ✅ **Acknowledge PubMed/Scopus gap** - UI shows "coming soon" for unavailable databases
3. ✅ **Day 2/3 swap** - Build persistence before UI to avoid data loss
4. ✅ **Reduced testing** - Focus on glue layer, not re-testing SLR internals
5. ✅ **Optimized state management** - Store metadata only, full results on disk

---

### Phase 1: The Merge (Backend) - Day 1 (3 hours)

#### Task 1.1: Copy SLR into Project (15 min)

**Action:**
```bash
# Navigate to project root
cd C:\Users\mouadh\Desktop\strategy-pipeline

# Copy slr directory AS-IS (preserve internal structure)
cp -r docs/next-steps/scratch_project/slr src/slr

# Verify structure
ls src/slr/
```

**Expected Output:**
```
src/slr/
├── __init__.py
├── providers/
├── dedup/
├── export/
├── normalization/
├── core/
├── utils/
└── cli/
```

**Important:** Do NOT manually edit any files yet. SLR is a "vendor library" - we'll fix imports automatically.

---

#### Task 1.2: Automated Import Fix Script (30 min)

**Critical Insight:** Manual import fixes are error-prone. Automate it!

**Create: `scripts/fix_slr_imports.py`**

```python
"""
Automated import fixer for SLR integration.
Replaces absolute imports from 'slr.' to 'src.slr.' across all SLR files.
"""
import re
from pathlib import Path

def fix_imports_in_file(filepath: Path) -> int:
    """Fix imports in a single Python file."""
    content = filepath.read_text(encoding='utf-8')
    original = content
    
    # Pattern 1: from slr.module import ...
    content = re.sub(
        r'\bfrom slr\.([a-zA-Z_][a-zA-Z0-9_\.]*)',
        r'from src.slr.\1',
        content
    )
    
    # Pattern 2: import slr.module
    content = re.sub(
        r'\bimport slr\.([a-zA-Z_][a-zA-Z0-9_\.]*)',
        r'import src.slr.\1',
        content
    )
    
    if content != original:
        filepath.write_text(content, encoding='utf-8')
        return 1
    return 0

def main():
    """Fix all Python files in src/slr/."""
    slr_dir = Path('src/slr')
    
    if not slr_dir.exists():
        print("❌ src/slr/ not found. Run Task 1.1 first.")
        return
    
    fixed_count = 0
    total_files = 0
    
    for py_file in slr_dir.rglob('*.py'):
        total_files += 1
        fixed_count += fix_imports_in_file(py_file)
    
    print(f"✅ Fixed imports in {fixed_count}/{total_files} files")
    print(f"📁 Checked: {slr_dir}")

if __name__ == '__main__':
    main()
```

**Action:**
```bash
# Create scripts directory
mkdir -p scripts

# Save the script above to scripts/fix_slr_imports.py

# Run it
python scripts/fix_slr_imports.py
```

**Expected Output:**
```
✅ Fixed imports in 15/45 files
📁 Checked: src/slr
```

**Note:** Relative imports (e.g., `from .base import`) are LEFT ALONE. They work correctly within the package structure.

---

#### Task 1.3: Update Dependencies (15 min)

**File: `requirements.txt`**

Add SLR dependencies at the end:

```txt
# Existing dependencies
Flask==3.0.0
Werkzeug==3.0.1
Jinja2==3.1.2

# Sprint 1: Configuration & Foundation
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Sprint 2: LLM Integration & Validation
openai>=1.3.0
requests>=2.31.0

# Sprint 3: Web UI
streamlit>=1.30.0

# Sprint 4: SLR Integration - NEW
httpx>=0.25.0              # HTTP client for async requests
ratelimit>=2.2.1           # Rate limiting decorator
tenacity>=8.2.3            # Retry logic with exponential backoff
bibtexparser>=1.4.0        # BibTeX parsing and writing
python-Levenshtein>=0.21.0 # String similarity for deduplication
reportlab>=4.0.0           # PDF generation (optional)
```

#### Task 1.3: Update Dependencies (15 min)

**File: `requirements.txt`**

Add SLR dependencies at the end:

```txt
# Sprint 4: SLR Integration - NEW
httpx>=0.25.0              # HTTP client for async requests
ratelimit>=2.2.1           # Rate limiting decorator
tenacity>=8.2.3            # Retry logic with exponential backoff
bibtexparser>=1.4.0        # BibTeX parsing and writing
python-Levenshtein>=0.21.0 # String similarity for deduplication
```

**Action:**
```bash
pip install -r requirements.txt
```

---

#### Task 1.4: Create Search Service Wrapper (2 hours)

**File: `src/services/search_service.py`**

Create unified interface to SLR providers (treat SLR as vendor library):

```python
"""
Unified search service - THE GLUE LAYER.
Wraps SLR providers without modifying them.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
import time
import logging

# Import from vendor library (SLR)
from src.slr.providers import (
    OpenAlexProvider,
    ArxivProvider,
    CrossRefProvider,
    SemanticScholarProvider
)
from src.slr.core.models import Paper
from src.slr.dedup.deduplicator import Deduplicator
from src.slr.export.csv_exporter import CSVExporter
from src.slr.export.bibtex_exporter import BibTeXExporter
from src.slr.export.jsonl_exporter import JSONLExporter

logger = logging.getLogger(__name__)


@dataclass
class SearchResultsSummary:
    """Lightweight summary for session state (NOT full papers)."""
    database: str
    query: str
    total_hits: int
    execution_time: float
    error: Optional[str] = None
    result_file: Optional[str] = None  # Path to saved results


class SearchService:
    """
    Execute searches across multiple databases using SLR providers.
    
    CRITICAL: This is the ADAPTER layer. Do NOT modify SLR code.
    """
    
    # Map our database names to SLR providers
    # NOTE: PubMed and Scopus are NOT here (no SLR connectors)
    PROVIDERS = {
        'openalex': OpenAlexProvider,
        'arxiv': ArxivProvider,
        'crossref': CrossRefProvider,
        'semanticscholar': SemanticScholarProvider,
        's2': SemanticScholarProvider,  # Alias
    }
    
    # Databases we generate syntax for but CAN'T execute yet
    SYNTAX_ONLY = {
        'pubmed': 'PubMed connector requires E-utilities auth. Use copy/paste for now.',
        'scopus': 'Scopus connector requires API key. Use copy/paste for now.'
    }
    
    def __init__(self, results_dir: str = "data/search_results"):
        self.deduplicator = Deduplicator()
        self._provider_instances = {}
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        logger.info("SearchService initialized (adapter layer)")
    
    def get_available_databases(self) -> List[str]:
        """Return databases we can actually execute (not just generate syntax for)."""
        return list(self.PROVIDERS.keys())
    
    def get_syntax_only_databases(self) -> Dict[str, str]:
        """Return databases we can't execute yet with reasons."""
        return self.SYNTAX_ONLY
        
    def _get_provider(self, database: str):
        """Get or create provider instance (cached)."""
        # ...existing logic from original plan...
        
    def execute_search(
        self, 
        database: str, 
        query: str, 
        max_results: int = 100,
        save_to_disk: bool = True
    ) -> SearchResultsSummary:
        """
        Execute search and return SUMMARY only (not full papers).
        Full results saved to disk to avoid bloating session state.
        """
        # ...existing execution logic...
        
        # Save results to disk immediately
        if save_to_disk and papers:
            result_file = self._save_results(database, papers)
        else:
            result_file = None
        
        # Return lightweight summary
        return SearchResultsSummary(
            database=database,
            query=query,
            total_hits=len(papers),
            execution_time=execution_time,
            result_file=result_file
        )
    
    def _save_results(self, database: str, papers: List[Paper]) -> str:
        """Save results to disk, return filepath."""
        from datetime import datetime
        import json
        
        filename = f"{database}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.results_dir / filename
        
        # Serialize papers
        data = [p.dict() for p in papers]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(papers)} results to {filepath}")
        return str(filepath)
    
    def load_results(self, result_file: str) -> List[Paper]:
        """Load results from disk."""
        import json
        from src.slr.core.models import Paper
        
        with open(result_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return [Paper(**p) for p in data]
```

**Key Improvements:**
1. ✅ Returns lightweight `SearchResultsSummary` (not full papers)
2. ✅ Saves results to disk immediately (avoids session state bloat)
3. ✅ Provides `get_available_databases()` and `get_syntax_only_databases()`
4. ✅ Treats SLR as vendor library (no modifications)

---

### Phase 2: The Memory (Persistence) - Day 2 (3 hours)

**Strategic Change:** Build persistence BEFORE UI so we don't lose search results on refresh.

#### Task 2.1: Create Project Service (2 hours)

**File: `src/services/search_service.py`**

Create unified interface to SLR providers:

```python
"""
Unified search service that wraps SLR providers.
Connects syntax generation with query execution.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import time
import logging

from src.slr.providers import (
    OpenAlexProvider,
    ArxivProvider,
    CrossRefProvider,
    SemanticScholarProvider
)
from src.slr.core.models import Paper
from src.slr.dedup.deduplicator import Deduplicator
from src.slr.export.csv_exporter import CSVExporter
from src.slr.export.bibtex_exporter import BibTeXExporter
from src.slr.export.jsonl_exporter import JSONLExporter

logger = logging.getLogger(__name__)


@dataclass
class SearchResults:
    """Unified search results from a single database."""
    database: str
    query: str
    total_hits: int
    papers: List[Paper]
    execution_time: float
    error: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'database': self.database,
            'query': self.query,
            'total_hits': self.total_hits,
            'papers': [p.dict() for p in self.papers] if self.papers else [],
            'execution_time': self.execution_time,
            'error': self.error
        }


class SearchService:
    """Execute searches across multiple databases using SLR providers."""
    
    # Map our database names to SLR providers
    PROVIDERS = {
        'openalex': OpenAlexProvider,
        'arxiv': ArxivProvider,
        'crossref': CrossRefProvider,
        'semanticscholar': SemanticScholarProvider,
        's2': SemanticScholarProvider,  # Alias
    }
    
    def __init__(self):
        self.deduplicator = Deduplicator()
        self._provider_instances = {}
        logger.info("SearchService initialized")
        
    def _get_provider(self, database: str):
        """Get or create provider instance (cached)."""
        database_lower = database.lower()
        
        if database_lower not in self._provider_instances:
            provider_class = self.PROVIDERS.get(database_lower)
            if not provider_class:
                raise ValueError(
                    f"Unknown database: {database}. "
                    f"Available: {', '.join(self.PROVIDERS.keys())}"
                )
            self._provider_instances[database_lower] = provider_class()
            logger.info(f"Created provider instance for {database}")
            
        return self._provider_instances[database_lower]
    
    def execute_search(
        self, 
        database: str, 
        query: str, 
        max_results: int = 100
    ) -> SearchResults:
        """
        Execute search on a single database.
        
        Args:
            database: Database name (openalex, arxiv, crossref, semanticscholar)
            query: Search query in database-specific syntax
            max_results: Maximum results to return
            
        Returns:
            SearchResults with papers and metadata
        """
        try:
            provider = self._get_provider(database)
            
            logger.info(f"Executing search on {database}: {query[:100]}...")
            start_time = time.time()
            
            # Execute search via SLR provider
            papers = provider.search(query, max_results=max_results)
            
            execution_time = time.time() - start_time
            
            logger.info(
                f"Search complete: {len(papers)} papers found in "
                f"{execution_time:.2f}s from {database}"
            )
            
            return SearchResults(
                database=database,
                query=query,
                total_hits=len(papers),
                papers=papers,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Search failed on {database}: {str(e)}", exc_info=True)
            return SearchResults(
                database=database,
                query=query,
                total_hits=0,
                papers=[],
                execution_time=0,
                error=str(e)
            )
    
    def multi_database_search(
        self, 
        queries: Dict[str, str], 
        max_results: int = 100
    ) -> Dict[str, SearchResults]:
        """
        Execute searches across multiple databases in parallel.
        
        Args:
            queries: Dict mapping database name to query string
            max_results: Maximum results per database
            
        Returns:
            Dict mapping database name to SearchResults
        """
        logger.info(f"Executing multi-database search across {len(queries)} databases")
        
        results = {}
        
        for database, query in queries.items():
            results[database] = self.execute_search(
                database, query, max_results
            )
        
        successful = sum(1 for r in results.values() if r.error is None)
        total_papers = sum(r.total_hits for r in results.values())
        
        logger.info(
            f"Multi-database search complete: {successful}/{len(queries)} "
            f"successful, {total_papers} total papers"
        )
        
        return results
    
    def deduplicate_results(
        self, 
        all_results: Dict[str, SearchResults]
    ) -> List[Paper]:
        """
        Combine and deduplicate papers from multiple databases.
        
        Uses SLR's smart deduplication strategies:
        - DOI matching
        - Title similarity (Levenshtein distance)
        - Author + year matching
        - Fingerprint matching
        
        Args:
            all_results: Results from multiple databases
            
        Returns:
            List of unique papers
        """
        # Collect all papers
        all_papers = []
        for result in all_results.values():
            if result.papers:
                all_papers.extend(result.papers)
        
        logger.info(f"Starting deduplication: {len(all_papers)} total papers")
        
        if not all_papers:
            return []
        
        # Deduplicate using SLR
        unique_papers = self.deduplicator.deduplicate(all_papers)
        
        duplicates_removed = len(all_papers) - len(unique_papers)
        logger.info(
            f"Deduplication complete: {len(unique_papers)} unique papers "
            f"({duplicates_removed} duplicates removed)"
        )
        
        return unique_papers
    
    def export_results(
        self, 
        papers: List[Paper], 
        format: str = 'csv'
    ) -> bytes:
        """
        Export results in specified format.
        
        Args:
            papers: List of papers to export
            format: Export format (csv, bibtex, json)
            
        Returns:
            Exported data as bytes
        """
        format_lower = format.lower()
        
        if format_lower == 'csv':
            exporter = CSVExporter()
        elif format_lower in ('bibtex', 'bib'):
            exporter = BibTeXExporter()
        elif format_lower in ('json', 'jsonl'):
            exporter = JSONLExporter()
        else:
            raise ValueError(
                f"Unknown format: {format}. "
                f"Supported: csv, bibtex, json"
            )
        
        logger.info(f"Exporting {len(papers)} papers as {format}")
        
        return exporter.export(papers)
    
    def get_statistics(self, results: Dict[str, SearchResults]) -> Dict:
        """
        Get statistics about search results.
        
        Args:
            results: Search results from multiple databases
            
        Returns:
            Dict with statistics
        """
        total_papers = sum(r.total_hits for r in results.values())
        successful_searches = sum(1 for r in results.values() if r.error is None)
        failed_searches = len(results) - successful_searches
        avg_time = (
            sum(r.execution_time for r in results.values()) / len(results)
            if results else 0
        )
        
        return {
            'total_papers': total_papers,
            'databases_searched': len(results),
            'successful_searches': successful_searches,
            'failed_searches': failed_searches,
            'average_response_time': avg_time,
            'fastest_database': min(
                results.items(), 
                key=lambda x: x[1].execution_time
            )[0] if results else None,
            'slowest_database': max(
                results.items(), 
                key=lambda x: x[1].execution_time
            )[0] if results else None
        }
```

**Verification:**
```python
# Test search service
from src.services.search_service import SearchService

service = SearchService()
results = service.execute_search(
    'openalex', 
    '"machine learning"', 
    max_results=5
)
print(f"✅ Found {results.total_hits} papers in {results.execution_time:.2f}s")
print(f"First paper: {results.papers[0].title if results.papers else 'None'}")
```

---

**File: `src/services/project_service.py`**

```python
"""
Project persistence service.
Saves complete workflows INCLUDING search results.
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging

from src.models import ProjectContext, ProblemFraming, ConceptModel

logger = logging.getLogger(__name__)


class ProjectService:
    """
    Manage project persistence to filesystem.
    
    IMPROVEMENT: Stores search result metadata, not full papers.
    Full results stay in data/search_results/.
    """
    
    PROJECTS_DIR = Path("data/projects")
    
    def __init__(self):
        self.PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"ProjectService initialized: {self.PROJECTS_DIR}")
    
    def save_project(
        self,
        project_id: str,
        context: ProjectContext,
        framing: Optional[ProblemFraming] = None,
        concepts: Optional[ConceptModel] = None,
        search_results_summary: Optional[Dict] = None  # Lightweight summaries only
    ) -> Path:
        """
        Save project with METADATA only.
        Full search results already saved to disk by SearchService.
        """
        project_data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "project_id": project_id,
            "context": context.model_dump() if context else None,
            "framing": framing.model_dump() if framing else None,
            "concepts": concepts.model_dump() if concepts else None,
            "search_results_summary": search_results_summary  # Just metadata!
        }
        
        filepath = self.PROJECTS_DIR / f"{project_id}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Project saved (metadata only): {filepath}")
        return filepath
    
    def load_project(self, project_id: str) -> Dict:
        """Load project metadata. Full results loaded on-demand."""
        # ...existing load logic...
        
    def list_projects(self) -> List[Dict]:
        """List all saved projects."""
        # ...existing list logic...
    
    def delete_project(self, project_id: str) -> bool:
        """Delete project and associated search results."""
        # ...existing delete logic...
```

**Key Improvements:**
1. ✅ Stores `search_results_summary` (lightweight) not full papers
2. ✅ Full results managed by `SearchService` in separate directory
3. ✅ Prevents session state bloat

---

#### Task 2.2: Add Save/Load to Dashboard (1 hour)

**File: `app.py` (sidebar section)**

Add project management EARLY in sidebar (before stage selection):

```python
# In sidebar, after provider info and before stage selection

st.divider()
st.subheader("💾 Project Management")

from src.services.project_service import ProjectService
if "project_service" not in st.session_state:
    st.session_state.project_service = ProjectService()

project_service = st.session_state.project_service

# Save current project
if st.session_state.get('context'):
    if st.button("💾 Save Project", use_container_width=True):
        try:
            filepath = project_service.save_project(
                project_id=st.session_state.context.id,
                context=st.session_state.context,
                framing=st.session_state.get('framing'),
                concepts=st.session_state.get('concepts'),
                search_results_summary=st.session_state.get('search_results_summary')  # Lightweight!
            )
            st.success(f"✅ Saved!")
        except Exception as e:
            st.error(f"❌ Save failed: {str(e)}")

# Load existing project
projects = project_service.list_projects()

if projects:
    st.markdown("**📁 Load Project:**")
    
    project_options = {
        f"{p['title']} ({p['saved_at'][:10]})": p['project_id'] 
        for p in projects
    }
    
    selected_project = st.selectbox(
        "Select",
        options=list(project_options.keys()),
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📂 Load", use_container_width=True):
            try:
                project_id = project_options[selected_project]
                data = project_service.load_project(project_id)
                
                # Restore session state
                st.session_state.context = data.get('context')
                st.session_state.framing = data.get('framing')
                st.session_state.concepts = data.get('concepts')
                st.session_state.search_results_summary = data.get('search_results_summary')
                
                st.success("✅ Loaded!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Load failed: {str(e)}")
    
    with col2:
        if st.button("🗑️", use_container_width=True, help="Delete project"):
            project_id = project_options[selected_project]
            if project_service.delete_project(project_id):
                st.success("Deleted")
                st.rerun()

st.divider()
```

**Why This Matters:** Users can now save/load BEFORE running expensive searches. No data loss on refresh!

---

### Phase 3: The Execution (UI) - Day 3 (4 hours)

**Strategic Change:** Now that persistence exists, we can build Stage 4 and auto-save results.

#### Task 3.1: Update Sidebar Navigation (5 min)

```python
step = st.radio("📍 Workflow Stage", [
    "1️⃣ Project Context", 
    "2️⃣ Problem Framing (AI Agent)", 
    "3️⃣ Search Strategy (Syntax)",
    "4️⃣ Execute Searches"  # NEW
], index=0)
```

---

#### Task 3.2: Add Stage 4 with Database Availability UI (3.5 hours)

**File: `app.py`**

Add new stage AFTER Stage 3:

```python
# --- STAGE 4: EXECUTE SEARCHES ---
elif step == "4️⃣ Execute Searches":
    st.header("4️⃣ Execute Searches & Get Results")
    
    if not st.session_state.concepts:
        st.warning("⚠️ Complete Stage 2 first")
    else:
        st.markdown("""
        ### 🔍 Run Searches Across Available Databases
        
        **What happens:**
        1. Select databases (4 available, 2 coming soon)
        2. Execute queries in parallel
        3. Results auto-saved to disk
        4. View/export results
        """)
        
        # Initialize search service
        from src.services.search_service import SearchService
        search_service = SearchService()
        
        # Build queries (reuse from Stage 3)
        from src.search.models import QueryPlan, ConceptBlock, FieldTag
        from src.search.builder import get_builder
        
        plan = QueryPlan()
        # ...build plan from concepts...
        
        # Generate queries for ALL databases (including unavailable)
        all_databases = ['openalex', 'arxiv', 'crossref', 'semanticscholar', 'pubmed', 'scopus']
        queries = {}
        
        for db in all_databases:
            try:
                builder = get_builder(db)
                queries[db] = builder.build(plan)
            except:
                pass
        
        # Separate available vs syntax-only
        available_dbs = search_service.get_available_databases()
        syntax_only_dbs = search_service.get_syntax_only_databases()
        
        # Configuration
        st.divider()
        st.subheader("⚙️ Configure Search")
        
        # CRITICAL: Show which databases are available
        st.markdown("**Available for Direct Execution:**")
        selected_dbs = st.multiselect(
            "Select databases",
            options=[db for db in queries.keys() if db in available_dbs],
            default=[db for db in queries.keys() if db in available_dbs][:2],
            help="These databases can be searched directly via API"
        )
        
        # Show syntax-only databases with tooltips
        if any(db in syntax_only_dbs for db in queries.keys()):
            st.markdown("**📋 Copy/Paste Required (Coming Soon):**")
            for db in queries.keys():
                if db in syntax_only_dbs:
                    with st.expander(f"🔒 {db.upper()} - {syntax_only_dbs[db]}"):
                        st.code(queries[db], language="text")
                        st.caption("💡 Use the copy button and paste into the database website")
        
        max_results = st.number_input(
            "📈 Max results per database",
            min_value=10,
            max_value=500,
            value=50,
            step=10
        )
        
        deduplicate = st.checkbox(
            "🔄 Deduplicate results",
            value=True,
            help="Remove duplicates using DOI + title similarity"
        )
        
        # Execute button
        st.divider()
        if st.button("▶️ Execute Searches", type="primary", use_container_width=True):
            if not selected_dbs:
                st.error("Select at least one database")
            else:
                selected_queries = {
                    db: query for db, query in queries.items() if db in selected_dbs
                }
                
                with st.status("🔍 Searching...", expanded=True) as status:
                    st.write(f"Querying {len(selected_dbs)} databases...")
                    
                    # Execute (results auto-saved to disk)
                    results = search_service.multi_database_search(
                        selected_queries, 
                        max_results=max_results,
                        save_to_disk=True  # CRITICAL: Don't bloat session state
                    )
                    
                    # Store SUMMARY only in session state
                    st.session_state.search_results_summary = {
                        db: {
                            'total_hits': r.total_hits,
                            'execution_time': r.execution_time,
                            'result_file': r.result_file,
                            'error': r.error
                        }
                        for db, r in results.items()
                    }
                    
                    # Deduplicate if requested
                    if deduplicate:
                        st.write("🔄 Deduplicating...")
                        # Load papers from disk for deduplication
                        all_papers = []
                        for r in results.values():
                            if r.result_file:
                                papers = search_service.load_results(r.result_file)
                                all_papers.extend(papers)
                        
                        unique_papers = search_service.deduplicator.deduplicate(all_papers)
                        
                        # Save deduplicated results
                        dedup_file = search_service._save_results('deduplicated', unique_papers)
                        st.session_state.dedup_result_file = dedup_file
                    
                    # Auto-save project with results
                    if st.session_state.get('context'):
                        project_service.save_project(
                            st.session_state.context.id,
                            st.session_state.context,
                            st.session_state.get('framing'),
                            st.session_state.get('concepts'),
                            st.session_state.search_results_summary
                        )
                        st.write("💾 Project auto-saved")
                    
                    status.update(
                        label=f"✅ Complete! Found {sum(r['total_hits'] for r in st.session_state.search_results_summary.values())} papers",
                        state="complete"
                    )
                    st.balloons()
        
        # Display results (load from disk on-demand)
        if st.session_state.get('search_results_summary'):
            st.divider()
            st.subheader("📊 Results")
            
            # Summary metrics
            summary = st.session_state.search_results_summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Papers", sum(r['total_hits'] for r in summary.values()))
            with col2:
                if st.session_state.get('dedup_result_file'):
                    dedup_papers = search_service.load_results(st.session_state.dedup_result_file)
                    st.metric("Unique Papers", len(dedup_papers))
            with col3:
                avg_time = sum(r['execution_time'] for r in summary.values()) / len(summary)
                st.metric("Avg Time", f"{avg_time:.2f}s")
            
            # Results tabs (load from disk when tab clicked)
            tabs = st.tabs([f"{db.upper()}" for db in selected_dbs])
            
            for tab, db in zip(tabs, selected_dbs):
                with tab:
                    result_info = summary[db]
                    
                    if result_info['error']:
                        st.error(f"❌ {result_info['error']}")
                    elif result_info['result_file']:
                        # Load papers from disk ONLY when this tab is viewed
                        papers = search_service.load_results(result_info['result_file'])
                        
                        st.success(f"✅ {len(papers)} papers in {result_info['execution_time']:.2f}s")
                        
                        # Display first 20
                        for i, paper in enumerate(papers[:20], 1):
                            with st.expander(f"{i}. {paper.title}"):
                                st.markdown(f"**Authors:** {', '.join(paper.authors[:3])}")
                                st.markdown(f"**Year:** {paper.year}")
                                if paper.abstract:
                                    st.markdown(f"**Abstract:** {paper.abstract[:300]}...")
                                if paper.url:
                                    st.link_button("🔗 Open", paper.url)
            
            # Export section
            st.divider()
            st.subheader("💾 Export")
            
            col1, col2, col3 = st.columns(3)
            
            # Load papers for export
            if st.session_state.get('dedup_result_file'):
                export_papers = search_service.load_results(st.session_state.dedup_result_file)
            else:
                export_papers = []
                for r in summary.values():
                    if r['result_file']:
                        export_papers.extend(search_service.load_results(r['result_file']))
            
            with col1:
                csv_data = search_service.export_results(export_papers, format='csv')
                st.download_button("📥 CSV", csv_data, file_name="results.csv", mime="text/csv")
            
            with col2:
                bib_data = search_service.export_results(export_papers, format='bibtex')
                st.download_button("📥 BibTeX", bib_data, file_name="results.bib")
            
            with col3:
                json_data = search_service.export_results(export_papers, format='json')
                st.download_button("📥 JSON", json_data, file_name="results.jsonl")
```

**Key Improvements:**
1. ✅ Shows available vs syntax-only databases with clear UI
2. ✅ Auto-saves project after search (no data loss on refresh)
3. ✅ Loads papers from disk on-demand (no session state bloat)
4. ✅ PubMed/Scopus shown as "coming soon" with copy/paste option

---

### Phase 4: The Polish (Exports & Cleanup) - Day 4 (2 hours)

**Strategic Change:** Reduced from 4 hours since we're not re-testing SLR internals.

#### Task 4.1: UI Polish (1 hour)

**Focus areas:**
1. ✅ Format result cards nicely (use `st.expander` for abstracts)
2. ✅ Add loading animations
3. ✅ Improve error messages
4. ✅ Add tooltips for all buttons

#### Task 4.2: Minimal Testing (1 hour)

**Test ONLY the glue layer (not SLR internals):**

**File: `tests/test_search_service_integration.py`**

```python
"""Test the ADAPTER layer only."""
import pytest
from src.services.search_service import SearchService

class TestSearchServiceIntegration:
    """Test our wrapper, not SLR internals."""
    
    def test_available_databases(self):
        """Test we correctly identify available databases."""
        service = SearchService()
        available = service.get_available_databases()
        
        assert 'openalex' in available
        assert 'arxiv' in available
        assert 'pubmed' not in available  # Should be syntax-only
    
    def test_syntax_only_databases(self):
        """Test we correctly identify syntax-only databases."""
        service = SearchService()
        syntax_only = service.get_syntax_only_databases()
        
        assert 'pubmed' in syntax_only
        assert 'scopus' in syntax_only
        assert 'openalex' not in syntax_only
    
    def test_search_saves_to_disk(self):
        """Test results are saved to disk, not kept in memory."""
        service = SearchService()
        
        result = service.execute_search('openalex', '"test"', max_results=5)
        
        # Should return summary, not full papers
        assert hasattr(result, 'result_file')
        assert result.result_file is not None
        
        # Should be able to load from disk
        papers = service.load_results(result.result_file)
        assert len(papers) > 0
```

**Note:** We do NOT test `OpenAlexProvider.search()` - that's SLR's job, already tested!

---

**File: `app.py`**

Update the sidebar radio to include Stage 4:

```python
# Update step selection in sidebar (around line 45)
step = st.radio("📍 Workflow Stage", [
    "1️⃣ Project Context", 
    "2️⃣ Problem Framing (AI Agent)", 
    "3️⃣ Search Strategy (Syntax)",
    "4️⃣ Execute Searches"  # NEW
], index=0)
```

---

#### Task 2.2: Add Stage 4 UI (3 hours)

**File: `app.py`**

Add new stage after Stage 3 (around line 300, after the Search Strategy section):

```python
# --- STAGE 4: EXECUTE SEARCHES (NEW) ---
elif step == "4️⃣ Execute Searches":
    st.header("4️⃣ Execute Searches & Get Results")
    st.markdown("### 🔍 Run Your Searches Across Multiple Databases")
    
    if not st.session_state.concepts:
        st.warning("⚠️ Please complete **Stage 2** (Problem Framing) first.")
        st.info("👈 Go to '2️⃣ Problem Framing' in the sidebar to generate concepts.")
    else:
        st.markdown("""
        Now we'll execute the validated queries and retrieve actual papers!
        
        **What happens:**
        1. ✅ Select databases to search
        2. ✅ Execute queries in parallel
        3. ✅ Display results with abstracts
        4. ✅ Deduplicate across databases
        5. ✅ Export in multiple formats (CSV, BibTeX, JSON)
        """)
        
        # Build queries from concepts (reuse logic from Stage 3)
        from src.search.models import QueryPlan, ConceptBlock, FieldTag
        from src.search.builder import get_builder
        
        plan = QueryPlan()
        grouped = {}
        
        for c in st.session_state.concepts.concepts:
            type_key = c.type if isinstance(c.type, str) else str(c.type)
            if type_key not in grouped:
                grouped[type_key] = ConceptBlock(type_key)
            grouped[type_key].add_term(c.label, FieldTag.KEYWORD)
        
        for block in grouped.values():
            plan.blocks.append(block)
        
        # Generate queries for available databases
        available_databases = ['openalex', 'arxiv', 'crossref', 'semanticscholar']
        queries = {}
        
        for db in available_databases:
            try:
                builder = get_builder(db)
                queries[db] = builder.build(plan)
            except:
                pass  # Skip if syntax generation fails
        
        # Save queries in session state
        st.session_state.queries = queries
        
        # Configuration section
        st.divider()
        st.subheader("⚙️ Configure Search")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_dbs = st.multiselect(
                "📊 Select databases to search",
                options=list(queries.keys()),
                default=list(queries.keys())[:2],  # Default: first 2
                help="Select which databases to query. More databases = more results but longer wait time."
            )
        
        with col2:
            max_results = st.number_input(
                "📈 Max results per database",
                min_value=10,
                max_value=500,
                value=50,
                step=10,
                help="Maximum number of papers to retrieve from each database"
            )
        
        deduplicate = st.checkbox(
            "🔄 Deduplicate results across databases",
            value=True,
            help="Remove duplicate papers found in multiple databases using smart matching (DOI, title similarity, etc.)"
        )
        
        # Show queries that will be executed
        with st.expander("📋 View Queries to be Executed"):
            for db in selected_dbs:
                st.markdown(f"**{db.upper()}:**")
                st.code(queries[db], language="text")
        
        # Execute button
        st.divider()
        if st.button("▶️ Execute Searches", type="primary", use_container_width=True):
            if not selected_dbs:
                st.error("⚠️ Please select at least one database")
            else:
                # Prepare queries
                selected_queries = {
                    db: query 
                    for db, query in queries.items() 
                    if db in selected_dbs
                }
                
                # Initialize search service
                from src.services.search_service import SearchService
                search_service = SearchService()
                
                # Execute with progress
                with st.status("🔍 Searching databases...", expanded=True) as status:
                    st.write(f"📡 Querying {len(selected_dbs)} databases...")
                    
                    # Execute searches
                    results = search_service.multi_database_search(
                        selected_queries, 
                        max_results=max_results
                    )
                    
                    st.session_state.search_results = results
                    
                    # Get statistics
                    stats = search_service.get_statistics(results)
                    
                    # Deduplicate if requested
                    if deduplicate:
                        st.write("🔄 Deduplicating results across databases...")
                        unique_papers = search_service.deduplicate_results(results)
                        st.session_state.unique_papers = unique_papers
                    else:
                        st.session_state.unique_papers = None
                    
                    status.update(
                        label=f"✅ Search complete! Found {stats['total_papers']} papers", 
                        state="complete"
                    )
                    
                    st.balloons()
        
        # Display results
        if st.session_state.get('search_results'):
            st.divider()
            st.subheader("📊 Search Results")
            
            from datetime import datetime
            
            # Get statistics
            from src.services.search_service import SearchService
            search_service = SearchService()
            stats = search_service.get_statistics(st.session_state.search_results)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📄 Total Papers", stats['total_papers'])
            with col2:
                if st.session_state.get('unique_papers'):
                    st.metric("✨ Unique Papers", len(st.session_state.unique_papers))
                else:
                    st.metric("✨ Unique Papers", "N/A")
            with col3:
                st.metric(
                    "✅ Successful", 
                    f"{stats['successful_searches']}/{stats['databases_searched']}"
                )
            with col4:
                st.metric(
                    "⏱️ Avg Time", 
                    f"{stats['average_response_time']:.2f}s"
                )
            
            # Results by database (tabs)
            st.divider()
            st.subheader("📑 Results by Database")
            
            tabs = st.tabs([f"🔍 {db.upper()}" for db in selected_dbs])
            
            for tab, db in zip(tabs, selected_dbs):
                with tab:
                    result = st.session_state.search_results[db]
                    
                    if result.error:
                        st.error(f"❌ Search failed: {result.error}")
                        st.info("💡 This might be due to API rate limits or network issues. Try again in a few moments.")
                        continue
                    
                    if result.total_hits > 0:
                        st.success(
                            f"✅ Found {result.total_hits} papers in "
                            f"{result.execution_time:.2f} seconds"
                        )
                        
                        # Display papers
                        st.markdown(f"**Showing first {min(20, len(result.papers))} results:**")
                        
                        for i, paper in enumerate(result.papers[:20], 1):
                            with st.expander(f"📄 {i}. {paper.title}"):
                                # Authors
                                if paper.authors:
                                    authors_display = ', '.join(paper.authors[:5])
                                    if len(paper.authors) > 5:
                                        authors_display += f" et al. ({len(paper.authors)} total)"
                                    st.markdown(f"**👥 Authors:** {authors_display}")
                                
                                # Metadata
                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    st.markdown(f"**📅 Year:** {paper.year or 'N/A'}")
                                with col_b:
                                    st.markdown(f"**📚 Source:** {paper.source or 'N/A'}")
                                with col_c:
                                    if hasattr(paper, 'cited_by_count') and paper.cited_by_count:
                                        st.markdown(f"**📊 Citations:** {paper.cited_by_count}")
                                
                                # Abstract
                                if paper.abstract:
                                    st.markdown("**📝 Abstract:**")
                                    abstract_text = paper.abstract[:500]
                                    if len(paper.abstract) > 500:
                                        abstract_text += "..."
                                    st.write(abstract_text)
                                
                                # Links
                                if paper.url:
                                    st.link_button("🔗 Open Paper", paper.url)
                                
                                # Citation info
                                if paper.doi:
                                    st.code(f"DOI: {paper.doi}", language="text")
                    else:
                        st.warning(f"⚠️ No results found for this database")
                        st.info("Try broadening your search terms or checking the query syntax.")
            
            # Export section
            st.divider()
            st.subheader("💾 Export Results")
            
            papers_to_export = (
                st.session_state.get('unique_papers') 
                if deduplicate and st.session_state.get('unique_papers')
                else [p for r in st.session_state.search_results.values() for p in r.papers]
            )
            
            st.info(f"📊 Ready to export {len(papers_to_export)} papers")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                try:
                    csv_data = search_service.export_results(papers_to_export, format='csv')
                    st.download_button(
                        "📥 Download CSV",
                        data=csv_data,
                        file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        help="Export as CSV for Excel/Google Sheets"
                    )
                except Exception as e:
                    st.error(f"CSV export failed: {str(e)}")
            
            with col2:
                try:
                    bibtex_data = search_service.export_results(papers_to_export, format='bibtex')
                    st.download_button(
                        "📥 Download BibTeX",
                        data=bibtex_data,
                        file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bib",
                        mime="text/plain",
                        use_container_width=True,
                        help="Export as BibTeX for Zotero/Mendeley/EndNote"
                    )
                except Exception as e:
                    st.error(f"BibTeX export failed: {str(e)}")
            
            with col3:
                try:
                    json_data = search_service.export_results(papers_to_export, format='json')
                    st.download_button(
                        "📥 Download JSON",
                        data=json_data,
                        file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl",
                        mime="application/json",
                        use_container_width=True,
                        help="Export as JSON for data processing"
                    )
                except Exception as e:
                    st.error(f"JSON export failed: {str(e)}")

else:
    st.info("👆 Complete previous stages first to enable search execution")
```

---

### Phase 3: Project Persistence (Day 3 - 4 hours)

#### Task 3.1: Create Project Service (2 hours)

**File: `src/services/project_service.py`**

```python
"""
Project persistence service.
Saves and loads complete research workflows.
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging

from src.models import ProjectContext, ProblemFraming, ConceptModel

logger = logging.getLogger(__name__)


class ProjectService:
    """Manage project persistence to filesystem."""
    
    PROJECTS_DIR = Path("data/projects")
    
    def __init__(self):
        # Ensure projects directory exists
        self.PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"ProjectService initialized: {self.PROJECTS_DIR}")
    
    def save_project(
        self,
        project_id: str,
        context: ProjectContext,
        framing: Optional[ProblemFraming] = None,
        concepts: Optional[ConceptModel] = None,
        search_results: Optional[Dict] = None
    ) -> Path:
        """
        Save project to filesystem.
        
        Args:
            project_id: Unique project identifier
            context: ProjectContext artifact
            framing: ProblemFraming artifact (optional)
            concepts: ConceptModel artifact (optional)
            search_results: Search results dict (optional)
            
        Returns:
            Path to saved project file
        """
        project_data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "project_id": project_id,
            "context": context.model_dump() if context else None,
            "framing": framing.model_dump() if framing else None,
            "concepts": concepts.model_dump() if concepts else None,
            "search_results": self._serialize_search_results(search_results) if search_results else None
        }
        
        filepath = self.PROJECTS_DIR / f"{project_id}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Project saved: {filepath}")
        return filepath
    
    def load_project(self, project_id: str) -> Dict:
        """
        Load project from filesystem.
        
        Args:
            project_id: Unique project identifier
            
        Returns:
            Dict with project data
        """
        filepath = self.PROJECTS_DIR / f"{project_id}.json"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Project not found: {project_id}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # Reconstruct artifacts
        if project_data.get('context'):
            project_data['context'] = ProjectContext(**project_data['context'])
        
        if project_data.get('framing'):
            project_data['framing'] = ProblemFraming(**project_data['framing'])
        
        if project_data.get('concepts'):
            project_data['concepts'] = ConceptModel(**project_data['concepts'])
        
        # Search results stay as dict (complex to deserialize)
        
        logger.info(f"Project loaded: {filepath}")
        return project_data
    
    def list_projects(self) -> List[Dict]:
        """
        List all saved projects.
        
        Returns:
            List of project metadata dicts
        """
        projects = []
        
        for filepath in self.PROJECTS_DIR.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                projects.append({
                    "project_id": data.get('project_id'),
                    "title": data.get('context', {}).get('title', 'Untitled'),
                    "saved_at": data.get('saved_at'),
                    "filepath": str(filepath)
                })
            except Exception as e:
                logger.error(f"Error loading project {filepath}: {e}")
        
        # Sort by saved_at descending (newest first)
        projects.sort(key=lambda x: x.get('saved_at', ''), reverse=True)
        
        logger.info(f"Listed {len(projects)} projects")
        return projects
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: Unique project identifier
            
        Returns:
            True if deleted, False if not found
        """
        filepath = self.PROJECTS_DIR / f"{project_id}.json"
        
        if filepath.exists():
            filepath.unlink()
            logger.info(f"Project deleted: {project_id}")
            return True
        
        logger.warning(f"Project not found for deletion: {project_id}")
        return False
    
    def _serialize_search_results(self, results: Dict) -> Dict:
        """Convert SearchResults objects to dicts for JSON."""
        serialized = {}
        for db, result in results.items():
            if hasattr(result, 'to_dict'):
                serialized[db] = result.to_dict()
            else:
                serialized[db] = str(result)  # Fallback
        return serialized
```

---

#### Task 3.2: Add Save/Load to Dashboard (2 hours)

**File: `app.py` (update sidebar section)**

Add project management to sidebar (around line 60, after provider info):

```python
# ... existing sidebar code ...

st.divider()
st.subheader("💾 Project Management")

# Initialize project service
from src.services.project_service import ProjectService
if "project_service" not in st.session_state:
    st.session_state.project_service = ProjectService()

project_service = st.session_state.project_service

# Save current project
if st.session_state.get('context'):
    project_name = st.text_input(
        "Project Name",
        value=st.session_state.context.title[:30] if st.session_state.context.title else "My Project",
        help="Enter a name for this project",
        key="project_name_input"
    )
    
    if st.button("💾 Save Project", use_container_width=True):
        try:
            filepath = project_service.save_project(
                project_id=st.session_state.context.id,
                context=st.session_state.context,
                framing=st.session_state.get('framing'),
                concepts=st.session_state.get('concepts'),
                search_results=st.session_state.get('search_results')
            )
            st.success(f"✅ Project saved successfully!")
            st.caption(f"Saved to: {filepath.name}")
        except Exception as e:
            st.error(f"❌ Save failed: {str(e)}")
            logger.error(f"Project save error: {e}", exc_info=True)

# Load existing project
st.divider()
projects = project_service.list_projects()

if projects:
    st.markdown("**📁 Load Project:**")
    
    project_options = {
        f"{p['title']} ({p['saved_at'][:10]})": p['project_id'] 
        for p in projects
    }
    
    if project_options:
        selected_project_name = st.selectbox(
            "Select project to load",
            options=list(project_options.keys()),
            label_visibility="collapsed",
            key="project_load_select"
        )
        
        col_load, col_delete = st.columns(2)
        
        with col_load:
            if st.button("📂 Load", use_container_width=True):
                try:
                    project_id = project_options[selected_project_name]
                    project_data = project_service.load_project(project_id)
                    
                    # Restore session state
                    st.session_state.context = project_data.get('context')
                    st.session_state.framing = project_data.get('framing')
                    st.session_state.concepts = project_data.get('concepts')
                    st.session_state.search_results = project_data.get('search_results')
                    
                    st.success(f"✅ Project loaded!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Load failed: {str(e)}")
                    logger.error(f"Project load error: {e}", exc_info=True)
        
        with col_delete:
            if st.button("🗑️ Delete", use_container_width=True):
                project_id = project_options[selected_project_name]
                if project_service.delete_project(project_id):
                    st.success("✅ Project deleted")
                    st.rerun()
                else:
                    st.error("❌ Delete failed")
else:
    st.info("📭 No saved projects yet")
    st.caption("Save your first project using the button above")
```

---

### Phase 4: Testing & Polish (Day 4 - 4 hours)

#### Task 4.1: Create Integration Tests (2 hours)

**File: `tests/test_search_service.py`**

```python
"""Tests for search service integration."""
import pytest
from src.services.search_service import SearchService, SearchResults


class TestSearchService:
    """Test search service functionality."""
    
    def test_initialization(self):
        """Test service initializes correctly."""
        service = SearchService()
        assert service is not None
        assert service.deduplicator is not None
        assert service._provider_instances == {}
    
    def test_openalex_search(self):
        """Test OpenAlex search integration."""
        service = SearchService()
        
        results = service.execute_search(
            'openalex',
            '"machine learning"',
            max_results=5
        )
        
        assert results.database == 'openalex'
        assert results.error is None
        assert results.total_hits > 0
        assert len(results.papers) > 0
        assert results.execution_time > 0
    
    def test_multi_database_search(self):
        """Test searching multiple databases."""
        service = SearchService()
        
        queries = {
            'openalex': '"deep learning"',
            'arxiv': 'all:"neural networks"'
        }
        
        results = service.multi_database_search(queries, max_results=5)
        
        assert len(results) == 2
        assert 'openalex' in results
        assert 'arxiv' in results
        
        # At least one should succeed
        successful = sum(1 for r in results.values() if r.error is None)
        assert successful >= 1
    
    def test_deduplication(self):
        """Test result deduplication."""
        service = SearchService()
        
        # Search same topic in multiple databases
        queries = {
            'openalex': '"covid-19"',
            'arxiv': 'all:"covid-19"'
        }
        
        results = service.multi_database_search(queries, max_results=10)
        unique_papers = service.deduplicate_results(results)
        
        total_papers = sum(r.total_hits for r in results.values())
        
        # Should have some papers
        assert len(unique_papers) > 0
        
        # Should not exceed total (duplicates removed)
        assert len(unique_papers) <= total_papers
    
    def test_export_csv(self):
        """Test CSV export."""
        service = SearchService()
        
        results = service.execute_search('openalex', '"test"', max_results=3)
        
        if results.papers:
            csv_data = service.export_results(results.papers, format='csv')
            
            assert csv_data is not None
            assert len(csv_data) > 0
            assert b'title' in csv_data.lower()  # Header should contain 'title'
    
    def test_get_statistics(self):
        """Test statistics generation."""
        service = SearchService()
        
        queries = {'openalex': '"test"'}
        results = service.multi_database_search(queries, max_results=5)
        
        stats = service.get_statistics(results)
        
        assert 'total_papers' in stats
        assert 'databases_searched' in stats
        assert 'successful_searches' in stats
        assert stats['databases_searched'] == 1
    
    def test_invalid_database(self):
        """Test handling of invalid database."""
        service = SearchService()
        
        with pytest.raises(ValueError):
            service.execute_search('invalid_db', 'query')
    
    def test_invalid_export_format(self):
        """Test handling of invalid export format."""
        service = SearchService()
        
        with pytest.raises(ValueError):
            service.export_results([], format='invalid_format')
```

**File: `tests/test_project_service.py`**

```python
"""Tests for project persistence."""
import pytest
from pathlib import Path
from src.services.project_service import ProjectService
from src.models import ProjectContext


class TestProjectService:
    """Test project save/load functionality."""
    
    def test_initialization(self):
        """Test service initializes and creates directory."""
        service = ProjectService()
        assert service.PROJECTS_DIR.exists()
        assert service.PROJECTS_DIR.is_dir()
    
    def test_save_and_load_project(self):
        """Test round-trip save/load."""
        service = ProjectService()
        
        # Create test context
        context = ProjectContext.create_empty("Test research idea")
        context.title = "Test Project"
        
        # Save
        filepath = service.save_project(
            project_id=context.id,
            context=context
        )
        
        assert filepath.exists()
        assert filepath.suffix == '.json'
        
        # Load
        loaded = service.load_project(context.id)
        
        assert loaded['project_id'] == context.id
        assert loaded['context'].title == "Test Project"
        assert loaded['context'].id == context.id
        
        # Cleanup
        service.delete_project(context.id)
    
    def test_list_projects(self):
        """Test listing projects."""
        service = ProjectService()
        
        # Create test project
        context = ProjectContext.create_empty("List test")
        service.save_project(context.id, context)
        
        # List projects
        projects = service.list_projects()
        
        assert isinstance(projects, list)
        assert len(projects) > 0
        
        # Find our project
        found = any(p['project_id'] == context.id for p in projects)
        assert found
        
        # Cleanup
        service.delete_project(context.id)
    
    def test_delete_project(self):
        """Test project deletion."""
        service = ProjectService()
        
        # Create and save
        context = ProjectContext.create_empty("Delete test")
        service.save_project(context.id, context)
        
        # Verify exists
        assert (service.PROJECTS_DIR / f"{context.id}.json").exists()
        
        # Delete
        result = service.delete_project(context.id)
        assert result is True
        
        # Verify deleted
        assert not (service.PROJECTS_DIR / f"{context.id}.json").exists()
    
    def test_delete_nonexistent_project(self):
        """Test deleting nonexistent project."""
        service = ProjectService()
        
        result = service.delete_project("nonexistent_id")
        assert result is False
    
    def test_load_nonexistent_project(self):
        """Test loading nonexistent project raises error."""
        service = ProjectService()
        
        with pytest.raises(FileNotFoundError):
            service.load_project("nonexistent_id")
```

---

#### Task 4.2: Update Documentation (1 hour)

Update the following files to reflect new features:

1. **SPRINT3_QUICKSTART.md** - Add Stage 4 usage instructions
2. **README_FULL.md** - Add search execution feature to feature list
3. **WHATS_NEXT.md** - Mark Option B as implemented

---

#### Task 4.3: Error Handling & Edge Cases (1 hour)

Add comprehensive error handling for:

- **API failures**: Network errors, timeout errors
- **Rate limiting**: Graceful handling of 429 errors
- **Empty results**: Clear messaging when no papers found
- **Invalid queries**: Syntax errors in queries
- **Export failures**: Handle missing data gracefully

---

### Phase 5: Deployment & Launch (Day 5 - 4 hours)

#### Task 5.1: Final Testing (1 hour)

**Checklist:**
- [ ] Test all 4 databases individually
- [ ] Test multi-database search
- [ ] Test deduplication
- [ ] Test all 3 export formats
- [ ] Test save/load projects
- [ ] Test error scenarios
- [ ] Performance test with 100+ results

---

#### Task 5.2: Update Deployment (1 hour)

1. **Update requirements.txt** - Ensure all SLR deps included
2. **Test locally** - `streamlit run app.py`
3. **Deploy to Streamlit Cloud** - Push to GitHub, redeploy
4. **Test production** - Verify all features work in cloud

---

#### Task 5.3: Create Demo Video (1.5 hours)

Record updated demo showing:
1. Context generation (existing)
2. Problem framing (existing)
3. Query generation (existing)
4. **Search execution** (NEW)
5. **Result viewing** (NEW)
6. **Deduplication** (NEW)
7. **Export** (NEW)

---

#### Task 5.4: Announce to Users (30 min)

1. Update README with new features
2. Post on social media
3. Email beta users
4. Collect feedback

---

## Implementation Checklist

### Pre-Implementation
- [ ] Read this entire plan
- [ ] Backup current working state: `git commit -am "Pre-SLR integration backup"`
- [ ] Create feature branch: `git checkout -b feature/slr-integration`
- [ ] Review SLR code structure in `docs/next-steps/scratch_project/slr/`

### Day 1: Setup & Integration
- [ ] Copy SLR to `src/slr/`
- [ ] Update requirements.txt with SLR dependencies
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Fix import paths in SLR modules
- [ ] Create `src/services/search_service.py`
- [ ] Test: Import SearchService successfully
- [ ] Test: Execute single search on OpenAlex
- [ ] Commit: `git commit -am "feat: Add SLR integration and search service"`

### Day 2: Dashboard Integration
- [ ] Update sidebar navigation with Stage 4
- [ ] Add Stage 4 UI to app.py
- [ ] Test: Stage 4 displays correctly
- [ ] Test: Can select databases
- [ ] Test: Search execution works
- [ ] Test: Results display correctly
- [ ] Test: Export buttons work
- [ ] Commit: `git commit -am "feat: Add Stage 4 search execution to dashboard"`

### Day 3: Project Persistence
- [ ] Create `src/services/project_service.py`
- [ ] Add project management to sidebar
- [ ] Test: Can save project
- [ ] Test: Can load project
- [ ] Test: Can list projects
- [ ] Test: Can delete project
- [ ] Test: Session state restored correctly after load
- [ ] Commit: `git commit -am "feat: Add project persistence service"`

### Day 4: Testing & Polish
- [ ] Write `tests/test_search_service.py`
- [ ] Write `tests/test_project_service.py`
- [ ] Run all tests: `pytest tests/`
- [ ] Fix failing tests
- [ ] Add error handling for API failures
- [ ] Add error handling for rate limits
- [ ] Test edge cases (empty results, invalid queries)
- [ ] Update documentation
- [ ] Commit: `git commit -am "test: Add comprehensive tests for SLR integration"`

### Day 5: Deploy & Launch
- [ ] Run full test suite one more time
- [ ] Test locally end-to-end
- [ ] Merge to dev: `git checkout dev && git merge feature/slr-integration`
- [ ] Push to GitHub: `git push origin dev`
- [ ] Deploy to Streamlit Cloud
- [ ] Test production deployment
- [ ] Record demo video
- [ ] Update README.md
- [ ] Announce to users
- [ ] Commit: `git commit -am "docs: Update documentation for Sprint 4 launch"`

---

## Success Criteria

### Functional Requirements
- [ ] ✅ Can search 4 databases (OpenAlex, arXiv, CrossRef, Semantic Scholar)
- [ ] ✅ Results display with titles, authors, years, abstracts
- [ ] ✅ Deduplication successfully removes duplicates
- [ ] ✅ Can export in 3 formats (CSV, BibTeX, JSON)
- [ ] ✅ Can save complete projects
- [ ] ✅ Can load and restore projects
- [ ] ✅ Can delete projects

### Performance Requirements
- [ ] ✅ Search completes in <10 seconds per database
- [ ] ✅ UI remains responsive during search
- [ ] ✅ Can handle 100+ results per database
- [ ] ✅ Deduplication completes in <5 seconds for 500 papers
- [ ] ✅ Export generates files in <3 seconds

### User Experience Requirements
- [ ] ✅ Clear progress indicators during search
- [ ] ✅ Helpful error messages for failures
- [ ] ✅ Intuitive database selection
- [ ] ✅ Easy export flow (one-click downloads)
- [ ] ✅ Simple project save/load
- [ ] ✅ Responsive layout works on different screen sizes

---

## Expected Outcome

### Before Sprint 4 (Current State)
```
User Input → AI Processing → Validated Queries → Copy to Clipboard
                                                   ↓
                                            [MANUAL PASTE TO DATABASES]
                                                   ↓
                                            [MANUAL RESULT COLLECTION]
                                                   ↓
                                            [MANUAL DEDUPLICATION]
                                                   ↓
                                            [MANUAL EXPORT]
```

**Time**: Several hours of manual work

### After Sprint 4 (With SLR Integration)
```
User Input → AI Processing → Validated Queries → AUTO-EXECUTE
                                                       ↓
                                                  View Results
                                                       ↓
                                                  AUTO-DEDUPLICATE
                                                       ↓
                                                  ONE-CLICK EXPORT
                                                       ↓
                                                  Bibliography Ready!
```

**Time**: 5 minutes automated workflow

### Value Proposition
**"From research idea to deduplicated bibliography in 5 minutes"**

---

## Risk Mitigation

### Potential Issues & Solutions

**Issue 1: SLR imports fail**
- Solution: Carefully update all import paths to use `src.slr.*`
- Fallback: Keep SLR in separate package if needed

**Issue 2: API rate limits hit**
- Solution: SLR already has rate limiting built-in
- Fallback: Add delays between requests, use retry logic

**Issue 3: Large result sets slow down UI**
- Solution: Limit initial display to 20 papers per database
- Fallback: Paginate results, lazy load on scroll

**Issue 4: Deduplication takes too long**
- Solution: SLR uses efficient algorithms, should be fast
- Fallback: Make deduplication optional, run in background

**Issue 5: Export fails for some formats**
- Solution: SLR has robust exporters, thoroughly tested
- Fallback: Graceful error messages, allow partial exports

---

## Timeline Summary

| Day | Phase | Hours | Key Deliverable |
|-----|-------|-------|-----------------|
| 1 | Setup & Integration | 4 | SLR integrated, SearchService working |
| 2 | Dashboard Integration | 4 | Stage 4 functional in UI |
| 3 | Project Persistence | 4 | Save/load projects working |
| 4 | Testing & Polish | 4 | All tests passing, bugs fixed |
| 5 | Deploy & Launch | 4 | Production deployment, demo video |

**Total: 20 hours over 5 days**

---

## Post-Implementation

### Immediate Next Steps (Week 1)
1. Monitor user feedback on new features
2. Fix any bugs reported by beta users
3. Optimize performance based on usage patterns
4. Add analytics to track feature usage

### Future Enhancements (Week 2-4)
1. Add more databases (PubMed via E-utilities, Scopus)
2. Advanced filters (date range, citation count, etc.)
3. Saved searches and alerts
4. Collaboration features (share projects)
5. Citation network visualization

---

## Resources

### Documentation References
- SLR provider code: `docs/next-steps/scratch_project/slr/providers/`
- Deduplication logic: `docs/next-steps/scratch_project/slr/dedup/`
- Export formats: `docs/next-steps/scratch_project/slr/export/`
- Core models: `docs/next-steps/scratch_project/slr/core/models.py`

### Testing Resources
- Existing SLR tests (if any) in SLR directory
- Strategy-pipeline existing tests: `tests/`
- Pytest documentation: https://docs.pytest.org

### Deployment Resources
- Streamlit deployment docs: https://docs.streamlit.io/streamlit-community-cloud
- Current deployment: DEPLOYMENT_GUIDE.md

---

## Support & Questions

### If You Get Stuck

1. **Check SLR code** - Review implementations in `src/slr/`
2. **Review existing tests** - See how SLR components are tested
3. **Test components individually** - Isolate the problem
4. **Use logging** - Enable debug logging to see what's happening
5. **Start simple** - Test with OpenAlex only first, then add others

### Testing Strategy

1. **Unit test** each component (SearchService, ProjectService)
2. **Integration test** with real APIs (use small result sets)
3. **End-to-end test** complete workflow in UI
4. **Performance test** with larger datasets (100+ results)
5. **Error test** API failures, invalid inputs, edge cases

---

## Revised Timeline & Strategic Summary

### Timeline Comparison

**Original Plan:**
- Day 1-5: 20 hours total
- Manual import fixes
- Full SLR testing
- Persistence after UI

**Revised Plan (Based on Strategic Critique):**
- Day 1-4: 12 hours total
- Automated import fixes
- Adapter testing only
- Persistence before UI

### Time Savings: 40%

| Day | Phase | Hours | Key Changes |
|-----|-------|-------|-------------|
| 1 | The Merge | 3 | ✅ Automated imports (not manual) |
| 2 | The Memory | 3 | ✅ Persistence FIRST (prevent data loss) |
| 3 | The Execution | 4 | ✅ Smart state (disk, not session) |
| 4 | The Polish | 2 | ✅ Adapter tests only (not SLR) |

**Total: 12 hours** (vs 20 hours original)

---

## Key Strategic Improvements

### 1. Import Path Automation ✅
**Problem:** Manual editing of 20+ files is error-prone  
**Solution:** `scripts/fix_slr_imports.py` - regex-based automation  
**Benefit:** Zero errors, 1-hour task → 10 minutes

### 2. Database Availability Transparency ✅
**Problem:** Users expect PubMed/Scopus execution after seeing syntax  
**Solution:** UI shows "Available" vs "Coming Soon" with clear messaging  
**Benefit:** No broken promises, better UX

### 3. State Management Optimization ✅
**Problem:** Large search results bloat session state  
**Solution:** Save full results to disk, store summaries only  
**Benefit:** Fast UI, no memory issues

### 4. Persistence-First Architecture ✅
**Problem:** Refreshing page loses search results  
**Solution:** Build ProjectService BEFORE Stage 4 UI  
**Benefit:** Auto-save on search completion, zero data loss

### 5. Testing Efficiency ✅
**Problem:** Re-testing already-tested SLR code wastes time  
**Solution:** Test adapter layer only (SearchService, ProjectService)  
**Benefit:** 4 hours → 1 hour, focus on glue code

---

## Success Criteria (REVISED)

### Must-Have (Sprint 4)
- [ ] ✅ Execute searches on 4 databases (OpenAlex, arXiv, CrossRef, S2)
- [ ] ✅ Results saved to disk (not session state)
- [ ] ✅ Auto-save project after search
- [ ] ✅ PubMed/Scopus shown as "coming soon" with copy/paste
- [ ] ✅ Export in 3 formats (CSV, BibTeX, JSON)
- [ ] ✅ No data loss on page refresh

### Nice-to-Have (Future)
- [ ] PubMed connector (requires E-utilities auth)
- [ ] Scopus connector (requires API key)
- [ ] Result pagination (for 500+ papers)
- [ ] Citation network viz

---

## Risk Mitigation (UPDATED)

### Risk 1: Import Path Issues
**Mitigation:** Automated script prevents human error  
**Fallback:** Keep SLR as separate package if needed

### Risk 2: Session State Bloat
**Mitigation:** Disk storage from Day 1  
**Fallback:** Already implemented!

### Risk 3: User Confusion (PubMed/Scopus)
**Mitigation:** Clear UI messaging "Coming Soon"  
**Fallback:** Provide copy/paste workflow

### Risk 4: Search Results Lost on Refresh
**Mitigation:** Auto-save after every search  
**Fallback:** ProjectService built Day 2

---

## Approval & Next Steps

### ✅ Plan Approved with Modifications

**Strategic Critiques Addressed:**
1. ✅ Import automation (not manual)
2. ✅ Database gap acknowledged in UI
3. ✅ Smart state management (disk storage)
4. ✅ Testing efficiency (adapter only)
5. ✅ Execution flow optimized (persistence first)

### Implementation Order

```
Day 1: Backend Merge
  ├─ Copy SLR (15 min)
  ├─ Auto-fix imports (10 min)
  ├─ Install deps (15 min)
  └─ Create SearchService (2 hours)

Day 2: Persistence Layer  ← SWAPPED FROM DAY 3
  ├─ Create ProjectService (2 hours)
  └─ Add Save/Load UI (1 hour)

Day 3: Execution UI  ← SWAPPED FROM DAY 2
  ├─ Add Stage 4 (3 hours)
  └─ Integrate auto-save (1 hour)

Day 4: Polish & Test
  ├─ UI improvements (1 hour)
  └─ Adapter tests (1 hour)
```

### Ready to Start?

```bash
# 1. Backup current state
git commit -am "Pre-SLR integration backup"

# 2. Create feature branch
git checkout -b feature/slr-integration

# 3. Start Day 1
cp -r docs/next-steps/scratch_project/slr src/slr
```

---

## Conclusion

This **REVISED** plan integrates SLR as a "vendor library" without modifying internals. By automating imports, optimizing state management, and building persistence first, we:

- ✅ **Save 40% time** (12 hours vs 20 hours)
- ✅ **Reduce risk** (automated imports, no manual errors)
- ✅ **Improve UX** (clear database availability, auto-save)
- ✅ **Focus testing** (adapter layer only, not re-testing SLR)

**Strategic Approach:** Treat SLR as a proven library. Build a clean adapter (`SearchService`). Don't touch the internals unless absolutely necessary.

**Timeline:** Achievable in 3-4 days with focused execution.

**The result**: A tool that takes researchers from raw idea to validated bibliography in 5 minutes instead of several hours.

**Ready to implement?** Start with Day 1 - The Merge! 🚀


