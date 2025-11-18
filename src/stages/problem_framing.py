"""Stage 1: Problem framing & concept decomposition.

Generates draft ProblemFraming and ConceptModel from an approved ProjectContext.
"""
from datetime import UTC, datetime

from .base import BaseStage, StageResult
from ..models import ModelMetadata, ProjectContext


class ProblemFramingStage(BaseStage):
    """Generate draft ProblemFraming and ConceptModel from ProjectContext.

    Inputs:
        project_id: str

    Outputs:
        StageResult with draft ProblemFraming (draft_artifact)
        ConceptModel stored in extra_data["concept_model"]
    """

    def execute(self, *, project_id: str, **kwargs) -> StageResult:
        errors = self.validate_inputs(project_id=project_id)
        if errors:
            return StageResult(
                stage_name="problem-framing",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                prompts=[],
                validation_errors=errors,
            )

        # Load the approved ProjectContext
        context = self.persistence_service.load_artifact("ProjectContext", project_id, ProjectContext)
        if context is None:
            return StageResult(
                stage_name="problem-framing",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                prompts=[],
                validation_errors=[f"ProjectContext not found for project '{project_id}'"],
            )

        # Generate draft ProblemFraming and ConceptModel
        framing, concept_model, metadata = self.model_service.generate_problem_framing(context)

        # Set project_id on both artifacts
        framing.project_id = project_id
        concept_model.project_id = project_id

        # Persist both artifacts
        self.persistence_service.save_artifact(framing, project_id, "ProblemFraming")
        self.persistence_service.save_artifact(concept_model, project_id, "ConceptModel")

        return StageResult(
            stage_name="problem-framing",
            draft_artifact=framing,
            metadata=metadata,
            prompts=[
                "Review the problem statement and refine if needed.",
                "Edit goals to align with your research objectives.",
                "Adjust scope (in/out) to clarify boundaries.",
                "Review extracted concepts and relations in the concept model.",
            ],
            extra_data={"concept_model": concept_model},
        )

    def validate_inputs(self, *, project_id: str, **_) -> list[str]:
        errors: list[str] = []
        if not project_id or not project_id.strip():
            errors.append("project_id must be a non-empty string")
        if not self.persistence_service.project_exists(project_id):
            errors.append(f"Project '{project_id}' does not exist")
        return errors
