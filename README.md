# Strategy Pipeline 🚀

<!-- Badges -->
<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10+-blue" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green" />
  <img alt="Status" src="https://img.shields.io/badge/Stages_Complete-8/8-brightgreen" />
  <img alt="Anti-Hallucination" src="https://img.shields.io/badge/Anti--Hallucination-Enabled-purple" />
  <img alt="Tests" src="https://img.shields.io/badge/Tests-Passing-success" />
  <img alt="Documentation" src="https://img.shields.io/badge/Docs-MkDocs-blue" />
</p>

> **TL;DR**: Production-ready systematic literature review pipeline that transforms a raw research idea into **validated, executable search queries + retrieved papers + PRISMA-compliant protocols**—with LLM assistance that never hallucinates invalid syntax, thanks to our Anti-Hallucination query engine.

---

## 🎉 **NEW: Complete End-to-End Pipeline (Nov 27, 2025)**

✨ **Major Update:** All 8 pipeline stages now operational!

- ✅ **Stage 7: Query Execution** - Live database searches (arXiv, OpenAlex, Crossref, Semantic Scholar)
- ✅ **Stage 6: Multi-Format Export** - CSV, BibTeX, RIS exports + PRISMA protocols
- ✅ **Stage 5: Screening Criteria** - Deterministic PICO-based inclusion/exclusion criteria
- ✅ **Auto-Deduplication** - DOI and title-based deduplication across databases
- ✅ **Production-Ready Documentation** - MkDocs with auto-generated API reference

**You can now go from research question → 300+ retrieved papers → ready-to-screen exports in ~5 minutes!**

---

## 🚀 Elevator Pitch

LLMs are great at brainstorming but unreliable at constructing professional literature search strategies. They hallucinate operators, misuse field tags, and produce non-reproducible outputs. **Strategy Pipeline** fixes that: it blends *expert-like LLM assistance* with *deterministic, validated Boolean query generation*, *live database execution*, and *multi-format export* across multiple scholarly databases—giving researchers a transparent, auditable, and refinable end-to-end workflow.

> Think of it as **"Git for your search strategy"** meets **"Rust-like guarantees for query correctness"** with **"One-click paper retrieval and export"**.

---

## 🧠 Who Is It For?

| User Type | Benefit |
|----------|---------|
| **Academic Researcher** | Complete systematic review workflow (PRISMA-compliant) |
| **PhD Student** | Automated literature search + citation export for dissertation |
| **Research Librarian** | Validated multi-database queries + professional protocols |
| **Meta-Analyst** | Rapid paper retrieval + screening preparation |
| **R&D Team** | Systematic landscape scanning with reproducible artifacts |

### 🔬 Common Use Cases

- Building a **complete systematic review** (search strategy → papers → screening)
- Mapping **emerging AI methods** with validated queries
- Generating **PICO-aligned research questions** + screening criteria
- Exporting papers to **Zotero/Mendeley/EndNote** in one click
- Creating **reproducible, PRISMA-compliant protocols**

---

## ✨ Why This Project

Traditional approaches have critical gaps:

**Manual Systematic Reviews:**
- ❌ Time-consuming query construction
- ❌ Error-prone Boolean syntax
- ❌ Inconsistent across databases
- ❌ Hard to reproduce

**Generic LLM Prompting:**
- ❌ Hallucinated operators (NEAR, ADJ, PROX)
- ❌ Invalid field tags
- ❌ No validation or execution
- ❌ No paper retrieval

**Strategy Pipeline Solutions:**
- ✅ **Anti-Hallucination Engine** - Guaranteed valid Boolean queries
- ✅ **Live Database Execution** - Retrieve papers from 4 databases
- ✅ **Auto-Deduplication** - DOI + title matching across sources
- ✅ **Multi-Format Export** - CSV, BibTeX, RIS for citation managers
- ✅ **PRISMA Compliance** - Professional protocol generation
- ✅ **Human-in-the-Loop** - Review and approve at every stage
- ✅ **Full Reproducibility** - All artifacts versioned and auditable

---

## 🔐 Anti-Hallucination Query Engine

**Three-tier safety net:**

1. **LLM Generation** - Research librarian persona generates candidate queries
2. **Syntax Validation** - Scans for hallucinated operators and invalid field tags
3. **Deterministic Builder** - Fallback to guaranteed executable Boolean queries

**Result:** 100% valid Boolean syntax for all supported databases.

**Supported Databases:**
- ✅ **PubMed** - Medical literature (`[Title/Abstract]` fields)
- ✅ **Scopus** - Multi-disciplinary (`TITLE-ABS-KEY()` operators)
- ✅ **arXiv** - Preprints (live execution)
- ✅ **OpenAlex** - Open scholarly data (live execution)
- ✅ **Crossref** - DOI registry (live execution)
- ✅ **Semantic Scholar** - AI-powered search (live execution)
- ✅ **Web of Science** - Citation database (syntax generation)

---

## 🧱 Complete Pipeline Stages (8/8 ✅)

| Stage | Name | Status | Summary |
|-------|------|--------|---------|
| **0** | Project Setup | ✅ Complete | Initialize `ProjectContext` from raw research idea |
| **1** | Problem Framing | ✅ Complete | PICO extraction + feasibility analysis |
| **2** | Research Questions | ✅ Complete | Generate structured research questions |
| **3** | Concept Expansion | ✅ Complete | MeSH/synonym expansion for search terms |
| **4** | Database Query Plan | ✅ Complete | Anti-hallucination validated Boolean queries |
| **5** | Screening Criteria | ✅ **NEW** | Deterministic PICO-based inclusion/exclusion |
| **6** | Strategy Export | ✅ **NEW** | Multi-format export (CSV/BibTeX/RIS/PRISMA) |
| **7** | Query Execution | ✅ **NEW** | Live database search + auto-deduplication |

**Status:** Production-ready, end-to-end workflow operational.

---

## 🎯 What You Get

### Input
```
"I want to review LLM hallucination mitigation techniques"
```

### Output (in ~5 minutes)
```
data/project_20251127_143022/
├── Artifacts/
│   ├── ProjectContext.json
│   ├── ProblemFraming.json
│   ├── ConceptModel.json
│   ├── ResearchQuestionSet.json
│   ├── SearchConceptBlocks.json
│   ├── DatabaseQueryPlan.json
│   ├── ScreeningCriteria.json
│   ├── SearchResults.json
│   └── StrategyExportBundle.json
├── search_results/
│   ├── arxiv_results.json (147 papers)
│   ├── openalex_results.json (189 papers)
│   ├── crossref_results.json (105 papers)
│   └── deduplicated_all.json (295 papers)
└── export/
    ├── papers.csv              # Excel-ready screening
    ├── papers.bib              # Zotero/Mendeley import
    ├── papers.ris              # EndNote import
    ├── STRATEGY_PROTOCOL.md    # PRISMA-compliant protocol
    └── queries/
        ├── openalex_query.txt
        ├── arxiv_query.txt
        ├── pubmed_query.txt
        └── scopus_query.txt
```

**Ready for:**
- ✅ Title/abstract screening in Excel
- ✅ Import into Zotero/Mendeley/EndNote
- ✅ PRISMA protocol submission
- ✅ Reproducible research workflow

---

## ⚡ Quick Start (5 Minutes)

### 1. Installation

```bash
# Clone repository
git clone https://github.com/mbsoft31/strategy-pipeline.git
cd strategy-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file:

```env
# Required: Choose one LLM provider
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Email for database APIs
SLR_MAILTO=your.email@example.com
```

### 3. Run Complete Pipeline

```python
from src.controller import PipelineController
from src.services import IntelligentModelService, FilePersistenceService

# Initialize
controller = PipelineController(
    IntelligentModelService(),
    FilePersistenceService(base_dir="./data")
)

# Start project (Stage 0)
result = controller.start_project(
    "Systematic review of LLM hallucination mitigation techniques"
)
project_id = result.draft_artifact.id

# Run all stages
stages = [
    "problem-framing",
    "research-questions",
    "search-concept-expansion",
    "database-query-plan",
    "screening-criteria",
    "query-execution",
    "strategy-export"
]

for stage in stages:
    result = controller.run_stage(stage, project_id=project_id)
    controller.approve_artifact(project_id, result.draft_artifact.__class__.__name__)

# Access results
print(f"✅ Complete! Check: data/{project_id}/export/")
```

**See:** [Quick Start Guide](https://mbsoft31.github.io/strategy-pipeline/getting-started/quick-start/) for detailed tutorial.

---

## 🧩 Core Features

### Backend Features
- ✅ **8-Stage Pipeline** - Complete workflow from idea to papers
- ✅ **Anti-Hallucination Engine** - Guaranteed valid Boolean queries
- ✅ **Live Database Search** - arXiv, OpenAlex, Crossref, Semantic Scholar
- ✅ **Auto-Deduplication** - DOI + title similarity matching
- ✅ **Multi-Format Export** - CSV, BibTeX, RIS
- ✅ **PRISMA Compliance** - Professional protocol generation
- ✅ **Human-in-the-Loop** - Approve/edit at every stage
- ✅ **Reproducible Artifacts** - JSON snapshots for audit trails
- ✅ **Complexity Analysis** - Query broadness/narrowness guidance
- ✅ **Graceful Degradation** - Automatic fallbacks ensure outputs

### Documentation Features
- ✅ **Professional Documentation** - MkDocs Material theme
- ✅ **Auto-Generated API Docs** - Always up-to-date from docstrings
- ✅ **Comprehensive Guides** - Getting started, user guide, architecture
- ✅ **Code Examples** - Real working examples
- ✅ **Testing Guide** - Full testing documentation
- ✅ **Contributing Guide** - Developer-friendly onboarding

---

## 🏗 Architecture

```
┌─────────────────┐
│  User Input     │
│  (Research Q)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PipelineController │ ◄── Facade Pattern
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ StageOrchestrator│ ◄── Stages 0-7
└────────┬────────┘
         │
    ┌────┴────┬────────┬──────────┐
    ▼         ▼        ▼          ▼
┌────────┐ ┌────┐ ┌────────┐ ┌────────┐
│LLM Svc │ │Persist│ │Search  │ │Syntax  │
│        │ │Svc    │ │Service │ │Engine  │
└────────┘ └────┘ └────────┘ └────────┘
                      │
                      ▼
              ┌───────────────┐
              │ 4 Databases   │
              │ (arXiv, etc.) │
              └───────────────┘
                      │
                      ▼
              ┌───────────────┐
              │ Deduplication │
              └───────────────┘
                      │
                      ▼
              ┌───────────────┐
              │ Multi-Format  │
              │ Export        │
              └───────────────┘
```

**See:** [Architecture Overview](https://mbsoft31.github.io/strategy-pipeline/architecture/overview/)

---

## 📚 Documentation

### Online Documentation (MkDocs)

**Deploy:** `mkdocs gh-deploy`  
**Live at:** https://mbsoft31.github.io/strategy-pipeline

**Structure:**
- 📖 [Getting Started](https://mbsoft31.github.io/strategy-pipeline/getting-started/) - Installation, quick start, configuration
- 📘 [User Guide](https://mbsoft31.github.io/strategy-pipeline/user-guide/) - Comprehensive reference
- 🏗️ [Architecture](https://mbsoft31.github.io/strategy-pipeline/architecture/) - System design
- 🔌 [API Reference](https://mbsoft31.github.io/strategy-pipeline/api-reference/) - Auto-generated from code
- 💻 [Development](https://mbsoft31.github.io/strategy-pipeline/development/) - Contributing, testing

### Quick Links

- **Installation:** [docs/getting-started/installation.md](docs/getting-started/installation.md)
- **Quick Start:** [docs/getting-started/quick-start.md](docs/getting-started/quick-start.md)
- **Configuration:** [docs/getting-started/configuration.md](docs/getting-started/configuration.md)
- **API Reference:** [docs/api-reference/](docs/api-reference/)
- **Contributing:** [docs/development/contributing.md](docs/development/contributing.md)
- **Testing:** [docs/development/testing.md](docs/development/testing.md)

---

## 🖥 Web Interface

```bash
# Start web server
python interfaces/web_app.py

# Visit http://localhost:5000
```

**Features:**
- Real-time stage progression
- Draft editing interface
- Approval workflow
- Visual artifact display
- Export downloads

**See:** [docs/architecture/frontend.md](docs/architecture/frontend.md)

---

## 🛠 CLI Usage

```bash
# Start new project
python -m interfaces.cli start "Your research question"

# List projects
python -m interfaces.cli list

# Run specific stage
python -m interfaces.cli run-stage problem-framing <project_id>

# Approve artifact
python -m interfaces.cli approve <project_id> ProjectContext
```

---

## 🎬 Examples & Demos

```bash
# Complete end-to-end pipeline
python examples/demos/demo_full_pipeline.py

# Anti-hallucination syntax engine
python examples/demos/demo_syntax_engine.py

# LLM synthesis workflow
python examples/demos/demo_synthesis.py

# Sprint 2 features (Stages 3-4)
python examples/demos/demo_sprint2.py
```

**See:** [examples/README.md](examples/README.md)

---

## ✅ Running Tests

```bash
# All tests (skip expensive LLM tests)
pytest -v -k "not llm"

# Full integration test
pytest tests/test_full_pipeline_stages_0_7.py -v

# Specific stage test
pytest tests/test_stage7_query_execution.py -v

# With coverage
pytest --cov=src --cov-report=html
```

**Test Coverage:** >80%  
**See:** [docs/development/testing.md](docs/development/testing.md)

---

## 📦 Project Structure

```
strategy-pipeline/
├── src/
│   ├── stages/              # 8 pipeline stages
│   │   ├── project_setup.py
│   │   ├── problem_framing.py
│   │   ├── research_questions.py
│   │   ├── search_concept_expansion.py
│   │   ├── database_query_plan.py
│   │   ├── screening_criteria.py      # NEW
│   │   ├── query_execution.py         # NEW
│   │   └── strategy_export.py         # NEW
│   ├── services/            # Core services
│   │   ├── model_service.py
│   │   ├── search_service.py          # NEW
│   │   └── persistence_service.py
│   ├── models.py            # Data models
│   ├── controller.py        # Main controller
│   └── orchestration/       # Stage orchestration
├── tests/                   # Comprehensive test suite
├── docs/                    # MkDocs documentation
├── examples/                # Code examples
├── interfaces/              # CLI + Web UI
└── requirements.txt
```

---

## 🔍 Stage 7: Query Execution (NEW)

**Features:**
- Executes validated queries on 4 live databases
- Auto-deduplication (DOI + title matching)
- Project-scoped result storage
- Graceful degradation for unsupported databases

**Supported Databases:**
- ✅ arXiv (preprints)
- ✅ OpenAlex (open scholarly data)
- ✅ Crossref (DOI registry)
- ✅ Semantic Scholar (AI-powered)

**Example Output:**
```json
{
  "total_results": 347,
  "deduplicated_count": 295,
  "databases_searched": ["arxiv", "openalex", "crossref"],
  "deduplication_stats": {
    "duplicates_removed": 52,
    "deduplication_rate": 15.0
  }
}
```

---

## 📊 Stage 6: Strategy Export (NEW)

**Export Formats:**
- ✅ **CSV** - Excel/Google Sheets compatible (11 fields)
- ✅ **BibTeX** - Zotero/Mendeley citations
- ✅ **RIS** - EndNote format
- ✅ **PRISMA Protocol** - Markdown documentation
- ✅ **Query Files** - Copy/paste ready for databases

**Example Usage:**
```python
# Export with all formats
result = controller.run_stage(
    "strategy-export",
    project_id=project_id,
    export_formats=["csv", "bibtex", "ris"]
)

# Files created:
# - papers.csv (295 papers)
# - papers.bib (BibTeX)
# - papers.ris (EndNote)
# - STRATEGY_PROTOCOL.md (PRISMA)
```

---

## 🎯 Stage 5: Screening Criteria (NEW)

**Features:**
- Deterministic PICO extraction (no LLM overhead)
- 10 inclusion criteria categories
- 7 exclusion criteria categories
- PRISMA-aligned defaults
- Query complexity awareness

**Example Output:**
```json
{
  "inclusion_criteria": [
    "Studies focusing on: LLM systems, AI models",
    "Studies evaluating: hallucination mitigation, factual accuracy",
    "Peer-reviewed publications",
    "Original research studies"
  ],
  "exclusion_criteria": [
    "Non-scholarly sources",
    "Opinion pieces without empirical data",
    "Studies outside specified scope"
  ]
}
```

---

## 📈 Performance & Cost

| Operation | Time | Cost (GPT-4) | Cost (GPT-3.5) |
|-----------|------|--------------|----------------|
| Stages 0-4 | ~20-30s | ~$0.005 | ~$0.001 |
| Stage 5 | <1ms | $0 | $0 |
| Stage 7 | 10-30s | $0 | $0 |
| Stage 6 | <1s | $0 | $0 |
| **Full Pipeline** | **~1-2 min** | **~$0.005** | **~$0.001** |

**Mock Mode:** $0 (deterministic, no API calls)

---

## 🌟 Differentiators

| Dimension | Strategy Pipeline | Generic LLM Prompting | Manual Review |
|-----------|-------------------|----------------------|---------------|
| **Query Validity** | ✅ Guaranteed | ❌ Often broken | ⚠️ Error-prone |
| **Paper Retrieval** | ✅ Automated (4 DBs) | ❌ None | ⚠️ Manual searches |
| **Deduplication** | ✅ Automatic | ❌ None | ⚠️ Manual |
| **Export Formats** | ✅ 3 formats | ❌ None | ⚠️ Manual conversion |
| **Reproducibility** | ✅ Full artifacts | ❌ Low | ⚠️ Medium |
| **PRISMA Compliance** | ✅ Built-in | ❌ None | ⚠️ Manual |
| **Time to Results** | ✅ ~5 minutes | ❌ N/A | ⚠️ Days/weeks |

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/development/contributing.md) for guidelines.

**Quick Start:**
1. Fork repository
2. Create feature branch
3. Add tests for new features
4. Update documentation
5. Submit pull request

**Development Setup:**
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest -v

# Build documentation
mkdocs serve
```

---

## 🗺 Roadmap

### ✅ Completed (Nov 2025)
- All 8 pipeline stages operational
- Live database execution (4 databases)
- Multi-format export (CSV/BibTeX/RIS)
- PRISMA-compliant protocols
- Comprehensive documentation (MkDocs)
- Auto-generated API reference

### 🔜 Next (Dec 2025 - Jan 2026)
- [ ] Frontend UI integration (React)
- [ ] Real-time progress updates (WebSocket)
- [ ] PubMed E-utilities integration (with auth)
- [ ] Scopus API integration (with auth)
- [ ] PDF protocol generation
- [ ] PRISMA flowchart visualization
- [ ] Manual deduplication review UI

### 🚀 Future
- [ ] Collaborative review workflows
- [ ] Custom stage plugins
- [ ] ML-powered query refinement
- [ ] Automated screening suggestions
- [ ] Integration with reference managers

---

## 📊 Status Snapshot

```
Pipeline Stages:     8 / 8 (100%)  ✅
Live Databases:      4 / 7 (57%)   ✅
Export Formats:      3 formats     ✅
Test Coverage:       >80%          ✅
Documentation:       Complete      ✅
Production Ready:    YES           ✅
```

**Last Updated:** November 27, 2025

---

## 🛡 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙋 Support & Community

- 📚 **Documentation:** https://mbsoft31.github.io/strategy-pipeline
- 🐛 **Issues:** [GitHub Issues](https://github.com/mbsoft31/strategy-pipeline/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/mbsoft31/strategy-pipeline/discussions)
- 📧 **Email:** bekhouche.mouadh@univ-oeb.dz

---

## ⭐ Acknowledgments

Built with:
- **OpenAI/Anthropic APIs** - LLM-powered intelligent generation
- **OpenAlex, arXiv, Crossref, Semantic Scholar** - Open scholarly data
- **MkDocs Material** - Beautiful documentation
- **PRISMA Guidelines** - Systematic review best practices

---

## 📝 Citation

If you use this project in your research, please cite:

```bibtex
@software{strategy_pipeline_2025,
  author = {Bekhouche, Mouadh},
  title = {Strategy Pipeline: Production-Ready Systematic Literature Review Pipeline},
  year = {2025},
  url = {https://github.com/mbsoft31/strategy-pipeline},
  version = {1.0}
}
```

---

## ⭐ Star & Share

If this project helps you build higher-quality, reproducible systematic reviews, **please star it and share with your research colleagues!**

---

**Built for reliable, transparent, and intelligent literature review workflows.**

**🚀 Ready for real-world systematic reviews | 📚 PRISMA-compliant | 🔬 Research-grade infrastructure**

