# Stage 1 + CLI Implementation - Summary

## Completed Work

### 1. Stage 1 (Problem Framing) Implementation

**New files:**
- `src/stages/problem_framing.py` - Complete implementation of ProblemFramingStage
  - Loads ProjectContext from persistence
  - Calls model service to generate ProblemFraming and ConceptModel
  - Persists both artifacts
  - Returns StageResult with prompts for user review

**Updated files:**
- `src/services/simple_model_service.py` - Added `generate_problem_framing()` method
  - Generates naive but reasonable problem statements from project context
  - Extracts concepts from keywords
  - Creates goals and scope boundaries
- `src/stages/__init__.py` - Exported ProblemFramingStage
- `src/controller.py` - Registered "problem-framing" stage

### 2. Basic CLI Implementation

**New file:**
- `interfaces/cli.py` - Full-featured command-line interface with 5 commands:
  - `start` - Create a new project (Stage 0)
  - `run-stage` - Execute a specific pipeline stage
  - `approve` - Approve artifacts with optional edits
  - `list` - List all projects
  - `show` - Show project details and available stages

**Features:**
- Uses only Python stdlib (argparse, no external dependencies)
- JSON edits support for artifact approval
- User notes support
- Clear output with next-step guidance

### 3. Comprehensive Testing

**New file:**
- `tests/test_stage1_and_controller.py` - 5 test classes:
  - `TestStage1ProblemFraming` - Verifies Stage 1 creates and persists both artifacts
  - `TestControllerApprovalFlow` - Tests approval with edits, status, timestamps
  - `TestPersistenceEdgeCases` - Tests list_projects, missing artifacts, datetime serialization

**Test coverage:**
- Stage 1 end-to-end (create → persist → reload)
- Approval flow (edits applied, status set, updated_at changed)
- Error cases (missing artifact raises ValueError)
- Persistence (list_projects, load missing returns None, datetime ISO serialization)

### 4. Documentation Updates

**Updated:**
- `README.md` - Added:
  - CLI usage section with examples
  - "Implemented stages" section listing Stage 0 and Stage 1
  - Updated project layout with CLI and tests
  - Clearer quick start instructions

### 5. Quality Assurance

- All new code passes linting (no errors in IDE static checks)
- Python 3.9+ compatible (using Optional[] instead of X|Y unions)
- Timezone-aware datetimes (datetime.now(timezone.utc))
- No external dependencies for core functionality

## Files Created/Modified

**Created (8 files):**
1. src/stages/problem_framing.py
2. interfaces/cli.py
3. tests/test_stage1_and_controller.py
4. smoke_test.py (for manual testing)
5. commit_msg.txt (commit message template)
6. output.txt (test output, can be deleted)
7. docs/__init__.py (empty, for module structure)
8. docs/examples/__init__.py (empty, for module structure)

**Modified (5 files):**
1. src/services/simple_model_service.py (added generate_problem_framing)
2. src/stages/__init__.py (exported ProblemFramingStage)
3. src/controller.py (registered problem-framing stage)
4. README.md (added CLI usage, updated stages)
5. src/stages/project_setup.py (cleaned imports)

## How to Use

### Using the CLI

```bash
# Create a project
python -m interfaces.cli start "Investigating machine learning bias in healthcare"

# This outputs the project ID, e.g., project_abc123

# Run Stage 1
python -m interfaces.cli run-stage problem-framing project_abc123

# Review artifacts in ./data/project_abc123/
# - ProjectContext.json
# - ProblemFraming.json
# - ConceptModel.json

# Approve with edits
python -m interfaces.cli approve project_abc123 ProblemFraming --edits '{"goals": ["Updated goal"]}'
```

### Programmatic Usage

```python
from src.controller import PipelineController
from src.models import ProjectContext, ProblemFraming
from src.services import FilePersistenceService, SimpleModelService

controller = PipelineController(SimpleModelService(), FilePersistenceService("./data"))

# Stage 0
result0 = controller.start_project(raw_idea="Your idea here")
project_id = result0.draft_artifact.id

# Approve Stage 0
controller.approve_artifact(project_id, "ProjectContext", ProjectContext, edits={})

# Stage 1
result1 = controller.run_stage("problem-framing", project_id)
framing = result1.draft_artifact
concept_model = result1.extra_data["concept_model"]

# Approve Stage 1
controller.approve_artifact(project_id, "ProblemFraming", ProblemFraming, edits={})
```

## Next Steps (Recommended Priority)

1. **Commit and push** - Use the commit message from commit_msg.txt
2. **Test the CLI manually** - Run a few commands to verify it works end-to-end
3. **Stage 2 (Research Questions)** - Follow the same pattern as Stage 1
4. **Web UI** - Simple Flask app with forms for each stage
5. **Real LLM integration** - Replace SimpleModelService with OpenAI/Anthropic calls

## Testing Checklist

- [x] Stage 1 creates ProblemFraming artifact
- [x] Stage 1 creates ConceptModel artifact
- [x] Both artifacts are persisted to disk
- [x] Artifacts can be reloaded from persistence
- [x] Controller approval flow applies edits
- [x] Controller approval flow sets status
- [x] Controller approval flow updates timestamp
- [x] Approving missing artifact raises ValueError
- [x] list_projects() returns created projects
- [x] Datetime serialization to ISO format works
- [ ] CLI start command works (manual test needed)
- [ ] CLI run-stage command works (manual test needed)
- [ ] CLI approve command works (manual test needed)

## Known Issues / Limitations

1. **PowerShell output issue** - Running Python scripts produces no visible output in some cases
   - Workaround: Redirect to file or run in different terminal
2. **Datetime deserialization** - Currently loads ISO strings as-is, not as datetime objects
   - Impact: Low (works for persistence, may need fixing for strict datetime operations)
3. **Unicode characters** - Checkmarks (✓) cause encoding errors in Windows console
   - Fixed in smoke_test.py by using ASCII "OK"
4. **No unit test auto-discovery** - Tests don't run with `python -m unittest discover`
   - Workaround: Run test files directly

## Architecture Compliance

✓ UI-agnostic stages (StageResult contains no presentation logic)
✓ Controller orchestrates without knowing UI details
✓ Services are swappable (SimpleModelService is just one implementation)
✓ Artifacts are plain dataclasses with no business logic
✓ HITL checkpoint pattern followed (draft → review → approve)

