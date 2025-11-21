"""Enhanced ModelService with LLM integration and validation.

This service implements the Draft → Critique → Refine → Validate pattern
for generating high-quality research artifacts.
"""

import uuid
import logging
from typing import Tuple, List

from .model_service import ModelService
from .llm_provider import get_llm_provider
from .validation_service import ValidationService, ValidationReport
from .prompts import (
    SYSTEM_PROMPT_METHODOLOGIST,
    SYSTEM_PROMPT_CRITIC,
    PROMPT_STAGE0_CONTEXT,
    PROMPT_STAGE1_CRITIQUE,
    PROMPT_STAGE1_REFINE, SYSTEM_PROMPT_LIBRARIAN,
)
from ..models import (
    ProjectContext,
    ProblemFraming,
    ConceptModel,
    Concept,
    ModelMetadata,
    ResearchQuestionSet,
    ResearchQuestion,
    SearchConceptBlocks,
    DatabaseQueryPlan,
    ScreeningCriteria,
    ScreeningChecklist,
    StrategyPackage,
)
from ..config import get_config
from ..utils.exceptions import LLMProviderError, ValidationError

logger = logging.getLogger(__name__)


class IntelligentModelService(ModelService):
    """Enhanced model service with LLM and validation capabilities.

    This service:
    1. Uses real LLMs (OpenAI) or Mock for generation
    2. Implements critique loop (Draft → Critique → Refine)
    3. Validates terms against OpenAlex to prevent hallucinations
    4. Stores validation reports for transparency
    """

    def __init__(self):
        """Initialize with LLM provider and validation service."""
        self.provider = get_llm_provider()
        self.validator = ValidationService()
        self.config = get_config()

        logger.info(
            f"IntelligentModelService initialized with provider: {self.config.llm.provider}"
        )

    def suggest_project_context(
        self, raw_idea: str
    ) -> Tuple[ProjectContext, ModelMetadata]:
        """Stage 0: Generate project context from raw idea using LLM.

        Args:
            raw_idea: Unstructured research idea text

        Returns:
            Tuple of (ProjectContext, ModelMetadata)

        Raises:
            LLMProviderError: On LLM generation failures
        """
        logger.info("Generating project context from raw idea...")

        try:
            # Generate with LLM
            prompt = PROMPT_STAGE0_CONTEXT.format(raw_idea=raw_idea)
            raw_response = self.provider.generate(SYSTEM_PROMPT_METHODOLOGIST, prompt)
            data = self.provider.clean_json_response(raw_response)

            # Create project ID
            project_id = f"project_{uuid.uuid4().hex[:8]}"

            # Extract data with fallbacks
            draft = ProjectContext(
                id=project_id,
                title=data.get("title", "Untitled Research Project"),
                short_description=data.get("short_description", raw_idea[:500]),
                discipline=data.get("discipline", None),
                subfield=None,
                application_area=None,
                initial_keywords=data.get("initial_keywords", []),
                constraints=data.get("constraints", {}),
            )

            # Create metadata
            meta = ModelMetadata(
                model_name=str(self.config.llm.provider.value),
                mode="generation",
                prompt_version="1.0",
                notes="Generated from raw idea using LLM"
            )

            draft.model_metadata = meta

            logger.info(f"Project context generated: {draft.title}")
            return draft, meta

        except Exception as e:
            logger.error(f"Failed to generate project context: {e}")
            # Fallback to simple extraction
            logger.warning("Falling back to simple extraction")
            return self._fallback_project_context(raw_idea)

    def generate_problem_framing(
        self, context: ProjectContext
    ) -> Tuple[ProblemFraming, ConceptModel, ModelMetadata]:
        """Stage 1: Generate problem framing with critique loop and validation.

        Implements: Draft → Critique → Refine → Validate

        Args:
            context: Approved ProjectContext

        Returns:
            Tuple of (ProblemFraming, ConceptModel, ModelMetadata)
        """
        logger.info(f"Generating problem framing for: {context.title}")

        try:
            # Step 1: Generate critique of initial context
            critique_data = self._critique_context(context)
            critique_text = critique_data.get("critique_summary", "")
            feasibility_score = critique_data.get("feasibility_score", 5)

            logger.info(f"Critique complete. Feasibility score: {feasibility_score}/10")

            # Step 2: Refine based on critique
            refine_data = self._refine_framing(context, critique_text)

            # Step 3: Extract concepts
            concepts_list, concept_labels = self._extract_concepts(
                refine_data, context.id
            )

            # Step 4: Validate concepts against OpenAlex
            validation_report = self._validate_concepts(concept_labels)

            # Step 5: Assemble final critique report
            final_critique = self._assemble_critique_report(
                critique_text, feasibility_score, validation_report
            )

            # Step 6: Create artifacts
            framing = ProblemFraming(
                project_id=context.id,
                problem_statement=refine_data.get("problem_statement", ""),
                research_gap=refine_data.get("research_gap", ""),
                goals=refine_data.get("goals", []),
                scope_in=refine_data.get("scope_in", []),
                scope_out=refine_data.get("scope_out", []),
                stakeholders=[],  # Not in current prompt
                critique_report=final_critique,
            )

            concept_model = ConceptModel(
                project_id=context.id,
                concepts=concepts_list,
                relations=[],  # Relations generation can be added later
            )

            # Create metadata
            meta = ModelMetadata(
                model_name=str(self.config.llm.provider.value),
                mode="critique-refine-validate",
                prompt_version="1.0",
                notes=f"Critique loop with OpenAlex validation. "
                      f"Validated {len(concept_labels)} concepts."
            )

            framing.model_metadata = meta
            concept_model.model_metadata = meta

            logger.info(
                f"Problem framing complete. {len(concepts_list)} concepts extracted. "
                f"Validation: {validation_report.summary}"
            )

            return framing, concept_model, meta

        except Exception as e:
            logger.error(f"Failed to generate problem framing: {e}")
            logger.warning("Falling back to simple generation")
            return self._fallback_problem_framing(context)

    def _critique_context(self, context: ProjectContext) -> dict:
        """Generate critique of project context.

        Args:
            context: ProjectContext to critique

        Returns:
            Dictionary with critique data
        """
        prompt = PROMPT_STAGE1_CRITIQUE.format(
            title=context.title,
            description=context.short_description
        )

        raw_response = self.provider.generate(SYSTEM_PROMPT_CRITIC, prompt)
        return self.provider.clean_json_response(raw_response)

    def _refine_framing(self, context: ProjectContext, critique: str) -> dict:
        """Refine problem framing based on critique.

        Args:
            context: Original ProjectContext
            critique: Critique text

        Returns:
            Dictionary with refined framing data
        """
        prompt = PROMPT_STAGE1_REFINE.format(
            context_str=context.short_description,
            critique_str=critique
        )

        raw_response = self.provider.generate(SYSTEM_PROMPT_METHODOLOGIST, prompt)
        return self.provider.clean_json_response(raw_response)

    def _extract_concepts(
        self, refine_data: dict, project_id: str
    ) -> Tuple[List[Concept], List[str]]:
        """Extract concepts from refined framing data.

        Args:
            refine_data: Refined framing dictionary
            project_id: Project ID for concepts

        Returns:
            Tuple of (concept objects list, concept labels list)
        """
        concepts_list = []
        concept_labels = []

        for c in refine_data.get("key_concepts", []):
            label = c.get("label", "Unknown")
            concept_type = c.get("type", "Undefined")
            description = c.get("description", label)

            concept_labels.append(label)

            concepts_list.append(Concept(
                id=str(uuid.uuid4()),
                label=label,
                description=description,
                type=concept_type
            ))

        return concepts_list, concept_labels

    def _validate_concepts(self, concept_labels: List[str]) -> ValidationReport:
        """Validate concept labels against OpenAlex.

        Args:
            concept_labels: List of concept label strings

        Returns:
            ValidationReport
        """
        if not concept_labels:
            logger.warning("No concepts to validate")
            return ValidationReport(
                results={},
                total_terms=0,
                valid_count=0,
                warning_count=0,
                critical_count=0,
                summary="No concepts to validate"
            )

        try:
            return self.validator.validate_concept_list(concept_labels)
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            # Return empty report on failure
            return ValidationReport(
                results={},
                total_terms=len(concept_labels),
                valid_count=0,
                warning_count=0,
                critical_count=len(concept_labels),
                summary=f"Validation failed: {str(e)}"
            )

    def _assemble_critique_report(
        self, critique: str, score: int, validation_report: ValidationReport
    ) -> str:
        """Assemble final critique report with validation results.

        Args:
            critique: Original critique text
            score: Feasibility score
            validation_report: ValidationReport

        Returns:
            Complete critique report string
        """
        report_parts = [
            "="*70,
            "AI CRITIQUE REPORT",
            "="*70,
            "",
            f"Feasibility Score: {score}/10",
            "",
            "CRITIQUE:",
            critique,
            "",
            "="*70,
            "OPENALEX VALIDATION REPORT",
            "="*70,
            "",
            f"Summary: {validation_report.summary}",
            "",
            "Detailed Results:",
        ]

        # Add individual term results
        for term, result in validation_report.results.items():
            status_icon = {
                "ok": "✅",
                "warning": "⚠️",
                "critical": "❌"
            }.get(result.severity, "❓")

            report_parts.append(
                f"{status_icon} {term}: {result.hit_count} works found"
            )

            if result.suggestion:
                report_parts.append(f"   → {result.suggestion}")

            if result.sample_works:
                report_parts.append("   Sample works:")
                for work in result.sample_works[:2]:
                    report_parts.append(f"     • {work}")

        return "\n".join(report_parts)

    def _fallback_project_context(
        self, raw_idea: str
    ) -> Tuple[ProjectContext, ModelMetadata]:
        """Fallback for project context generation when LLM fails."""
        project_id = f"project_{uuid.uuid4().hex[:8]}"

        # Simple extraction
        title = raw_idea[:80].strip()
        if not title:
            title = "Untitled Research Project"

        context = ProjectContext(
            id=project_id,
            title=title,
            short_description=raw_idea[:500],
            discipline=None,
            initial_keywords=[],
            constraints={},
        )

        meta = ModelMetadata(
            model_name="fallback",
            mode="simple",
            notes="Generated using fallback (LLM unavailable)"
        )

        context.model_metadata = meta
        return context, meta

    def _fallback_problem_framing(
        self, context: ProjectContext
    ) -> Tuple[ProblemFraming, ConceptModel, ModelMetadata]:
        """Fallback for problem framing when LLM fails."""
        framing = ProblemFraming(
            project_id=context.id,
            problem_statement=f"Investigate {context.title}",
            research_gap="To be determined",
            goals=["Explore the problem domain"],
            scope_in=["Academic literature"],
            scope_out=["Non-academic sources"],
            critique_report="LLM unavailable - manual review required"
        )

        concept_model = ConceptModel(
            project_id=context.id,
            concepts=[],
            relations=[]
        )

        meta = ModelMetadata(
            model_name="fallback",
            mode="simple",
            notes="Generated using fallback (LLM unavailable)"
        )

        framing.model_metadata = meta
        concept_model.model_metadata = meta

        return framing, concept_model, meta

    # Placeholder methods for later stages
    def generate_research_questions(
        self, framing: ProblemFraming, concepts: ConceptModel
    ) -> Tuple[ResearchQuestionSet, ModelMetadata]:
        """Stage 2: Generate research questions from framing + concepts.

        Uses LLM prompt; falls back to heuristic if LLM fails.
        """
        try:
            from .prompts import PROMPT_STAGE2_RESEARCH_QUESTIONS, format_concepts_for_prompt, format_goals_for_prompt
            concept_str = format_concepts_for_prompt(concepts.concepts)
            goals_str = format_goals_for_prompt(framing.goals)
            prompt = PROMPT_STAGE2_RESEARCH_QUESTIONS.format(
                problem_statement=framing.problem_statement,
                goals=goals_str,
                concepts=concept_str
            )
            raw = self.provider.generate(SYSTEM_PROMPT_METHODOLOGIST, prompt)
            data = self.provider.clean_json_response(raw)
            questions_payload = data.get("questions", [])
            rq_objects: List[ResearchQuestion] = []
            for i, q in enumerate(questions_payload):
                rq_objects.append(
                    ResearchQuestion(
                        id=f"rq_{i}",
                        text=q.get("text", "Unnamed research question"),
                        type=q.get("type", "descriptive"),
                        linked_concept_ids=q.get("linked_concepts", [])[:4],
                        priority=q.get("priority", "must_have")
                    )
                )
            if not rq_objects:
                raise ValueError("LLM returned no questions")
            rq_set = ResearchQuestionSet(project_id=framing.project_id, questions=rq_objects)
            meta = ModelMetadata(
                model_name=str(self.config.llm.provider.value),
                mode="generation",
                prompt_version="2.0",
                notes="Generated research questions via LLM"
            )
            rq_set.model_metadata = meta
            return rq_set, meta
        except Exception as e:
            logger.error(f"LLM research question generation failed: {e}")
            logger.warning("Falling back to heuristic generation")
            # Fallback similar to SimpleModelService
            base_terms = [c.label for c in concepts.concepts[:5]] or ["Core Phenomenon"]
            texts: List[str] = []
            if framing.problem_statement:
                texts.append(f"How does {base_terms[0]} relate to outcomes described in the problem statement?")
            if len(base_terms) >= 2:
                texts.append(f"What factors influence {base_terms[1]} adoption or effectiveness?")
            if len(base_terms) >= 3:
                texts.append(f"What mechanisms link {base_terms[2]} to observed performance or quality measures?")
            if len(base_terms) >= 4:
                texts.append(f"How can {base_terms[3]} be optimized to improve reliability or consistency?")
            if len(base_terms) >= 5:
                texts.append(f"What are the barriers and facilitators to integrating {base_terms[4]} in practice?")
            rq_objects = []
            for i, text in enumerate(texts):
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
            meta = ModelMetadata(
                model_name=str(self.config.llm.provider.value),
                mode="fallback-heuristic",
                prompt_version="fallback",
                notes="Heuristic fallback for research questions"
            )
            rq_set.model_metadata = meta
            return rq_set, meta

    def expand_search_terms(
        self, concepts: ConceptModel, rqs: ResearchQuestionSet
    ) -> Tuple[SearchConceptBlocks, ModelMetadata]:
        """Stage 3: Expand search terms using LLM.

        Added robust handling for deserialized dict items and detailed debug logging.
        """
        try:
            # Reconstruct ResearchQuestion objects if persistence produced dicts
            from ..models import SearchConceptBlock, ResearchQuestion
            import uuid
            if rqs.questions and isinstance(rqs.questions[0], dict):
                reconstructed = []
                for idx, q in enumerate(rqs.questions):
                    if isinstance(q, dict):
                        reconstructed.append(
                            ResearchQuestion(
                                id=q.get('id', f"rq_{idx}"),
                                text=q.get('text', 'Unnamed research question'),
                                type=q.get('type', 'descriptive'),
                                linked_concept_ids=q.get('linked_concept_ids', []) or q.get('linked_concepts', []),
                                priority=q.get('priority', 'must_have'),
                                methodological_lens=q.get('methodological_lens')
                            )
                        )
                    else:
                        reconstructed.append(q)
                rqs.questions = reconstructed

            from .prompts import PROMPT_STAGE3_SEARCH_EXPANSION, format_concepts_for_prompt
            concept_str = format_concepts_for_prompt(concepts.concepts)
            rq_str = "\n".join([f"- {q.text}" for q in rqs.questions[:5]])

            prompt = PROMPT_STAGE3_SEARCH_EXPANSION.format(
                concepts=concept_str,
                research_questions=rq_str
            )
            logger.debug("Stage3 search expansion prompt:\n%s", prompt)

            raw = self.provider.generate(SYSTEM_PROMPT_LIBRARIAN, prompt)
            logger.debug("Stage3 raw LLM response: %s", raw)

            data = self.provider.clean_json_response(raw)

            blocks_data = data.get("blocks", [])
            blocks_list: List[SearchConceptBlock] = []

            for b in blocks_data:
                if not isinstance(b, dict):
                    continue
                block = SearchConceptBlock(
                    id=str(uuid.uuid4()),
                    label=b.get("label", "Unnamed Block"),
                    description=b.get("description"),
                    terms_included=b.get("terms_included", []),
                    terms_excluded=b.get("terms_excluded", [])
                )
                blocks_list.append(block)

            if not blocks_list:
                raise ValueError("LLM returned no blocks or malformed JSON")

            search_blocks = SearchConceptBlocks(
                project_id=concepts.project_id,
                blocks=blocks_list
            )

            meta = ModelMetadata(
                model_name=str(self.config.llm.provider.value),
                mode="generation",
                prompt_version="3.0",
                notes="Generated search concept blocks via LLM"
            )
            search_blocks.model_metadata = meta
            return search_blocks, meta

        except Exception as e:
            logger.error(f"LLM search expansion failed: {e}")
            logger.debug("Stage3 fallback triggered. Concepts=%d RQs=%d", len(concepts.concepts), len(rqs.questions))
            # Fallback: simple expansion
            from ..models import SearchConceptBlock
            import uuid

            blocks_list = []
            for concept in concepts.concepts[:6]:
                label = concept.label
                terms = [label, label.lower()]
                if not label.endswith('s'):
                    terms.append(label + 's')
                if ' ' in label:
                    terms.append(label.replace(' ', '-'))

                block = SearchConceptBlock(
                    id=str(uuid.uuid4()),
                    label=label,
                    description=concept.description,
                    terms_included=sorted(set(terms)),
                    terms_excluded=[]
                )
                blocks_list.append(block)

            search_blocks = SearchConceptBlocks(
                project_id=concepts.project_id,
                blocks=blocks_list
            )

            meta = ModelMetadata(
                model_name=str(self.config.llm.provider.value),
                mode="fallback-heuristic",
                prompt_version="fallback",
                notes=f"Heuristic fallback for search expansion (reason: {str(e)})"
            )
            search_blocks.model_metadata = meta
            return search_blocks, meta

    def build_database_queries(
        self, blocks: SearchConceptBlocks, db_names: List[str]
    ) -> Tuple[DatabaseQueryPlan, ModelMetadata]:
        """Stage 4: Generate database queries using LLM with Anti-Hallucination validation.

        Strategy:
        1. Try LLM generation (database-specific expertise)
        2. Validate using Anti-Hallucination syntax engine
        3. Fallback to syntax engine if LLM fails or produces invalid syntax
        """
        try:
            from .prompts import PROMPT_STAGE4_QUERY_GENERATION
            from ..models import DatabaseQuery, DatabaseQueryPlan
            import uuid

            # Format blocks for prompt
            blocks_str = self._format_blocks_for_query_gen(blocks.blocks)

            prompt = PROMPT_STAGE4_QUERY_GENERATION.format(
                blocks=blocks_str,
                databases=", ".join(db_names)
            )

            logger.debug("Stage4 query generation prompt:\n%s", prompt)

            raw = self.provider.generate(SYSTEM_PROMPT_LIBRARIAN, prompt)
            logger.debug("Stage4 raw LLM response: %s", raw[:500])

            data = self.provider.clean_json_response(raw)

            # Parse queries
            queries = []
            for q_data in data.get("queries", []):
                # Validate query syntax using Anti-Hallucination layer
                query_str = q_data.get("query", "")
                db_name = q_data.get("database", "").lower()

                # Check for hallucinated operators
                validation_errors = self._validate_query_syntax(query_str, db_name)

                if validation_errors:
                    logger.warning(f"LLM generated invalid syntax for {db_name}: {validation_errors}")
                    # Fallback to syntax engine for this database
                    query_str = self._generate_with_syntax_engine(blocks, db_name)
                    notes = f"LLM syntax invalid, used engine. Original errors: {', '.join(validation_errors)}"
                else:
                    notes = q_data.get("notes", "Generated by LLM")

                queries.append(DatabaseQuery(
                    id=f"query_{db_name}_{uuid.uuid4().hex[:6]}",
                    database_name=db_name,
                    query_blocks=q_data.get("blocks_used", [b.id for b in blocks.blocks]),
                    boolean_query_string=query_str,
                    notes=notes
                ))

            if not queries:
                raise ValueError("LLM returned no queries")

            plan = DatabaseQueryPlan(project_id=blocks.project_id, queries=queries)
            meta = ModelMetadata(
                model_name=str(self.config.llm.provider.value),
                mode="generation-with-validation",
                prompt_version="4.0",
                notes="LLM generation with Anti-Hallucination validation"
            )
            plan.model_metadata = meta
            return plan, meta

        except Exception as e:
            logger.error(f"LLM query generation failed: {e}")
            logger.warning("Falling back to Anti-Hallucination syntax engine")
            return self._fallback_query_generation(blocks, db_names)

    def _format_blocks_for_query_gen(self, blocks: List) -> str:
        """Format SearchConceptBlocks for LLM prompt."""
        lines = []
        for i, block in enumerate(blocks, 1):
            label = getattr(block, 'label', f'Block {i}')

            # Get terms (handle both dict and object)
            if hasattr(block, 'terms_included'):
                included = block.terms_included
            elif isinstance(block, dict):
                included = block.get('terms_included', [])
            else:
                included = []

            if hasattr(block, 'terms_excluded'):
                excluded = block.terms_excluded
            elif isinstance(block, dict):
                excluded = block.get('terms_excluded', [])
            else:
                excluded = []

            terms_str = ', '.join(included[:8])  # Limit to 8 terms for readability
            if len(included) > 8:
                terms_str += f", ... ({len(included)} total)"

            lines.append(f"- Block {i}: {label}")
            lines.append(f"  Included: {terms_str}")

            if excluded:
                excl_str = ', '.join(excluded[:5])
                lines.append(f"  Excluded: {excl_str}")

        return "\n".join(lines)

    def _validate_query_syntax(self, query: str, database: str) -> List[str]:
        """Validate query doesn't contain hallucinated operators.

        Returns list of validation errors (empty if valid).
        """
        errors = []

        # Check for hallucinated operators that ChatGPT often generates
        hallucinated_operators = ["NEAR", "ADJ", "PROX", "W/", "WITHIN"]
        for op in hallucinated_operators:
            if op in query.upper():
                errors.append(f"Invalid operator '{op}' (not supported in {database})")

        # Database-specific validation
        if database == "pubmed":
            # Check for common PubMed mistakes
            if "[mesh]" in query.lower() and not ("[mesh terms]" in query.lower() or "[mesh]" in query):
                errors.append("PubMed MeSH tag should be [MeSH Terms] not [mesh]")

        elif database == "scopus":
            # Scopus should use TITLE-ABS-KEY wrapper
            if "TITLE-ABS-KEY" not in query:
                errors.append("Scopus queries should use TITLE-ABS-KEY() wrapper")

        return errors

    def _generate_with_syntax_engine(self, blocks: SearchConceptBlocks, db_name: str) -> str:
        """Generate query using Anti-Hallucination syntax engine."""
        from ..search.models import QueryPlan as SyntaxQueryPlan, ConceptBlock as SyntaxConceptBlock, FieldTag
        from ..search.builder import get_builder

        syntax_plan = SyntaxQueryPlan()
        for block in blocks.blocks:
            syntax_block = SyntaxConceptBlock(label=block.label)
            for term in block.terms_included:
                syntax_block.add_term(term, FieldTag.KEYWORD)
            for ex_term in block.terms_excluded:
                syntax_block.add_excluded_term(ex_term, FieldTag.KEYWORD)
            syntax_plan.blocks.append(syntax_block)

        builder = get_builder(db_name)
        return builder.build(syntax_plan)

    def _fallback_query_generation(
        self, blocks: SearchConceptBlocks, db_names: List[str]
    ) -> Tuple[DatabaseQueryPlan, ModelMetadata]:
        """Fallback using Anti-Hallucination syntax engine."""
        from ..models import DatabaseQuery, DatabaseQueryPlan
        from ..search.models import QueryPlan as SyntaxQueryPlan, ConceptBlock as SyntaxConceptBlock, FieldTag
        from ..search.builder import get_builder
        import uuid

        queries = []

        # Convert to syntax engine format
        syntax_plan = SyntaxQueryPlan()
        for block in blocks.blocks:
            syntax_block = SyntaxConceptBlock(label=block.label)
            for term in block.terms_included:
                syntax_block.add_term(term, FieldTag.KEYWORD)
            for ex_term in block.terms_excluded:
                syntax_block.add_excluded_term(ex_term, FieldTag.KEYWORD)
            syntax_plan.blocks.append(syntax_block)

        # Generate for each database
        for db_name in db_names:
            try:
                builder = get_builder(db_name.lower())
                query_string = builder.build(syntax_plan)

                queries.append(DatabaseQuery(
                    id=f"query_{db_name}_{uuid.uuid4().hex[:6]}",
                    database_name=db_name.lower(),
                    query_blocks=[b.id for b in blocks.blocks],
                    boolean_query_string=query_string,
                    notes="Generated by Anti-Hallucination syntax engine (fallback)"
                ))
            except ValueError:
                # Database not supported
                queries.append(DatabaseQuery(
                    id=f"query_{db_name}_{uuid.uuid4().hex[:6]}",
                    database_name=db_name.lower(),
                    query_blocks=[b.id for b in blocks.blocks],
                    boolean_query_string=f"# Unsupported database: {db_name}",
                    notes=f"Database {db_name} not supported by syntax engine"
                ))

        plan = DatabaseQueryPlan(project_id=blocks.project_id, queries=queries)
        meta = ModelMetadata(
            model_name=str(self.config.llm.provider.value),
            mode="fallback-syntax-engine",
            prompt_version="fallback",
            notes="Anti-Hallucination syntax engine (LLM unavailable)"
        )
        plan.model_metadata = meta
        return plan, meta

    def draft_screening_criteria(
        self, rqs: ResearchQuestionSet, blocks: SearchConceptBlocks
    ) -> Tuple[ScreeningCriteria, ScreeningChecklist, ModelMetadata]:
        raise NotImplementedError("Stage 5 not yet implemented")

    def summarize_strategy(
        self, pkg: StrategyPackage
    ) -> Tuple[str, ModelMetadata]:
        raise NotImplementedError("Stage 6 not yet implemented")
