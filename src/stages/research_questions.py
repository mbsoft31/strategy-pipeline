"""Stage 2: Research question generation.

Generates a draft ResearchQuestionSet from approved ProblemFraming + ConceptModel.
"""
from datetime import UTC, datetime

from .base import BaseStage, StageResult
from ..models import ModelMetadata, ProblemFraming, ConceptModel, Concept

class ResearchQuestionStage(BaseStage):
    """Generate draft ResearchQuestionSet from ProblemFraming + ConceptModel.

    Inputs:
        project_id: str
    Output:
        StageResult with ResearchQuestionSet in draft_artifact.
    Preconditions:
        - ProblemFraming approved
        - ConceptModel approved
    """
    def execute(self, *, project_id: str, **kwargs) -> StageResult:
        errors = self.validate_inputs(project_id=project_id)
        if errors:
            return StageResult(
                stage_name="research-questions",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                prompts=[],
                validation_errors=errors,
            )

        framing = self.persistence_service.load_artifact("ProblemFraming", project_id, ProblemFraming)
        concept_model = self.persistence_service.load_artifact("ConceptModel", project_id, ConceptModel)
        # If concept_model concepts contain dicts, coerce to Concept dataclasses
        if concept_model and concept_model.concepts and isinstance(concept_model.concepts[0], dict):
            concept_model.concepts = [
                Concept(
                    id=d.get('id'),
                    label=d.get('label'),
                    description=d.get('description'),
                    type=d.get('type')
                ) for d in concept_model.concepts if isinstance(d, dict)
            ]
        if framing is None or concept_model is None:
            return StageResult(
                stage_name="research-questions",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                validation_errors=["ProblemFraming or ConceptModel missing"],
            )
        # Call model service
        rq_set, meta = self.model_service.generate_research_questions(framing, concept_model)
        # Persist
        self.persistence_service.save_artifact(rq_set, project_id, "ResearchQuestionSet")
        return StageResult(
            stage_name="research-questions",
            draft_artifact=rq_set,
            metadata=meta,
            prompts=[
                "Review each research question for clarity and specificity.",
                "Adjust priority (must_have vs nice_to_have).",
                "Ensure types align (descriptive/explanatory/evaluative/design).",
            ],
        )

    def validate_inputs(self, *, project_id: str, **_) -> list[str]:
        errors: list[str] = []
        if not project_id or not project_id.strip():
            errors.append("project_id must be a non-empty string")
        if not self.persistence_service.project_exists(project_id):
            errors.append(f"Project '{project_id}' does not exist")
        return errors
