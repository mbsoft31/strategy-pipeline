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
    PROMPT_STAGE1_REFINE,
)
from ..models import (
    ProjectContext,
    ProblemFraming,
    ConceptModel,
    Concept,
    ModelMetadata,
    ResearchQuestionSet,
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
        raise NotImplementedError("Stage 2 not yet implemented")

    def expand_search_terms(
        self, concepts: ConceptModel, rqs: ResearchQuestionSet
    ) -> Tuple[SearchConceptBlocks, ModelMetadata]:
        raise NotImplementedError("Stage 3 not yet implemented")

    def build_database_queries(
        self, blocks: SearchConceptBlocks, db_names: List[str]
    ) -> Tuple[DatabaseQueryPlan, ModelMetadata]:
        raise NotImplementedError("Stage 4 not yet implemented")

    def draft_screening_criteria(
        self, rqs: ResearchQuestionSet, blocks: SearchConceptBlocks
    ) -> Tuple[ScreeningCriteria, ScreeningChecklist, ModelMetadata]:
        raise NotImplementedError("Stage 5 not yet implemented")

    def summarize_strategy(
        self, pkg: StrategyPackage
    ) -> Tuple[str, ModelMetadata]:
        raise NotImplementedError("Stage 6 not yet implemented")

