"""Database-specific syntax dialects using Strategy Pattern.

Each dialect knows how to format terms, join with operators,
and apply database-specific quirks.
"""

from abc import ABC, abstractmethod
from typing import List

from .models import SearchTerm, FieldTag


class DatabaseDialect(ABC):
    """Abstract base class for database syntax rules."""

    @abstractmethod
    def format_term(self, term: SearchTerm) -> str:
        """Format a single search term with field tags."""
        pass

    @abstractmethod
    def join_or(self, terms: List[str]) -> str:
        """Join terms with OR operator."""
        pass

    @abstractmethod
    def join_and(self, groups: List[str]) -> str:
        """Join groups with AND operator."""
        pass

    def format_not(self, terms: List[str]) -> str:
        """Format NOT clause for excluded terms.

        Default implementation: NOT (term1 OR term2)
        Dialects can override for database-specific syntax.
        """
        if not terms:
            return ""
        or_group = self.join_or(terms)
        return f"NOT {or_group}" if or_group else ""


class PubMedDialect(DatabaseDialect):
    """PubMed/MEDLINE syntax.

    Rules:
    - Phrases use double quotes: "machine learning"
    - Field tags use square brackets: [Title/Abstract]
    - OR groups use parentheses: (term1 OR term2)
    - AND joins concept blocks

    Example:
        "deep learning"[Title/Abstract] AND (diabetes[MeSH Terms] OR "type 2 diabetes"[Title/Abstract])
    """

    def format_term(self, term: SearchTerm) -> str:
        """Format term with PubMed field tags.

        Args:
            term: Search term to format

        Returns:
            Formatted string
        """
        # Sanitize and quote if needed
        clean_text = term.text.replace('"', '').strip()

        if term.is_phrase:
            base = f'"{clean_text}"'
        else:
            base = clean_text

        # Apply field tags
        if term.field_tag == FieldTag.CONTROLLED_VOCAB:
            return f"{base}[MeSH Terms]"
        elif term.field_tag == FieldTag.KEYWORD:
            return f"{base}[Title/Abstract]"
        else:
            return f"{base}[All Fields]"

    def join_or(self, terms: List[str]) -> str:
        """Join terms with OR, wrapped in parentheses.

        Args:
            terms: List of formatted terms

        Returns:
            OR-joined string
        """
        if not terms:
            return ""
        if len(terms) == 1:
            return terms[0]
        return f"({' OR '.join(terms)})"

    def join_and(self, groups: List[str]) -> str:
        """Join groups with AND.

        Args:
            groups: List of OR-joined groups

        Returns:
            AND-joined string
        """
        return "\nAND\n".join(groups)


class ScopusDialect(DatabaseDialect):
    """Scopus syntax.

    Rules:
    - Phrases use double quotes: "machine learning"
    - Uses TITLE-ABS-KEY() wrapper for keyword search
    - Can optimize: TITLE-ABS-KEY(term1 OR term2) instead of multiple wrappers
    - AND joins concept blocks

    Example:
        TITLE-ABS-KEY("deep learning" OR "neural networks") AND TITLE-ABS-KEY(diabetes OR "type 2 diabetes")
    """

    def format_term(self, term: SearchTerm) -> str:
        """Format term for Scopus.

        Args:
            term: Search term to format

        Returns:
            Formatted string (without wrapper, added by join_or)
        """
        clean_text = term.text.replace('"', '').strip()

        if term.is_phrase:
            return f'"{clean_text}"'
        return clean_text

    def join_or(self, terms: List[str]) -> str:
        """Join terms with OR inside TITLE-ABS-KEY wrapper.

        This is more efficient than wrapping each term individually.

        Args:
            terms: List of formatted terms

        Returns:
            OR-joined string with wrapper
        """
        if not terms:
            return ""

        inner = " OR ".join(terms)
        return f"TITLE-ABS-KEY({inner})"

    def join_and(self, groups: List[str]) -> str:
        """Join groups with AND.

        Args:
            groups: List of wrapped groups

        Returns:
            AND-joined string
        """
        return " AND ".join(groups)

    def format_not(self, terms: List[str]) -> str:
        """Format NOT clause for Scopus using AND NOT syntax.

        Scopus prefers: AND NOT TITLE-ABS-KEY(excluded terms)
        """
        if not terms:
            return ""
        inner = " OR ".join(terms)
        return f"AND NOT TITLE-ABS-KEY({inner})"


class ArxivDialect(DatabaseDialect):
    """arXiv API syntax.

    Rules:
    - Field tags: ti: (Title), abs: (Abstract), all: (All fields)
    - Boolean: AND, OR, ANDNOT
    - Grouping: parentheses
    """
    def format_term(self, term: SearchTerm) -> str:
        clean_text = term.text.replace('"', '').strip()
        if term.is_phrase:
            base = f'"{clean_text}"'
        else:
            base = clean_text

        # arXiv doesn't have MeSH, so we treat controlled vocab as Title/Abstract
        if term.field_tag == FieldTag.KEYWORD:
            # arXiv often requires searching title OR abstract explicitly if not using 'all'
            # But for simplicity in string gen, 'all' is safest, or explicit ti/abs
            return f'all:{base}'
        elif term.field_tag == FieldTag.CONTROLLED_VOCAB:
             return f'all:{base}'
        else:
            return f'all:{base}'

    def join_or(self, terms: List[str]) -> str:
        if not terms: return ""
        if len(terms) == 1: return terms[0]
        # arXiv likes clear grouping
        return f"({' OR '.join(terms)})"

    def join_and(self, groups: List[str]) -> str:
        return " AND ".join(groups)


class OpenAlexDialect(DatabaseDialect):
    """OpenAlex Search API syntax.

    Rules:
    - Supports standard Boolean (AND, OR, NOT) in the 'search' parameter
    - Phrases in quotes
    - Field specific searches usually handled via API filters (e.g. title.search),
      but for the general search string, we use standard boolean.
    """
    def format_term(self, term: SearchTerm) -> str:
        clean_text = term.text.replace('"', '').strip()
        if term.is_phrase:
            return f'"{clean_text}"'
        return clean_text

    def join_or(self, terms: List[str]) -> str:
        if not terms: return ""
        if len(terms) == 1: return terms[0]
        return f"({' OR '.join(terms)})"

    def join_and(self, groups: List[str]) -> str:
        return " AND ".join(groups)


class SemanticScholarDialect(DatabaseDialect):
    """Semantic Scholar Graph API syntax.

    Rules:
    - Standard Boolean: + (AND), | (OR), - (NOT), "phrase"
    - However, the UI and newer APIs accept standard AND/OR text.
    - We will output the standard text format used in their keyword search.
    """
    def format_term(self, term: SearchTerm) -> str:
        clean_text = term.text.replace('"', '').strip()
        if term.is_phrase:
            return f'"{clean_text}"'
        return clean_text

    def join_or(self, terms: List[str]) -> str:
        if not terms: return ""
        if len(terms) == 1: return terms[0]
        return f"({' OR '.join(terms)})"

    def join_and(self, groups: List[str]) -> str:
        return " AND ".join(groups)


class CrossRefDialect(DatabaseDialect):
    """CrossRef Query syntax.

    Rules:
    - CrossRef is 'fuzzy' boolean. It prefers standard Google-like syntax.
    - + for required, - for exclusion.
    - We will generate a standard logical string which their engine interprets best.
    """
    def format_term(self, term: SearchTerm) -> str:
        clean_text = term.text.replace('"', '').strip()
        if term.is_phrase:
            return f'"{clean_text}"'
        return clean_text

    def join_or(self, terms: List[str]) -> str:
        if not terms: return ""
        # CrossRef isn't strict on OR, but grouping helps context
        return f"({' OR '.join(terms)})"

    def join_and(self, groups: List[str]) -> str:
        # CrossRef implies AND by default space, but explicit AND is clearer
        return " AND ".join(groups)


