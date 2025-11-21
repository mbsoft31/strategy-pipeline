# Strategy Pipeline 🚀

<!-- Badges -->
<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-blue" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green" />
  <img alt="Status" src="https://img.shields.io/badge/Stages_Complete-5/7-brightgreen" />
  <img alt="Anti-Hallucination" src="https://img.shields.io/badge/Anti--Hallucination-Enabled-purple" />
  <img alt="Tests" src="https://img.shields.io/badge/Tests-Passing-success" />
</p>

> **TL;DR**: Turn a raw research idea into a validated, multi‑database, reproducible search strategy with **LLM help that never hallucinates invalid query syntax**—thanks to a deterministic Anti‑Hallucination query engine and human-in-the-loop approvals.

---
### 🚀 Elevator Pitch
LLMs are great at brainstorming but unreliable at constructing professional literature search strategies. They hallucinate operators, misuse field tags, and produce non-reproducible outputs. **Strategy Pipeline** fixes that: it blends *expert-like LLM assistance* with *deterministic, validated Boolean query generation* across seven major scholarly databases—giving researchers a transparent, auditable, and refinable process.

> Think of it as **“Git for your search strategy”** plus **“Rust-like guarantees for query correctness.”**

---
## 🧠 Who Is It For?
| User Type | Benefit |
|----------|---------|
| Academic Researcher | Faster protocol drafting (PRISMA, SLR prep) |
| Applied AI/ML Scientist | Structured exploration of emerging topics |
| Research Librarian | Assisted multi-database query assembly with validation |
| R&D Strategist | Rapid landscape scanning with reproducible artifacts |
| Startup / Innovation Analyst | Systematic concept expansion & risk framing |

### 🔬 Common Use Cases
- Building a **systematic review** search strategy
- Mapping **emerging AI methods** (e.g., retrieval augmentation)
- Creating **risk & feasibility framing** for a proposal
- Generating **PICO-aligned research questions** quickly
- Constructing **Boolean queries** for PubMed + Scopus without syntax errors

---
## ✨ Why This Project
Traditional LLM prompts for search strategies hallucinate unsupported operators (NEAR, ADJ, PROX), misuse field tags, and produce brittle queries. Manual construction is slow and error‑prone. Strategy Pipeline solves this by combining:

- ✅ Human-in-the-loop approvals at every stage
- ✅ Deterministic syntax engine (guaranteed valid queries)
- ✅ Multi-database dialect support (PubMed, Scopus, arXiv, OpenAlex, Semantic Scholar, Crossref, Web of Science)
- ✅ LLM assistance with validation + graceful fallback
- ✅ Excluded-term (NOT) logic & complexity scoring
- ✅ Persistent, reproducible artifact history

You get **precision, transparency, and auditability** instead of opaque one-off LLM outputs.

---
## 🔐 Anti-Hallucination Query Engine (Moat)
Three-tier safety net:
1. LLM generates candidate queries (persona: Research Librarian)
2. Syntax validator scans for hallucinated operators / invalid field tags
3. Deterministic dialect builder produces guaranteed executable Boolean queries (fallback if needed)

Result: 100% valid Boolean syntax; zero NEAR/ADJ/PROX leakage; consistent field-tag usage; database-specific formatting (e.g., `TITLE-ABS-KEY()` for Scopus, `[Title/Abstract]` for PubMed).

> ✅ Guarantees correctness where generic ChatGPT outputs fail.

---
## 🧱 Implemented Pipeline Stages (Current MVP – 5/7)
| Stage | Name | Status | Summary |
|-------|------|--------|---------|
| 0 | Project Setup | ✅ | Draft `ProjectContext` from raw idea |
| 1 | Problem Framing | ✅ | Structured framing + `ConceptModel` + feasibility & risks |
| 2 | Research Questions | ✅ | PICO-informed, method lenses, linked concepts |
| 3 | Search Concept Expansion | ✅ | Included/excluded term blocks (LLM + fallback) |
| 4 | Database Query Plan | ✅ | Multi-database Boolean queries + complexity analysis |
| 5 | Screening Criteria | ⏳ | Planned (inclusion / exclusion logic) |
| 6 | Strategy Export | ⏳ | Planned (Markdown / PDF full bundle) |

Roadmap details: `docs/IMPLEMENTATION_STATUS.md` & `PROJECT_STATUS.md`.

---
## 🧩 Core Features
- Human-in-the-loop approval workflow (edit before advancing)
- Artifact persistence under `./data/<project_id>/`
- Multi-model provider abstraction (OpenAI, OpenRouter, Mock)
- Structured dataclass artifacts (versionable & auditable)
- Dialect-based query synthesis (7 databases)
- Complexity scoring & guidance (broad ↔ narrow balance)
- Excluded term NOT logic (dialect aware)
- Fallback resilience (always produces output)
- Auditability & reproducibility built-in

---
## 🏗 Architecture at a Glance
- Controller: Orchestrates stage progression (`src/controller.py`)
- Stages: Discrete transformation units (`src/stages/`)
- Services: Model, search, persistence, syntax (`src/services/`, `src/search/`)
- Anti-Hallucination Layer: Dialects + builder + validators (`src/search/`)
- Interfaces: CLI + Web UI (`interfaces/`)

See:
- `docs/architecture-overview.md`
- `docs/pipeline-design.md`
- `docs/models-and-model-services.md`

---
## ⚡ Try It in 60 Seconds
```bash
# 1. Clone
git clone https://github.com/your-username/strategy-pipeline.git
cd strategy-pipeline

# 2. (Optional) virtual env
python -m venv .venv && .venv\\Scripts\\activate  # Windows
# or
python -m venv .venv && source .venv/bin/activate    # macOS/Linux

# 3. Install deps
pip install -r requirements.txt

# 4. Run Stage 0
python main.py

# 5. Inspect artifact
cat data/*/ProjectContext.json
```

---
## 🔧 Configure LLM Provider
Copy template and choose provider:
```bash
cp .env.example .env
```
Edit `.env`:
```env
LLM__PROVIDER=mock          # offline deterministic mode
# OR
LLM__PROVIDER=openrouter    # real models via OpenRouter
LLM__OPENROUTER_API_KEY=sk-or-... 
LLM__OPENROUTER_MODEL=mistralai/mistral-nemo
# OR
LLM__PROVIDER=openai
LLM__OPENAI_API_KEY=sk-proj-...
LLM__OPENAI_MODEL=gpt-4o-mini
```
Mock mode lets you explore pipeline logic without cost or network.

---
## 🖥 Web UI
```bash
pip install -r requirements.txt
python interfaces/web_app.py
# Visit http://localhost:5000
```
Features: real-time stage updates (HTMX), draft editing, approval workflow, visual progression. More: `docs/WEB_UI_README.md`.

---
## 🛠 CLI Usage
```bash
# Start new project (Stage 0)
python -m interfaces.cli start "Investigate retrieval-augmented hallucination mitigation"

# List projects
python -m interfaces.cli list

# Run next stage (example: Problem Framing)
python -m interfaces.cli run-stage problem-framing <project_id>

# Approve artifact (editable)
python -m interfaces.cli approve <project_id> ProjectContext --edits '{"title": "Refined Title"}'
```

---
## 🎬 Demos & Examples
All demos moved to `examples/demos/` (see `examples/README.md`).
```bash
# Full pipeline through Stage 4
python examples/demos/demo_full_pipeline.py

# Anti-Hallucination syntax engine showcase
python examples/demos/demo_syntax_engine.py

# LLM synthesis & critique loop
python examples/demos/demo_synthesis.py
```
Recommended learning order: syntax engine → workflow → full pipeline.

---
## ✅ Running Tests
```bash
pytest tests/ -v
# Specific test
pytest tests/test_stage4_query_plan.py::test_complexity_analysis_present -v
```
All critical tests (28+) must pass before feature PRs.

---
## 🧪 Verification Utilities
Located in `scripts/utilities/`:
- `verify_implementation.py` – sanity checks
- `validate_dialects.py` – syntax engine validation
- `test_openrouter.py` – provider integration check

Run:
```bash
python scripts/utilities/verify_implementation.py
python scripts/utilities/validate_dialects.py
```

---
## 📦 Data Artifacts
Each approved stage saves a JSON artifact:
```
/data/<project_id>/
  ProjectContext.json
  ProblemFraming.json
  ConceptModel.json
  ResearchQuestionSet.json
  SearchConceptBlocks.json
  DatabaseQueryPlan.json
```
Deterministic snapshots support audit trails & reproducibility.

---
## 🔍 Complexity Analysis (Stage 4)
Each database query receives metrics:
```json
{
  "complexity_level": "balanced",
  "total_terms": 18,
  "num_blocks": 3,
  "expected_results": "100-1,000",
  "guidance": "Well-balanced query - recommended complexity for systematic reviews.",
  "warnings": []
}
```
Guides refinement decisions (broaden vs narrow).

---
## 🛡 Advantages vs Naive LLM Queries
| Problem | Naive LLM | Strategy Pipeline |
|---------|-----------|-------------------|
| Hallucinated operators | Frequent | Eliminated (validator + fallback) |
| Field tag misuse | High | Dialect-controlled |
| Reproducibility | Low | Artifact versioning |
| Human oversight | Minimal | Built-in approvals |
| Multi-database coverage | Ad-hoc | Structured, standardized |
| Error recovery | Fragile | Graceful fallback chain |

---
## 📈 Performance & Cost
| Operation | Typical Time | Approx Cost (gpt-4o-mini) |
|-----------|--------------|---------------------------|
| Stage 0 | 2–3s | ~$0.0003 |
| Stage 1 | 5–6s | ~$0.0005 |
| Stage 2 | 3–4s | ~$0.0004 |
| Stage 3 | 6–8s | ~$0.0005 |
| Stage 4 | <2s (mostly deterministic) | $0 (fallback) |
| Full (0–4) | ~20–25s | <$0.002 |

Mock mode: $0, deterministic fallback: $0.

---
## 🌟 Differentiators
| Dimension | Strategy Pipeline | Generic Prompting |
|-----------|-------------------|-------------------|
| Query Validity | Guaranteed | Often broken |
| Reproducibility | High (artifacts) | Low |
| Human Oversight | Built-in approvals | Manual / absent |
| Multi-DB Coverage | Structured & dialect-aware | Inconsistent |
| Error Handling | Automatic fallback | Unpredictable |
| Refinement | Guided complexity metrics | None |

---
## 🤝 Contributing
1. Fork & branch (`feature/add-stage5`)
2. Run tests & verification utilities
3. Add docs (update `docs/INDEX.md` + stage docs)
4. Open PR (follow Conventional Commits: `feat: add screening criteria stage`)
5. Ensure no secrets in commits

See `CONTRIBUTING.md` for full guidelines.

---
## 🗺 Roadmap (High-Level)
- Stage 5: Screening Criteria (inclusion/exclusion, study design filters)
- Stage 6: Export Bundle (Markdown/PDF strategy package)
- MeSH validation via NCBI E-utilities
- Additional dialects: IEEE Xplore, ACM, CINAHL
- Query preview / dry-run mode
- Execution + result deduplication pipeline
- Strategy quality scoring & adaptive refinement

---
## 📊 Status Snapshot
See live details in `PROJECT_STATUS.md`.
```
Stages Complete: 5 / 7 (71%)
Tests Passing:   100% (28+)
Anti-Hallucination: Fully integrated (Stage 4)
```

---
## 🧪 Example Programmatic Use
```python
from src.controller import PipelineController
from src.services import IntelligentModelService, FilePersistenceService

controller = PipelineController(
    model_service=IntelligentModelService(),
    persistence_service=FilePersistenceService(base_dir="./data")
)
# Stage 0
ctx_result = controller.start_project(raw_idea="Assess retrieval augmentation strategies for reducing LLM hallucinations")
project_id = ctx_result.draft_artifact.id
# Approve context
controller.approve_artifact(project_id, "ProjectContext")
# Run further stages sequentially
for stage in ["problem-framing", "research-questions", "search-concept-expansion", "database-query-plan"]:
    res = controller.run_stage(stage, project_id=project_id)
    controller.approve_artifact(project_id, res.stage_name.replace("-", "").title())  # or manual edits
```

---
## 🛡 License
MIT License – see `LICENSE`.

---
## 🙋 Support & Questions
- Documentation Index: `docs/INDEX.md`
- Examples guide: `examples/README.md`
- Utilities guide: `scripts/utilities/README.md`
- Open an Issue / Discussion after publishing to GitHub

---
## ⭐ Star & Share
If this project helps you build higher-quality, reproducible search strategies, **star it and share with research colleagues**.

---
**Built for reliable, transparent, and intelligent literature strategy development.**
