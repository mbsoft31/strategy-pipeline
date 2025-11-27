# Strategy Pipeline Documentation

Production-ready systematic literature review pipeline with LLM-powered search strategy generation and anti-hallucination query validation.

## 🚀 Quick Links

- 📚 [Getting Started](getting-started/quick-start.md) - 5-minute tutorial
- 📖 [User Guide](user-guide/quick-reference.md) - Comprehensive reference
- 🏗️ [Architecture](architecture/overview.md) - System design
- 🔌 [API Reference](api-reference/index.md) - Auto-generated API docs
- 💻 [Development](development/contributing.md) - Contributing guide
- 📝 [Examples](examples/) - Code examples

## ✨ Features

- ✅ **8-stage pipeline** - From research question to exportable papers
- ✅ **Anti-hallucination engine** - Validated boolean query generation
- ✅ **4 database integrations** - arXiv, OpenAlex, Crossref, Semantic Scholar
- ✅ **Auto-deduplication** - DOI + title similarity matching
- ✅ **Multi-format export** - CSV, BibTeX, RIS for citation managers
- ✅ **PRISMA-compliant** - Publication-ready protocols
- ✅ **Deterministic screening** - PICO-based inclusion/exclusion criteria
- ✅ **Production-ready** - Comprehensive tests and error handling

## 📦 Installation

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

See [Installation Guide](getting-started/installation.md) for detailed setup.

## ⚡ Quick Example

```python
from src.controller import PipelineController
from src.services import IntelligentModelService, FilePersistenceService

# Initialize controller
controller = PipelineController(
    IntelligentModelService(),
    FilePersistenceService(base_dir="./data")
)

# Start project
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
    controller.approve_artifact(
        project_id,
        result.draft_artifact.__class__.__name__
    )

# Access results
print(f"Results: data/{project_id}/export/")
# - papers.csv (Excel-ready screening)
# - papers.bib (Zotero/Mendeley)
# - papers.ris (EndNote)
# - STRATEGY_PROTOCOL.md (PRISMA protocol)
```

## 📊 Pipeline Stages

| Stage | Name | Function |
|-------|------|----------|
| 0 | Project Setup | Initialize project context |
| 1 | Problem Framing | Extract PICO elements |
| 2 | Research Questions | Generate research questions |
| 3 | Concept Expansion | Expand keywords (MeSH/synonyms) |
| 4 | Database Query Plan | Generate validated boolean queries |
| 5 | Screening Criteria | PICO-based inclusion/exclusion |
| 7 | Query Execution | Execute searches, retrieve papers |
| 6 | Strategy Export | Export to CSV/BibTeX/RIS |

## 🎯 Use Cases

- **Academic Researchers** - Systematic literature reviews
- **Research Teams** - Collaborative review workflows
- **Meta-Analysts** - Evidence synthesis
- **PhD Students** - Dissertation research
- **Research Librarians** - Search strategy development

## 🏗️ Architecture

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
```

See [Architecture Overview](architecture/overview.md) for details.

## 📚 Documentation Structure

```
docs/
├── getting-started/     # Setup and tutorials
├── user-guide/          # Usage guides
├── architecture/        # System design
├── api-reference/       # Auto-generated API docs
├── development/         # Contributing guides
└── examples/            # Code examples
```

## 🤝 Support

- 🐛 [Report Issues](https://github.com/mbsoft31/strategy-pipeline/issues)
- 💬 [Discussions](https://github.com/mbsoft31/strategy-pipeline/discussions)
- 📧 Email: bekhouche.mouadh@univ-oeb.dz

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgments

Built with:
- OpenAI/Anthropic LLMs for intelligent query generation
- OpenAlex, arXiv, Crossref, Semantic Scholar APIs
- PRISMA guidelines for systematic reviews

---

**Version:** 1.0  
**Last Updated:** November 27, 2025  
**Status:** Production Ready ✅

