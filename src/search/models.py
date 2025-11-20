"""Data models for search query construction.

These are intermediate representations of queries before they are
translated into database-specific syntax.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class FieldTag(str, Enum):
    """Search field types."""
    KEYWORD = "keyword"  # Title/Abstract/Keywords
    CONTROLLED_VOCAB = "controlled"  # MeSH / Emtree
    ALL_FIELDS = "all"


@dataclass
class SearchTerm:
    """An atomic search unit.

    Attributes:
        text: The search term (e.g., "machine learning")
        field_tag: Which field to search
        is_phrase: Whether to treat as exact phrase
    """
    text: str
    field_tag: FieldTag = FieldTag.KEYWORD
    is_phrase: bool = False

    def __post_init__(self):
        """Auto-detect phrases (terms with spaces)."""
        if not self.is_phrase and " " in self.text.strip():
            self.is_phrase = True


@dataclass
class ConceptBlock:
    """A group of synonyms combined with OR.

    Example:
        label = "Population"
        terms = ["elderly", "older adults", "seniors"]

    Becomes: (elderly OR "older adults" OR seniors)
    """
    label: str
    terms: List[SearchTerm] = field(default_factory=list)

    def add_term(self, text: str, tag: FieldTag = FieldTag.KEYWORD):
        """Add a term to this concept block.

        Args:
            text: Search term text
            tag: Field tag for this term
        """
        self.terms.append(SearchTerm(text, tag))


@dataclass
class QueryPlan:
    """Complete search strategy (blocks combined with AND).

    Example:
        Block 1: (elderly OR "older adults")
        Block 2: (diabetes OR "type 2 diabetes")

    Becomes: (elderly OR "older adults") AND (diabetes OR "type 2 diabetes")
    """
    blocks: List[ConceptBlock] = field(default_factory=list)

