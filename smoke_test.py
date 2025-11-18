"""Quick smoke test for Stage 1 and CLI."""
import sys
sys.path.insert(0, ".")

from src.controller import PipelineController
from src.models import ProjectContext, ProblemFraming
from src.services import FilePersistenceService, SimpleModelService

print("Testing Stage 1 implementation...")

# Setup
model = SimpleModelService()
store = FilePersistenceService(base_dir="./test_data_temp")
controller = PipelineController(model_service=model, persistence_service=store)

# Stage 0
print("\n1. Creating project (Stage 0)...")
result0 = controller.start_project(raw_idea="Testing AI ethics in autonomous systems")
project_id = result0.draft_artifact.id
print(f"   OK Project created: {project_id}")

# Approve Stage 0
print("\n2. Approving ProjectContext...")
controller.approve_artifact(
    project_id=project_id,
    artifact_type="ProjectContext",
    artifact_class=ProjectContext,
    edits={},
)
print("   OK ProjectContext approved")

# Stage 1
print("\n3. Running Stage 1 (Problem Framing)...")
result1 = controller.run_stage("problem-framing", project_id)
print(f"   OK Stage 1 completed")
print(f"   - Artifact: {result1.draft_artifact.__class__.__name__}")
print(f"   - Problem: {result1.draft_artifact.problem_statement[:60]}...")
print(f"   - Goals: {len(result1.draft_artifact.goals)} goals")
print(f"   - ConceptModel: {len(result1.extra_data['concept_model'].concepts)} concepts")

# Approve Stage 1
print("\n4. Approving ProblemFraming...")
controller.approve_artifact(
    project_id=project_id,
    artifact_type="ProblemFraming",
    artifact_class=ProblemFraming,
    edits={},
)
print("   OK ProblemFraming approved")

# Verify persistence
print("\n5. Verifying persistence...")
loaded = controller.get_artifact(project_id, "ProblemFraming", ProblemFraming)
assert loaded is not None
assert loaded.project_id == project_id
print(f"   OK Artifacts persisted and reloadable")

print("\nALL TESTS PASSED!")

# Cleanup
import shutil
shutil.rmtree("./test_data_temp", ignore_errors=True)
