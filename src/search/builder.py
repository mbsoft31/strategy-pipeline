"""Query builder that orchestrates dialect-specific syntax generation."""

from typing import Type

from .models import QueryPlan
from .dialects import (
    DatabaseDialect, PubMedDialect, ScopusDialect,
    ArxivDialect, OpenAlexDialect, SemanticScholarDialect, CrossRefDialect
)


class SyntaxBuilder:
    """Builds database-specific query strings from a QueryPlan.

    Example:
        >>> plan = QueryPlan()
        >>> block = ConceptBlock("Disease")
        >>> block.add_term("diabetes")
        >>> plan.blocks.append(block)
        >>>
        >>> builder = SyntaxBuilder(PubMedDialect)
        >>> query = builder.build(plan)
        >>> print(query)
        diabetes[Title/Abstract]
    """

    def __init__(self, dialect: Type[DatabaseDialect]):
        """Initialize with a dialect class.

        Args:
            dialect: DatabaseDialect subclass (not instance)
        """
        self.dialect = dialect()

    def build(self, plan: QueryPlan) -> str:
        """Build query string from plan.

        Args:
            plan: QueryPlan with concept blocks

        Returns:
            Database-specific query string
        """
        group_strings = []

        for block in plan.blocks:
            # Format each term in the block
            term_strings = []
            for term in block.terms:
                formatted = self.dialect.format_term(term)
                term_strings.append(formatted)

            if term_strings:
                # Join terms with OR
                group_str = self.dialect.join_or(term_strings)
                group_strings.append(group_str)

        # Join groups with AND
        return self.dialect.join_and(group_strings)


def get_builder(db_name: str) -> SyntaxBuilder:
    """Factory function to get builder for a database.

    Args:
        db_name: Database name ("pubmed", "scopus", "arxiv", "openalex", "semanticscholar", "crossref")

    Returns:
        SyntaxBuilder instance

    Raises:
        ValueError: If database name is unknown

    Example:
        >>> builder = get_builder("pubmed")
        >>> isinstance(builder.dialect, PubMedDialect)
        True
    """
    db_name_lower = db_name.lower()

    if db_name_lower == "pubmed":
        return SyntaxBuilder(PubMedDialect)
    elif db_name_lower == "scopus":
        return SyntaxBuilder(ScopusDialect)
    elif db_name_lower == "arxiv":
        return SyntaxBuilder(ArxivDialect)
    elif db_name_lower == "openalex":
        return SyntaxBuilder(OpenAlexDialect)
    elif db_name_lower == "semanticscholar":
        return SyntaxBuilder(SemanticScholarDialect)
    elif db_name_lower == "crossref":
        return SyntaxBuilder(CrossRefDialect)
    else:
        raise ValueError(
            f"Unknown database: {db_name}. "
            f"Supported: pubmed, scopus, arxiv, openalex, semanticscholar, crossref"
        )

