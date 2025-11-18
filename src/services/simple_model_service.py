"""A simple, dependency-free ModelService implementation for local testing.

This implementation doesn't call any external APIs. It generates reasonable
placeholders to enable an end-to-end demo.
"""
from datetime import UTC, datetime
from typing import List, Optional, Tuple
import re
import uuid

from .model_service import ModelService
from ..models import (
    Concept,
    ConceptModel,
    DatabaseQueryPlan,
    ModelMetadata,
    ProblemFraming,
    ProjectContext,
    ResearchQuestionSet,
    ScreeningChecklist,
    ScreeningCriteria,
    SearchConceptBlocks,
    StrategyPackage,
)


def _title_from_text(text: str) -> str:
    # Naive title generator: take first sentence, title-case it, truncate
    first_sentence = re.split(r"[.!?]", text.strip())[0]
    words = first_sentence.strip()[:120]
    title = words.title()
    return title[:80] or "Untitled Project"


def _extract_keywords(text: str) -> list[str]:
    # Very naive keyword extraction: select alphanumeric words longer than 4 chars
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]{4,}", text.lower())
    # Deduplicate preserving order
    seen = set()
    keywords: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            keywords.append(t)
    return keywords[:10]


class SimpleModelService(ModelService):
    """Simple local implementation useful for tests and demos."""

    def _meta(self, notes: Optional[str] = None) -> ModelMetadata:
        return ModelMetadata(
            model_name="simple-local",
            mode="offline",
            prompt_version=None,
            generated_at=datetime.now(UTC),
            notes=notes,
        )

    def suggest_project_context(self, raw_idea: str) -> Tuple[ProjectContext, ModelMetadata]:
        project_id = f"project_{uuid.uuid4().hex[:8]}"
        title = _title_from_text(raw_idea)
        keywords = _extract_keywords(raw_idea)
        ctx = ProjectContext(
            id=project_id,
            title=title,
            short_description=raw_idea.strip(),
            discipline=None,
            subfield=None,
            application_area=None,
            constraints={},
            initial_keywords=keywords,
            model_metadata=None,
        )
        meta = self._meta("Initial ProjectContext suggested from raw idea")
        ctx.model_metadata = meta
        return ctx, meta

    def generate_problem_framing(self, context: ProjectContext) -> Tuple[ProblemFraming, ConceptModel, ModelMetadata]:
        """Generate draft ProblemFraming and ConceptModel from ProjectContext."""
        # Naive problem statement
        problem_statement = (
            f"The research aims to investigate {context.title.lower()} "
            f"by examining key factors, relationships, and outcomes."
        )

        # Simple goals derived from keywords
        goals = [
            f"Understand the role of {kw}" for kw in context.initial_keywords[:3]
        ] if context.initial_keywords else ["Explore the problem domain"]

        # Scope
        scope_in = ["Academic literature", "Empirical studies", "Recent publications (last 10 years)"]
        scope_out = ["Non-peer-reviewed sources", "Opinion pieces"]

        framing = ProblemFraming(
            project_id=context.id,
            problem_statement=problem_statement,
            goals=goals,
            scope_in=scope_in,
            scope_out=scope_out,
            stakeholders=["Researchers", "Practitioners"],
        )

        # Naive concept extraction: use first few keywords as concepts
        concepts = [
            Concept(
                id=f"concept_{i}",
                label=kw.title(),
                description=f"Key concept: {kw}",
                type="domain_concept"
            )
            for i, kw in enumerate(context.initial_keywords[:5])
        ] if context.initial_keywords else []

        concept_model = ConceptModel(
            project_id=context.id,
            concepts=concepts,
            relations=[],
        )

        meta = self._meta("Generated ProblemFraming and ConceptModel from ProjectContext")
        framing.model_metadata = meta
        concept_model.model_metadata = meta

        return framing, concept_model, meta

    # The remaining methods are placeholders to satisfy the interface; they raise
    # NotImplementedError for now until later stages are built.

    def generate_research_questions(self, framing: ProblemFraming, concepts: ConceptModel) -> Tuple[ResearchQuestionSet, ModelMetadata]:
        raise NotImplementedError

    def expand_search_terms(self, concepts: ConceptModel, rqs: ResearchQuestionSet) -> Tuple[SearchConceptBlocks, ModelMetadata]:
        raise NotImplementedError

    def build_database_queries(self, blocks: SearchConceptBlocks, db_names: List[str]) -> Tuple[DatabaseQueryPlan, ModelMetadata]:
        raise NotImplementedError

    def draft_screening_criteria(self, rqs: ResearchQuestionSet, blocks: SearchConceptBlocks) -> Tuple[ScreeningCriteria, Optional[ScreeningChecklist], ModelMetadata]:
        raise NotImplementedError

    def summarize_strategy(self, pkg: StrategyPackage) -> Tuple[str, ModelMetadata]:
        raise NotImplementedError
