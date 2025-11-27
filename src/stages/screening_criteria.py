"""Stage 5: Screening Criteria Generation.

Generates PRISMA-aligned inclusion/exclusion criteria based on prior artifacts:
- ProblemFraming (goals, scope)
- ConceptModel (PICO elements)
- ResearchQuestionSet (research focus)
- DatabaseQueryPlan (optional complexity-informed adjustments)

Uses deterministic extraction (no LLM calls) for fast, predictable criteria generation.
"""
from datetime import UTC, datetime
from typing import List, Set
import logging

from .base import BaseStage, StageResult
from ..models import (
    ModelMetadata,
    ProblemFraming,
    ConceptModel,
    ResearchQuestionSet,
    ScreeningCriteria,
    DatabaseQueryPlan,
    Concept,
)

logger = logging.getLogger(__name__)


class ScreeningCriteriaStage(BaseStage):
    """Generate PRISMA-aligned ScreeningCriteria artifact using deterministic PICO extraction.

    Inputs:
        project_id: str
        refine_with_queries: bool - whether to adjust based on query complexity
        include_study_designs: bool - add study design filters (default True)

    Output:
        ScreeningCriteria in StageResult.draft_artifact
    """

    def execute(
        self,
        *,
        project_id: str,
        refine_with_queries: bool = True,
        include_study_designs: bool = True,
        **kwargs
    ) -> StageResult:
        """Execute screening criteria generation."""

        errors = self.validate_inputs(project_id=project_id)
        if errors:
            return StageResult(
                stage_name="screening-criteria",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                validation_errors=errors,
            )

        # Load required artifacts
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

        logger.info(f"Generating screening criteria for project {project_id}")

        # Extract PICO elements from ConceptModel
        pico_elements = self._extract_pico_elements(concept_model)

        # Generate inclusion criteria
        inclusion = self._generate_inclusion_criteria(
            framing,
            pico_elements,
            rq_set,
            include_study_designs
        )

        # Generate exclusion criteria
        exclusion = self._generate_exclusion_criteria(
            framing,
            pico_elements,
            include_study_designs
        )

        # Optional refinement using query complexity
        if refine_with_queries and query_plan is not None:
            self._refine_with_query_complexity(inclusion, exclusion, query_plan)

        # Create ScreeningCriteria artifact
        criteria = ScreeningCriteria(
            project_id=project_id,
            inclusion_criteria=inclusion,
            exclusion_criteria=exclusion,
            model_metadata=ModelMetadata(
                model_name=self.model_service.model_name,
                mode="deterministic_pico_extraction",
                generated_at=datetime.now(UTC),
                notes="Generated using deterministic PICO extraction (no LLM)"
            ),
        )

        self.persistence_service.save_artifact(criteria, project_id, "ScreeningCriteria")

        # Generate user-friendly prompts
        prompts = [
            f"✅ Generated {len(inclusion)} inclusion criteria from PICO elements",
            f"✅ Generated {len(exclusion)} exclusion criteria",
            "💡 Review criteria and adjust for your specific domain",
            "💡 Consider adding temporal range (e.g., published after 2020)",
            "💡 Add language filters if needed (currently defaults to English)",
        ]

        if pico_elements["population"]:
            prompts.append(f"   Population: {', '.join(pico_elements['population'][:3])}")
        if pico_elements["intervention"]:
            prompts.append(f"   Intervention: {', '.join(pico_elements['intervention'][:3])}")

        return StageResult(
            stage_name="screening-criteria",
            draft_artifact=criteria,
            metadata=criteria.model_metadata,
            prompts=prompts,
            validation_errors=[],
        )

    def _extract_pico_elements(self, concept_model: ConceptModel) -> dict:
        """Extract PICO elements from ConceptModel.

        Returns dict with keys: population, intervention, comparison, outcome, context, method
        """
        pico = {
            "population": [],
            "intervention": [],
            "comparison": [],
            "outcome": [],
            "context": [],
            "method": [],
            "other": []
        }

        for concept in concept_model.concepts:
            concept_type = concept.type.lower()

            if concept_type in ("population", "participant", "sample"):
                pico["population"].append(concept.label)
            elif concept_type in ("intervention", "treatment", "exposure"):
                pico["intervention"].append(concept.label)
            elif concept_type in ("comparison", "control", "comparator"):
                pico["comparison"].append(concept.label)
            elif concept_type in ("outcome", "result", "effect"):
                pico["outcome"].append(concept.label)
            elif concept_type in ("context", "setting", "environment"):
                pico["context"].append(concept.label)
            elif concept_type in ("method", "methodology", "approach"):
                pico["method"].append(concept.label)
            else:
                pico["other"].append(concept.label)

        logger.info(f"Extracted PICO: {sum(len(v) for v in pico.values())} concepts across {len([k for k, v in pico.items() if v])} categories")
        return pico

    def _generate_inclusion_criteria(
        self,
        framing: ProblemFraming,
        pico: dict,
        rq_set: ResearchQuestionSet,
        include_study_designs: bool
    ) -> List[str]:
        """Generate inclusion criteria from PICO elements and research questions."""

        inclusion = []

        # 1. Population criteria
        if pico["population"]:
            pop_str = ", ".join(pico["population"][:5])
            inclusion.append(f"Studies focusing on: {pop_str}")

        # 2. Intervention/Exposure criteria
        if pico["intervention"]:
            intervention_str = ", ".join(pico["intervention"][:5])
            inclusion.append(f"Studies evaluating or implementing: {intervention_str}")

        # 3. Outcome criteria
        if pico["outcome"]:
            outcome_str = ", ".join(pico["outcome"][:5])
            inclusion.append(f"Studies reporting outcomes related to: {outcome_str}")

        # 4. Method criteria
        if pico["method"]:
            method_str = ", ".join(pico["method"][:4])
            inclusion.append(f"Studies using methods: {method_str}")

        # 5. Context criteria
        if pico["context"]:
            context_str = ", ".join(pico["context"][:3])
            inclusion.append(f"Studies conducted in contexts: {context_str}")

        # 6. Research question alignment
        if rq_set.questions:
            primary_rqs = [q.text for q in rq_set.questions if q.priority == "must_have"]
            if primary_rqs:
                inclusion.append(f"Studies addressing primary research questions (n={len(primary_rqs)})")

        # 7. Scope inclusion
        if framing.scope_in:
            for scope_item in framing.scope_in[:3]:
                inclusion.append(f"Studies within scope: {scope_item}")

        # 8. Study design filters (PRISMA-aligned)
        if include_study_designs:
            inclusion.extend([
                "Peer-reviewed publications (journal articles, conference papers)",
                "Original research studies (empirical data)",
                "Full-text available for quality assessment"
            ])

        # 9. Language filter
        inclusion.append("Published in English (or specify other languages as needed)")

        # 10. Publication type
        inclusion.append("Scholarly publications (excludes preprints unless from reputable archives)")

        return inclusion

    def _generate_exclusion_criteria(
        self,
        framing: ProblemFraming,
        pico: dict,
        include_study_designs: bool
    ) -> List[str]:
        """Generate exclusion criteria based on scope and PICO elements."""

        exclusion = []

        # 1. Non-scholarly sources
        exclusion.extend([
            "Non-scholarly sources (blogs, forums, social media, press releases)",
            "Opinion pieces, editorials, and commentaries without empirical data",
            "Books, book chapters, and theses (unless specifically relevant)"
        ])

        # 2. Scope exclusions
        if framing.scope_out:
            for scope_item in framing.scope_out[:5]:
                exclusion.append(f"Studies outside scope: {scope_item}")

        # 3. Study design exclusions
        if include_study_designs:
            exclusion.extend([
                "Studies without clear methodology",
                "Studies with insufficient detail to assess quality",
                "Duplicate publications (same study, different venues)"
            ])

        # 4. Population mismatch
        if pico["population"]:
            exclusion.append("Studies with populations not matching inclusion criteria")

        # 5. Intervention/Method mismatch
        if pico["intervention"]:
            exclusion.append("Studies not evaluating specified interventions or methods")

        # 6. Language and access
        exclusion.extend([
            "Studies not available in full text",
            "Retracted publications",
            "Studies with major methodological flaws (to be determined during quality assessment)"
        ])

        # 7. Relevance
        exclusion.append("Studies not addressing the research questions despite keyword matches")

        return exclusion

    def _refine_with_query_complexity(
        self,
        inclusion: List[str],
        exclusion: List[str],
        query_plan: DatabaseQueryPlan
    ):
        """Refine criteria based on query complexity analysis.

        Modifies inclusion and exclusion lists in place.
        """

        # Analyze query complexity
        broad_queries = [
            q for q in query_plan.queries
            if q.complexity_analysis and q.complexity_analysis.get("complexity_level") in ("very_broad", "broad")
        ]

        narrow_queries = [
            q for q in query_plan.queries
            if q.complexity_analysis and q.complexity_analysis.get("complexity_level") in ("very_narrow", "narrow")
        ]

        # If queries are very broad, add narrowing criteria
        if len(broad_queries) >= len(query_plan.queries) / 2:
            exclusion.append("General surveys or overviews unless they specifically address the intervention-outcome relationship")
            logger.info("Added narrowing exclusion criteria due to broad queries")

        # If queries are very narrow, add note about specificity
        if len(narrow_queries) >= len(query_plan.queries) / 2:
            inclusion.append("Studies must closely match the specific focus defined in research questions")
            logger.info("Added specificity requirement due to narrow queries")

