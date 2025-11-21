"""Stage 3: Search concept expansion.

Generates SearchConceptBlocks from approved ConceptModel + ResearchQuestionSet.
Each block represents a conceptual dimension with synonyms, related terms, and exclusions.
"""
from datetime import UTC, datetime

from .base import BaseStage, StageResult
from ..models import ModelMetadata, ConceptModel, ResearchQuestionSet, Concept


class SearchConceptExpansionStage(BaseStage):
    """Generate SearchConceptBlocks from ConceptModel + ResearchQuestionSet.

    Inputs:
        project_id: str
    Output:
        StageResult with SearchConceptBlocks in draft_artifact.
    Preconditions:
        - ConceptModel approved
        - ResearchQuestionSet approved
    """

    def execute(self, *, project_id: str, **kwargs) -> StageResult:
        errors = self.validate_inputs(project_id=project_id)
        if errors:
            return StageResult(
                stage_name="search-concept-expansion",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                prompts=[],
                validation_errors=errors,
            )

        concept_model = self.persistence_service.load_artifact("ConceptModel", project_id, ConceptModel)
        rq_set = self.persistence_service.load_artifact("ResearchQuestionSet", project_id, ResearchQuestionSet)

        # Handle dict-to-dataclass conversion if needed
        if concept_model and concept_model.concepts and isinstance(concept_model.concepts[0], dict):
            concept_model.concepts = [
                Concept(
                    id=d.get('id'),
                    label=d.get('label'),
                    description=d.get('description'),
                    type=d.get('type')
                ) for d in concept_model.concepts if isinstance(d, dict)
            ]

        if concept_model is None or rq_set is None:
            return StageResult(
                stage_name="search-concept-expansion",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                validation_errors=["ConceptModel or ResearchQuestionSet missing"],
            )

        # Call model service
        blocks, meta = self.model_service.expand_search_terms(concept_model, rq_set)

        # Persist
        self.persistence_service.save_artifact(blocks, project_id, "SearchConceptBlocks")

        return StageResult(
            stage_name="search-concept-expansion",
            draft_artifact=blocks,
            metadata=meta,
            prompts=[
                "Review each concept block for completeness.",
                "Add domain-specific synonyms or narrower terms.",
                "Specify terms to exclude if needed.",
                "Consider Boolean operators for combining blocks.",
            ],
        )

    def validate_inputs(self, *, project_id: str, **_) -> list[str]:
        errors: list[str] = []
        if not project_id or not project_id.strip():
            errors.append("project_id must be a non-empty string")
        if not self.persistence_service.project_exists(project_id):
            errors.append(f"Project '{project_id}' does not exist")
        return errors

