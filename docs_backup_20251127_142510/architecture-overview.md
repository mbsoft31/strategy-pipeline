# Architecture Overview

This document outlines the high-level architecture of the HITL research-strategy pipeline, emphasizing separation of concerns between core pipeline logic and UI/presentation layers.

---

## Core architectural principle

The pipeline is built with UI-agnostic stages that can be driven by:
- A CLI (command-line interface).
- A web UI (Flask, FastAPI, or any frontend).
- A Jupyter notebook.
- Programmatic API calls (e.g., for testing or automation).

To achieve this, we use a layered architecture:

```
┌─────────────────────────────────────────────┐
│  Presentation Layer (UI/CLI/Web/Notebook)   │
│  - Renders artifacts to users               │
│  - Collects user input/edits                │
│  - Calls pipeline controller methods        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Controller Layer (PipelineController)      │
│  - Orchestrates stage execution             │
│  - Manages state transitions                │
│  - Enforces HITL checkpoints                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Domain Layer (Stages + Models)             │
│  - Stage implementations                    │
│  - Artifact/data models                     │
│  - Business logic (pure Python)             │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Service Layer (ModelService, Persistence)  │
│  - LLM/SLM backends                         │
│  - File/database storage                    │
│  - External integrations                    │
└─────────────────────────────────────────────┘
```

This architecture ensures your pipeline is future-proof and can grow from a simple CLI to a full web application without major refactoring.

Note: For runnable examples, see `docs/examples/`.

---

## Layer responsibilities

### 1. Presentation Layer (UI-specific)

Responsibility:
- Render artifacts (questions, queries, criteria) in a format suitable for the user (terminal, HTML, JSON API).
- Collect user edits and approval decisions.
- Call controller methods to advance the pipeline.

Key point:
- Does not contain business logic.
- Does not directly manipulate artifacts or call model services.

Examples:
- `interfaces/cli.py` – CLI using `rich`, `click`, or `prompt_toolkit`.
- `interfaces/web_app.py` – Flask/FastAPI server exposing REST endpoints.
- `notebook_runner.ipynb` – Jupyter notebook with interactive widgets.

---

### 2. Controller Layer

Responsibility:
- Orchestrate pipeline execution.
- Manage the current project state (which stage is active, which artifacts exist).
- Enforce HITL checkpoint logic:
  - Present draft artifacts to the UI.
  - Wait for user approval/edits.
  - Transition to the next stage.

Key abstraction: `PipelineController`

Provides methods like:
- `start_project(raw_idea: str) -> StageResult`
- `run_stage(stage_name: str, project_id: str, **inputs) -> StageResult`
- `get_artifact(project_id: str, artifact_type: str, artifact_class: Any) -> Artifact`
- `approve_artifact(...) -> None`
- `get_next_available_stages(project_id: str) -> List[str]`

Key point:
- Controller knows what to do but doesn't know how to present it (that's the UI's job).
- Controller calls domain-layer stages and service-layer backends.

---

### 3. Domain Layer (Core pipeline logic)

Responsibility:
- Implement each pipeline stage as a self-contained unit.
- Define artifact models (data classes).
- Contain business logic (e.g., validation rules, transformation logic).

Key abstractions:

- `BaseStage` (in `src/stages/base.py`):
  - `execute(...) -> StageResult`
  - Returns draft artifacts and metadata.
  - Does not interact with users directly.

- Concrete stages (planned):
  - `ProjectSetupStage`
  - `ProblemFramingStage`
  - `ResearchQuestionStage`
  - `SearchStrategyStage`
  - `ScreeningCriteriaStage`
  - `StrategyExportStage`

Key point:
- Stages are pure functions from inputs + services → `StageResult`.
- Stages don't “wait” for user input—they return immediately with drafts for HITL.

---

### 4. Service Layer

Responsibility:
- Provide external capabilities to stages (LLM, SLM, persistence, etc.).

Key abstractions:

- `ModelService` (in `src/services/model_service.py`)
  - LLM/SLM interface used by stages.
- `PersistenceService` (in `src/services/persistence_service.py`)
  - Saving/loading artifacts:
    - `save_artifact(artifact: Any, project_id: str, artifact_type: str) -> None`
    - `load_artifact(artifact_type: str, project_id: str, artifact_class: Type[T]) -> Optional[T]`
    - `list_projects() -> List[str]`
    - `project_exists(project_id: str) -> bool`
- Future: `DatabaseConnectorService`, `ReferenceManagerService`, etc.

Key point:
- Services are dependency-injected into controller/stages.
- Swappable implementations (e.g., file-based vs database-based persistence; online vs local models).

---

## HITL checkpoint pattern (UI-agnostic)

The HITL interaction is split between controller and UI.

### Controller's role

1. Execute a stage to get a draft artifact.
2. Store it with `status = DRAFT`.
3. Return a `StageResult` object containing:
   - The draft artifact.
   - Suggested prompts/questions for the user.
   - Metadata (model used, timestamp, etc.).
4. Wait for the UI to call back with user edits and approval.

### UI's role

1. Receive `StageResult` from controller.
2. Render the draft artifact (form, table, CLI prompts, etc.).
3. Let user edit fields.
4. Collect user approval decision (`approve`, `revise`, `restart`).
5. Call controller to apply edits and transition state.

Example interaction flow (CLI vs Web)

CLI flow:

```python
# User runs: python cli.py run-stage project-setup
result = controller.run_stage("project-setup", project_id="project_123")

draft_context = result.draft_artifact
print(f"Generated title: {draft_context.title}")

# User edits/approves
new_title = input("Edit title (or press Enter to keep): ") or draft_context.title
controller.approve_artifact(
    project_id="project_123",
    artifact_type="ProjectContext",
    artifact_class=ProjectContext,
    edits={"title": new_title},
)
```

Web flow:

```python
# User hits POST /api/projects with {"idea": "NLP for healthcare"}
result = controller.start_project(raw_idea)
return jsonify(result.to_dict())  # Frontend renders form

# User edits and submits
# POST /api/projects/{project_id}/context/approve with JSON body
controller.approve_artifact(
    project_id=project_id,
    artifact_type="ProjectContext",
    artifact_class=ProjectContext,
    edits=request.json,
)
```

Same controller logic, different presentation.

---

## Data flow example: Stage 0 (Project Setup)

1. User initiates (CLI or Web)
   - CLI: `python cli.py start-project --idea "NLP for healthcare"`
   - Web: `POST /api/projects { "idea": "NLP for healthcare" }`

2. Controller receives request

```python
def start_project(raw_idea: str) -> StageResult:
    stage = ProjectSetupStage(model_service, persistence_service)
    result = stage.execute(raw_idea=raw_idea)
    persistence_service.save_artifact(result.draft_artifact, result.draft_artifact.id, "ProjectContext")
    return result
```

3. Stage executes (pure logic)

```python
class ProjectSetupStage(BaseStage):
    def execute(self, raw_idea: str) -> Tuple[ProjectContext, ModelMetadata]:
        draft, metadata = self.model_service.suggest_project_context(raw_idea)
        return draft, metadata
```

4. UI renders and collects edits
   - CLI: Interactive prompts.
   - Web: JSON → frontend form → user edits → submit.

5. User approves
   - CLI: Calls `controller.approve_artifact(...)`.
   - Web: `POST /api/projects/{project_id}/context/approve`.

6. Controller updates state

```python
def approve_artifact(artifact_id: str, edits: Dict[str, Any]) -> None:
    artifact = persistence_service.load_artifact("ProjectContext", artifact_id)
    for key, value in edits.items():
        setattr(artifact, key, value)
    artifact.status = ApprovalStatus.APPROVED
    artifact.updated_at = datetime.utcnow()
    persistence_service.save_artifact(artifact, artifact_id)
```

---

## Benefits of this architecture

1. UI flexibility
2. Testability
3. Maintainability
4. Collaboration
5. Reproducibility

---

## Folder structure (proposed)

```text
strategy-pipeline/
├── docs/
│   ├── pipeline-design.md
│   ├── models-and-model-services.md
│   └── architecture-overview.md
├── src/
│   ├── __init__.py
│   ├── models.py               # Artifact data classes
│   ├── controller.py           # PipelineController
│   ├── stages/
│   │   ├── __init__.py
│   │   └── base.py             # BaseStage abstraction
│   └── services/
│       ├── __init__.py
│       ├── model_service.py    # ModelService interface + implementations
│       └── persistence_service.py
├── interfaces/
│   ├── __init__.py
│   ├── cli.py                  # CLI using click/rich (future)
│   └── web_app.py              # Flask/FastAPI web server (future)
├── tests/
│   ├── test_models.py
│   ├── test_controller.py
│   └── test_stages.py
├── main.py                     # Entry point, imports from src/
└── README.md
```

For runnable examples, see `docs/examples/`.
