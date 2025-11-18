"""Model service abstraction for LLM and SLM capabilities.

This module defines the interface that pipeline stages use to interact with
language models, keeping the core logic decoupled from specific LLM/SLM providers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from ..models import (
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


class ModelService(ABC):
    """Abstract interface for LLM/SLM capabilities.

    Concrete implementations can use:
    - Online LLMs (OpenAI, Anthropic, etc.)
    - Local SLMs (LLaMA, Mistral, etc.)
    - Hybrid approaches (SLM for extraction, LLM for generation)
    - Simple heuristics (for testing without external dependencies)
    """

    @abstractmethod
    def suggest_project_context(self, raw_idea: str) -> Tuple[ProjectContext, ModelMetadata]:
        """Generate a draft ProjectContext from a raw idea description.

        Args:
            raw_idea: Free-text description of the research idea.

        Returns:
            Tuple of (draft ProjectContext, metadata about generation).
        """
        pass

    @abstractmethod
    def generate_problem_framing(
        self, context: ProjectContext
    ) -> Tuple[ProblemFraming, ConceptModel, ModelMetadata]:
        """Generate draft ProblemFraming and ConceptModel from project context.

        Args:
            context: The approved project context.

        Returns:
            Tuple of (draft ProblemFraming, draft ConceptModel, metadata).
        """
        pass

    @abstractmethod
    def generate_research_questions(
        self, framing: ProblemFraming, concepts: ConceptModel
    ) -> Tuple[ResearchQuestionSet, ModelMetadata]:
        """Generate draft research questions from problem framing and concepts.

        Args:
            framing: The approved problem framing.
            concepts: The approved concept model.

        Returns:
            Tuple of (draft ResearchQuestionSet, metadata).
        """
        pass

    @abstractmethod
    def expand_search_terms(
        self, concepts: ConceptModel, rqs: ResearchQuestionSet
    ) -> Tuple[SearchConceptBlocks, ModelMetadata]:
        """Generate draft search concept blocks (synonyms, terms) from concepts and RQs.

        Args:
            concepts: The approved concept model.
            rqs: The approved research questions.

        Returns:
            Tuple of (draft SearchConceptBlocks, metadata).
        """
        pass

    @abstractmethod
    def build_database_queries(
        self, blocks: SearchConceptBlocks, db_names: List[str]
    ) -> Tuple[DatabaseQueryPlan, ModelMetadata]:
        """Generate draft database-specific Boolean queries.

        Args:
            blocks: The approved search concept blocks.
            db_names: List of target databases (e.g., ["pubmed", "scopus"]).

        Returns:
            Tuple of (draft DatabaseQueryPlan, metadata).
        """
        pass

    @abstractmethod
    def draft_screening_criteria(
        self, rqs: ResearchQuestionSet, blocks: SearchConceptBlocks
    ) -> Tuple[ScreeningCriteria, Optional[ScreeningChecklist], ModelMetadata]:
        """Generate draft screening criteria and optional checklist.

        Args:
            rqs: The approved research questions.
            blocks: The approved search concept blocks.

        Returns:
            Tuple of (draft ScreeningCriteria, optional ScreeningChecklist, metadata).
        """
        pass

    @abstractmethod
    def summarize_strategy(self, pkg: StrategyPackage) -> Tuple[str, ModelMetadata]:
        """Generate a narrative Markdown summary of the complete strategy.

        Args:
            pkg: The complete strategy package.

        Returns:
            Tuple of (Markdown summary string, metadata).
        """
        pass

