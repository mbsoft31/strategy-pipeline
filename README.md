# HITL Research Strategy Pipeline

This project implements a UI-agnostic, human-in-the-loop (HITL) pipeline to go from a raw research idea to a structured, reproducible search strategy.

- Architecture overview: `docs/architecture-overview.md`
- Design docs: `docs/pipeline-design.md`, `docs/models-and-model-services.md`
- Stage implementations: `src/stages/`
- Services: `src/services/`
- Controller: `src/controller.py`

## Quick start (Stage 0 demo)

Run the end-to-end demo for Project Setup using a local simple model service and file-based persistence:

```
python .\main.py
```

This will:
- Generate a draft `ProjectContext` from a raw idea
- Save it under `./data/<project_id>/ProjectContext.json`
- Simulate approval with a tiny edit

You can also run the example module:

```
python -m docs.examples.stage0_demo
```

## Project layout

- `src/models.py` — dataclasses for artifacts
- `src/stages/` — `BaseStage` + concrete stages (Stage 0 implemented)
- `src/services/` — model and persistence abstractions + simple local implementation
- `src/controller.py` — `PipelineController` that orchestrates stages and HITL approvals
- `docs/` — architecture & design docs, examples

## Next steps

- Add Stage 1 (Problem Framing) using the same pattern
- Implement a basic CLI in `interfaces/` or a small FastAPI app for a web UI
- Flesh out ModelService to call a real LLM/SLM (optional)
