# HITL Research Strategy Pipeline

This project implements a UI-agnostic, human-in-the-loop (HITL) pipeline to go from a raw research idea to a structured, reproducible search strategy.

- Architecture overview: `docs/architecture-overview.md`
- Design docs: `docs/pipeline-design.md`, `docs/models-and-model-services.md`
- Stage implementations: `src/stages/`
- Services: `src/services/`
- Controller: `src/controller.py`

## Quick start (Stage 0 demo)

Run the end-to-end demo for Project Setup using a local simple model service and file-based persistence:

```bash
python .\main.py
```

This will:
- Generate a draft `ProjectContext` from a raw idea
- Save it under `./data/<project_id>/ProjectContext.json`
- Simulate approval with a tiny edit

You can also run the example module:

```bash
python -m docs.examples.stage0_demo
```

## CLI usage

The pipeline includes a basic CLI for starting projects, running stages, and approving artifacts:

```bash
# Start a new project (Stage 0)
python -m interfaces.cli start "Your research idea here"

# List all projects
python -m interfaces.cli list

# Show project details
python -m interfaces.cli show <project_id>

# Run Stage 1 (Problem Framing)
python -m interfaces.cli run-stage problem-framing <project_id>

# Approve an artifact
python -m interfaces.cli approve <project_id> ProjectContext

# Approve with edits
python -m interfaces.cli approve <project_id> ProjectContext --edits '{"title": "New Title"}'
```

## Project layout

- `src/models.py` — dataclasses for artifacts
- `src/stages/` — `BaseStage` + concrete stages (Stage 0 & 1 implemented)
- `src/services/` — model and persistence abstractions + simple local implementation
- `src/controller.py` — `PipelineController` that orchestrates stages and HITL approvals
- `docs/` — architecture & design docs, examples
- `interfaces/cli.py` — Basic command-line interface
- `tests/` — Unit tests for stages and controller

## Implemented stages

- **Stage 0 (Project Setup):** Generates `ProjectContext` from a raw idea
- **Stage 1 (Problem Framing):** Generates `ProblemFraming` and `ConceptModel` from context

## Next steps

- Add Stage 2 (Research Questions) using the same pattern
- Implement a web UI with Flask/FastAPI
- Flesh out ModelService to call a real LLM/SLM (optional)
- Add more comprehensive validation and error handling
