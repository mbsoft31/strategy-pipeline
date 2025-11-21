# Documentation Index

**Last Updated:** November 21, 2025

This document provides a complete overview of the project documentation, organized by category.

---

## Quick Start

- **README.md** (root) - Main project overview and setup instructions
- **IMPLEMENTATION_STATUS.md** - Current implementation progress (5/7 stages)

---

## Documentation Structure

### 📋 **Stages/** - Stage Implementation Documentation

Complete documentation for each pipeline stage:

- **STAGE3_COMPLETE.md** - SearchConceptExpansion stage (✅ Complete)
- **STAGE3_DEBUG_FIX.md** - Debug logging and error fixes for Stage 3
- **STAGE4_COMPLETE.md** - DatabaseQueryPlan stage (✅ Complete)
- **STAGE4_REVISION_PLAN.md** - Revision plan identifying 10 improvement areas
- **STAGE4_REVISION_COMPLETE.md** - Final revision with complexity analysis + NOT operator fixes
- **STAGE5_PLACEHOLDER.md** - ScreeningCriteria stage (🚧 Scaffolding)
- **STAGE6_PLACEHOLDER.md** - StrategyExport stage (🚧 Scaffolding)

**Current Status:** Stages 0-4 complete (57% of pipeline)

---

### 📈 **Sprints/** - Sprint Progress & Summaries

Historical sprint documentation tracking implementation progress:

- **SPRINT1_SUMMARY.md** - Foundation phase (Stages 0-2)
- **SPRINT2_COMPLETE.md** - Problem framing and research questions
- **SPRINT2_FINAL_SUMMARY.md** - Stage 2 completion summary
- **SPRINT2_QUICKSTART.md** - Stage 2 quick reference
- **SPRINT3_COMPLETE.md** - Search concept expansion (Stage 3)
- **SPRINT3_QUICKSTART.md** - Stage 3 quick reference
- **SPRINT4_PHASE1_COMPLETE.md** - Stage 4 initial implementation
- **SPRINT4_QUICKSTART.md** - Stage 4 quick reference
- **SPRINT4_REFERENCE.md** - Technical reference for Stage 4
- **SPRINT4_SUMMARY.md** - Stage 4 completion summary
- **SPRINT5_COMPLETE.md** - Anti-Hallucination layer integration

---

### 📋 **Plans/** - Implementation Plans & Prompts

Detailed implementation plans for future stages and features:

- **plan-databaseQueryPlan.prompt.md** - Stage 4 comprehensive plan
- **plan-enhancedHitlPipeline.prompt.md** - Enhanced HITL pipeline planning
- **plan-hitlPipelineNextSteps.prompt.md** - HITL next steps
- **plan-llmIntegrationWithValidation.prompt.md** - LLM integration strategy
- **plan-slrIntegration.prompt.md** - Systematic Literature Review integration

---

### 🔧 **Guides/** - Technical Guides & References

Implementation guides and technical references:

- **DEPLOYMENT_GUIDE.md** - Deployment instructions and best practices
- **DIALECT_EXAMPLES.md** - Search syntax examples for different databases
- **DIALECT_EXTENSION_SUMMARY.md** - Guide for extending database dialects
- **guide-phase1Foundation.prompt.md** - Phase 1 foundation guide
- **OPENROUTER_GUIDE.md** - OpenRouter API setup and usage
- **OPENROUTER_INTEGRATION.md** - OpenRouter integration details

---

### 📚 **Archive/** - Historical Documentation

Older documentation kept for reference:

- **DAY1_COMPLETE.md** - Initial day progress
- **DAY1_EXECUTION_SUMMARY.md** - Day 1 summary
- **DAY2_QUICKSTART.md** - Day 2 quick start
- **GIT_COMMIT_SUMMARY.md** - Git commit history summary
- **README_FULL.md** - Older comprehensive README
- **WHATS_NEXT.md** - Previous next steps document

---

## Root Documentation Files

### Main Reference Documents

```
README.md                     - Project overview, setup, quick start
PROJECT_STATUS.md             - Overall project status and metrics
IMPLEMENTATION_STATUS.md      - Detailed implementation progress (5/7 stages)
```

---

## Project Structure Overview

```
strategy-pipeline/
├── docs/                     # 📚 Documentation (this folder)
│   ├── stages/              # Stage-specific documentation
│   ├── sprints/             # Sprint progress tracking
│   ├── plans/               # Implementation plans
│   ├── guides/              # Technical guides
│   ├── archive/             # Historical docs
│   ├── IMPLEMENTATION_STATUS.md
│   ├── PROJECT_STATUS.md
│   └── INDEX.md            # This file
│
├── src/                      # Source code
│   ├── stages/              # Pipeline stages (0-4 complete)
│   ├── services/            # LLM, model, and utility services
│   ├── search/              # Anti-Hallucination syntax engine
│   └── utils/               # Utilities and exceptions
│
├── tests/                    # Test suite (comprehensive)
├── scripts/                  # Demo and utility scripts
├── interfaces/               # CLI and web app interfaces
├── static/ & templates/      # Web UI assets
│
└── [Configuration Files]
    ├── .env                  # Environment configuration
    ├── requirements.txt      # Python dependencies
    ├── pytest.ini           # Pytest configuration
    └── README.md            # Main README
```

---

## Key Metrics

| Metric | Value |
|--------|-------|
| **Stages Complete** | 5 / 7 (71%) |
| **Progress** | Stages 0-4 ✅ |
| **Test Coverage** | Comprehensive |
| **Documentation** | 35+ files |
| **Sprints Completed** | 5 |
| **Latest Update** | Stage 4 revision |

---

## Current Implementation Status

### ✅ Completed Stages

**Stage 0: Project Setup** (✅)
- LLM-powered project context generation
- Comprehensive input validation

**Stage 1: Problem Framing** (✅)
- Critique loop (Draft → Critique → Refine)
- OpenAlex validation of concepts
- Risk assessment and feasibility scoring

**Stage 2: Research Questions** (✅)
- PICO-based question generation
- Linked concept tracking
- Methodological lens integration

**Stage 3: Search Concept Expansion** (✅)
- LLM-powered synonym generation
- Graceful fallback to heuristic expansion
- Included/excluded term handling

**Stage 4: Database Query Plan** (✅)
- Database-specific Boolean query generation
- **NEW:** Complexity analysis (6 levels)
- **NEW:** Enhanced NOT operator formatting
- **NEW:** Empty block validation
- Hit count estimation support

### ⏳ Future Stages

**Stage 5: Screening Criteria** - Next
- Inclusion/exclusion criteria generation
- PICO-based criterion formulation
- Study design and quality filters

**Stage 6: Strategy Export** - Future
- Markdown/PDF output generation
- Complete strategy documentation
- Execution blueprints

---

## Anti-Hallucination Features

The project implements multiple layers of anti-hallucination protection:

### Layer 1: Deterministic Syntax Engine
- Database-specific dialect system
- Guaranteed valid Boolean query syntax
- Field-tag validation (PubMed MeSH, Scopus TITLE-ABS-KEY, etc.)

### Layer 2: LLM Validation
- Detects hallucinated operators (NEAR, ADJ, PROX)
- Database-specific syntax checking
- Character limit warnings

### Layer 3: Graceful Fallback
- LLM → Validation → Syntax Engine
- Always produces valid output
- Clear error messages with guidance

---

## Getting Started with Documentation

### For New Contributors

1. Start with **README.md** in root
2. Review **PROJECT_STATUS.md** for current progress
3. Check relevant **stages/** doc for your area
4. Reference **guides/** for technical implementation details

### For Continuing Development

1. Read **IMPLEMENTATION_STATUS.md** for what's complete
2. Review **STAGE4_REVISION_COMPLETE.md** for latest improvements
3. Check **plans/** for next stage details
4. Use **sprints/** for historical context

### For Deployment

1. Follow **DEPLOYMENT_GUIDE.md** in guides/
2. Reference **OPENROUTER_GUIDE.md** for LLM setup
3. Review environment configuration in root .env.example

---

## Documentation Best Practices

### Adding New Documentation

1. **Stage docs**: Use `STAGE{N}_COMPLETE.md` format
2. **Plans**: Use `plan-{camelCaseName}.prompt.md` format
3. **Guides**: Use descriptive names in `guides/` folder
4. **Updates**: Always include date and status badge

### Organization Rules

- **Root level**: Only main README.md and config files
- **docs/stages/**: Stage-specific implementation docs
- **docs/sprints/**: Sprint tracking and progress
- **docs/plans/**: Future implementation plans
- **docs/guides/**: Technical and deployment guides
- **docs/archive/**: Old or superseded documentation

---

## Version History

### Latest Updates (November 21, 2025)

- ✅ Stage 4 revision complete with complexity analysis
- ✅ Anti-Hallucination layer fully integrated
- ✅ 5/7 pipeline stages implemented
- ✅ Documentation reorganized and indexed
- ✅ Repository cleaned up

### Previous Major Updates

- Sprint 5: Anti-Hallucination layer integration
- Sprint 4: Database query plan stage
- Sprint 3: Search concept expansion
- Sprint 2: Problem framing & research questions
- Sprint 1: Foundation (Project setup)

---

## Quick Reference Links

### Essential Files

- [README.md](../README.md) - Main project overview
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Project metrics
- [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) - Progress tracking

### Latest Stage Documentation

- [STAGE4_REVISION_COMPLETE.md](stages/STAGE4_REVISION_COMPLETE.md) - Latest improvements
- [STAGE4_COMPLETE.md](stages/STAGE4_COMPLETE.md) - Full stage documentation
- [STAGE3_COMPLETE.md](stages/STAGE3_COMPLETE.md) - Search expansion

### Quick Starts

- [SPRINT4_QUICKSTART.md](sprints/SPRINT4_QUICKSTART.md) - Stage 4 quick reference
- [SPRINT3_QUICKSTART.md](sprints/SPRINT3_QUICKSTART.md) - Stage 3 quick reference

### Setup Guides

- [DEPLOYMENT_GUIDE.md](guides/DEPLOYMENT_GUIDE.md) - Deployment instructions
- [OPENROUTER_GUIDE.md](guides/OPENROUTER_GUIDE.md) - LLM API setup

---

## Contributing

When working on the project:

1. Update relevant stage documentation
2. Create new plan doc if adding features
3. Keep status documents current
4. Move completed items to archive
5. Update this INDEX.md

---

**Documentation organized and maintained with ❤️**

For questions or updates needed, see the main README.md in the project root.
