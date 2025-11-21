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
    ResearchQuestion,
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

    def generate_research_questions(self, framing: ProblemFraming, concepts: ConceptModel) -> Tuple[ResearchQuestionSet, ModelMetadata]:
        """Heuristic generation of 3-5 research questions from framing + concepts."""
        base_terms = [c.label for c in concepts.concepts[:5]] or ["Core Phenomenon"]
        qs: List[str] = []
        # Simple templates
        if framing.problem_statement:
            qs.append(f"How does {base_terms[0]} relate to outcomes described in the problem statement?")
        if len(base_terms) >= 2:
            qs.append(f"What factors influence {base_terms[1]} adoption or effectiveness?")
        if len(base_terms) >= 3:
            qs.append(f"What mechanisms link {base_terms[2]} to observed performance or quality measures?")
        if len(base_terms) >= 4:
            qs.append(f"How can {base_terms[3]} be optimized to improve reliability or consistency?")
        if len(base_terms) >= 5:
            qs.append(f"What are the barriers and facilitators to integrating {base_terms[4]} in practice?")
        # Build objects
        rq_objects = []
        for i, text in enumerate(qs):
            rq_objects.append(
                ResearchQuestion(
                    id=f"rq_{i}",
                    text=text,
                    type="descriptive" if i == 0 else "explanatory",
                    linked_concept_ids=[c.id for c in concepts.concepts[: min(2, len(concepts.concepts))]],
                    priority="must_have" if i < 3 else "nice_to_have",
                )
            )
        rq_set = ResearchQuestionSet(project_id=framing.project_id, questions=rq_objects)
        meta = self._meta("Generated ResearchQuestionSet heuristically")
        rq_set.model_metadata = meta
        return rq_set, meta

    # The remaining methods are placeholders to satisfy the interface; they raise
    # NotImplementedError for now until later stages are built.

    def expand_search_terms(self, concepts: ConceptModel, rqs: ResearchQuestionSet) -> Tuple[SearchConceptBlocks, ModelMetadata]:
        """Heuristic search term expansion."""
        from ..models import SearchConceptBlock
        import uuid

        blocks_list = []
        for concept in concepts.concepts[:6]:  # Limit to 6 main concepts
            # Simple heuristic: use concept label + basic variations
            label = concept.label
            terms = [label, label.lower(), label.replace(" ", "-")]

            # Add plural if applicable
            if not label.endswith('s'):
                terms.append(label + 's')

            block = SearchConceptBlock(
                id=str(uuid.uuid4()),
                label=label,
                description=concept.description,
                terms_included=list(set(terms)),  # Deduplicate
                terms_excluded=[]
            )
            blocks_list.append(block)

        search_blocks = SearchConceptBlocks(
            project_id=concepts.project_id,
            blocks=blocks_list
        )

        meta = self._meta("Generated SearchConceptBlocks heuristically")
        search_blocks.model_metadata = meta
        return search_blocks, meta

    def build_database_queries(self, blocks: SearchConceptBlocks, db_names: List[str]) -> Tuple[DatabaseQueryPlan, ModelMetadata]:
        """Generate database queries using Anti-Hallucination syntax engine."""
        from ..models import DatabaseQuery, DatabaseQueryPlan
        from ..search.models import QueryPlan as SyntaxQueryPlan, ConceptBlock as SyntaxConceptBlock, FieldTag
        from ..search.builder import get_builder
        import uuid

        queries = []

        # Convert SearchConceptBlocks to syntax engine format
        syntax_plan = SyntaxQueryPlan()
        for block in blocks.blocks:
            syntax_block = SyntaxConceptBlock(label=block.label)

            # Add included terms
            for term in block.terms_included:
                syntax_block.add_term(term, FieldTag.KEYWORD)

            # Add excluded terms (Anti-Hallucination layer)
            for ex_term in block.terms_excluded:
                syntax_block.add_excluded_term(ex_term, FieldTag.KEYWORD)

            syntax_plan.blocks.append(syntax_block)

        # Generate queries using syntax engine (guaranteed valid syntax)
        for db_name in db_names:
            try:
                builder = get_builder(db_name.lower())
                query_string = builder.build(syntax_plan)

                # Add database-specific notes
                notes = self._get_database_notes(db_name.lower())

                queries.append(DatabaseQuery(
                    id=f"query_{db_name}_{uuid.uuid4().hex[:6]}",
                    database_name=db_name.lower(),
                    query_blocks=[b.id for b in blocks.blocks],
                    boolean_query_string=query_string,
                    notes=notes
                ))
            except ValueError as e:
                # Database not supported by syntax engine
                queries.append(DatabaseQuery(
                    id=f"query_{db_name}_{uuid.uuid4().hex[:6]}",
                    database_name=db_name.lower(),
                    query_blocks=[b.id for b in blocks.blocks],
                    boolean_query_string=f"# Unsupported database: {db_name}",
                    notes=f"Syntax engine doesn't support {db_name}: {str(e)}"
                ))

        plan = DatabaseQueryPlan(project_id=blocks.project_id, queries=queries)
        meta = self._meta("Generated queries using Anti-Hallucination syntax engine")
        plan.model_metadata = meta
        return plan, meta

    def _get_database_notes(self, db_name: str) -> str:
        """Return database-specific usage notes."""
        notes_map = {
            "pubmed": "Syntax-only: Copy to PubMed UI. Consider adding MeSH terms.",
            "scopus": "Syntax-only: Requires Scopus API key. Copy to Scopus UI.",
            "wos": "Syntax-only: Requires Web of Science access. Copy to WoS UI.",
            "openalex": "Executable via SearchService",
            "arxiv": "Executable via SearchService",
            "semanticscholar": "Executable via SearchService",
            "crossref": "Executable via SearchService"
        }
        return notes_map.get(db_name, "Generated using syntax engine")

    def draft_screening_criteria(self, rqs: ResearchQuestionSet, blocks: SearchConceptBlocks) -> Tuple[ScreeningCriteria, Optional[ScreeningChecklist], ModelMetadata]:
        raise NotImplementedError

    def summarize_strategy(self, pkg: StrategyPackage) -> Tuple[str, ModelMetadata]:
        raise NotImplementedError
