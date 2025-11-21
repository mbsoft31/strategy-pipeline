"""Stage 5: Screening Criteria Generation.

Generates preliminary inclusion/exclusion criteria based on prior artifacts:
- ProblemFraming
- ConceptModel
- ResearchQuestionSet
- DatabaseQueryPlan (optional complexity-informed adjustments)

This is a placeholder minimal implementation to scaffold the stage.
"""
from datetime import UTC, datetime
from typing import List

from .base import BaseStage, StageResult
from ..models import (
    ModelMetadata,
    ProblemFraming,
    ConceptModel,
    ResearchQuestionSet,
    ScreeningCriteria,
    DatabaseQueryPlan,
)


class ScreeningCriteriaStage(BaseStage):
    """Generate ScreeningCriteria artifact.

    Inputs:
        project_id: str
        refine_with_queries: bool - whether to adjust based on query complexity

    Output:
        ScreeningCriteria in StageResult.draft_artifact
    """

    def execute(self, *, project_id: str, refine_with_queries: bool = True, **kwargs) -> StageResult:
        errors = self.validate_inputs(project_id=project_id)
        if errors:
            return StageResult(
                stage_name="screening-criteria",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                validation_errors=errors,
            )

        framing = self.persistence_service.load_artifact("ProblemFraming", project_id, ProblemFraming)
        concept_model = self.persistence_service.load_artifact("ConceptModel", project_id, ConceptModel)
        rq_set = self.persistence_service.load_artifact("ResearchQuestionSet", project_id, ResearchQuestionSet)
        query_plan = self.persistence_service.load_artifact("DatabaseQueryPlan", project_id, DatabaseQueryPlan)

        missing = []
        if framing is None:
            missing.append("ProblemFraming")
        if concept_model is None:
            missing.append("ConceptModel")
        if rq_set is None:
            missing.append("ResearchQuestionSet")
        if missing:
            return StageResult(
                stage_name="screening-criteria",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                validation_errors=[f"Missing required prior artifacts: {', '.join(missing)}"],
            )

        inclusion: List[str] = []
        exclusion: List[str] = []

        # Basic inclusion criteria derived from goals & concepts
        if framing.goals:
            inclusion.append(f"Studies addressing goals: {', '.join(framing.goals[:3])}")
        if concept_model.concepts:
            pop_concepts = [c.label for c in concept_model.concepts if c.type.lower() == "population"]
            if pop_concepts:
                inclusion.append(f"Population includes: {', '.join(pop_concepts[:5])}")
        if rq_set.questions:
            inclusion.append(f"Addresses at least one primary research question (n={len(rq_set.questions)})")

        # Placeholder methodological inclusion
        methods = [c.label for c in concept_model.concepts if c.type.lower() in ("method", "approach")]
        if methods:
            inclusion.append(f"Utilizes method categories: {', '.join(methods[:4])}")

        # Basic exclusion examples
        exclusion.extend([
            "Non-scholarly sources (blogs, forums, unrefereed opinions)",
            "Studies lacking full text (if full-text screening stage)",
            "Irrelevant application domains outside stated scope"
        ])

        # Optional refinement using query complexity
        if refine_with_queries and query_plan is not None:
            broad_queries = [q for q in query_plan.queries if q.complexity_analysis and q.complexity_analysis.get("complexity_level") in ("very_broad", "broad")]
            if broad_queries:
                exclusion.append("Exclude overly general surveys unless directly addressing specified intervention/outcome relationship.")

        criteria = ScreeningCriteria(
            project_id=project_id,
            inclusion_criteria=inclusion,
            exclusion_criteria=exclusion,
            model_metadata=ModelMetadata(model_name=self.model_service.model_name, mode=self.model_service.mode, generated_at=datetime.now(UTC)),
        )

        self.persistence_service.save_artifact(criteria, project_id, "ScreeningCriteria")

        return StageResult(
            stage_name="screening-criteria",
            draft_artifact=criteria,
            metadata=criteria.model_metadata,
            prompts=[
                "Review inclusion criteria for specificity and add domain filters (e.g., study design).",
                "Consider adding temporal range (e.g., last 5 years).",
                "Refine exclusion criteria to minimize irrelevant high-volume studies.",
            ],
            validation_errors=[],
        )
