"""Database-specific query syntax generation."""

from .models import SearchTerm, ConceptBlock, QueryPlan, FieldTag
from .dialects import (
    PubMedDialect, ScopusDialect, ArxivDialect,
    OpenAlexDialect, SemanticScholarDialect, CrossRefDialect
)
from .builder import SyntaxBuilder, get_builder

__all__ = [
    "SearchTerm",
    "ConceptBlock",
    "QueryPlan",
    "FieldTag",
    "PubMedDialect",
    "ScopusDialect",
    "ArxivDialect",
    "OpenAlexDialect",
    "SemanticScholarDialect",
    "CrossRefDialect",
    "SyntaxBuilder",
    "get_builder",
]

