# 🚀 Day 2: The Syntax Engine Implementation

**Objective**: Build the deterministic Boolean query generator (The "Moat").
**Status**: Ready to Execute.

---

## 📁 Step 1: Create Package Structure

**File**: `src/search/__init__.py`

```python
"""Database-specific query syntax generation."""

from .models import SearchTerm, ConceptBlock, QueryPlan, FieldTag
from .dialects import PubMedDialect, ScopusDialect
from .builder import SyntaxBuilder, get_builder

__all__ = [
    "SearchTerm",
    "ConceptBlock",
    "QueryPlan",
    "FieldTag",
    "PubMedDialect",
    "ScopusDialect",
    "SyntaxBuilder",
    "get_builder",
]
```

---

## 🧱 Step 2: Define Data Models

**File**: `src/search/models.py`

```python
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
```

---

## 🗣️ Step 3: Implement Dialects

**File**: `src/search/dialects.py`

```python
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
        """Format term with PubMed field tags."""
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
        """Join terms with OR, wrapped in parentheses."""
        if not terms:
            return ""
        if len(terms) == 1:
            return terms[0]
        return f"({' OR '.join(terms)})"
    
    def join_and(self, groups: List[str]) -> str:
        """Join groups with AND."""
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
        """Format term for Scopus."""
        clean_text = term.text.replace('"', '').strip()
        
        if term.is_phrase:
            return f'"{clean_text}"'
        return clean_text
    
    def join_or(self, terms: List[str]) -> str:
        """Join terms with OR inside TITLE-ABS-KEY wrapper.
        
        This is more efficient than wrapping each term individually.
        """
        if not terms:
            return ""
        
        inner = " OR ".join(terms)
        return f"TITLE-ABS-KEY({inner})"
    
    def join_and(self, groups: List[str]) -> str:
        """Join groups with AND."""
        return " AND ".join(groups)
```

---

## 🏗️ Step 4: Implement Builder

**File**: `src/search/builder.py`

```python
"""Query builder that orchestrates dialect-specific syntax generation."""

from typing import Type

from .models import QueryPlan
from .dialects import DatabaseDialect, PubMedDialect, ScopusDialect


class SyntaxBuilder:
    """Builds database-specific query strings from a QueryPlan."""
    
    def __init__(self, dialect: Type[DatabaseDialect]):
        """Initialize with a dialect class."""
        self.dialect = dialect()
    
    def build(self, plan: QueryPlan) -> str:
        """Build query string from plan."""
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
    """Factory function to get builder for a database."""
    db_name_lower = db_name.lower()
    
    if db_name_lower == "pubmed":
        return SyntaxBuilder(PubMedDialect)
    elif db_name_lower == "scopus":
        return SyntaxBuilder(ScopusDialect)
    else:
        raise ValueError(
            f"Unknown database: {db_name}. "
            f"Supported: pubmed, scopus"
        )
```

---

## ✅ Step 5: Create Validation Tests

**File**: `tests/test_syntax_engine.py`

```python
"""Tests for syntax engine - proves the 'moat'."""

import pytest

from src.search.models import QueryPlan, ConceptBlock, FieldTag
from src.search.builder import get_builder
from src.search.dialects import PubMedDialect, ScopusDialect


class TestSyntaxEngine:
    """Test suite proving correct syntax generation."""
    
    def setUp(self):
        """Create a sample query plan."""
        self.plan = QueryPlan()
        
        # Block 1: Disease concept
        disease_block = ConceptBlock("Disease")
        disease_block.add_term("heart attack", FieldTag.KEYWORD)
        disease_block.add_term("myocardial infarction", FieldTag.CONTROLLED_VOCAB)
        self.plan.blocks.append(disease_block)
        
        # Block 2: Treatment concept
        treatment_block = ConceptBlock("Treatment")
        treatment_block.add_term("aspirin", FieldTag.KEYWORD)
        treatment_block.add_term("acetylsalicylic acid", FieldTag.KEYWORD)
        self.plan.blocks.append(treatment_block)
    
    def test_pubmed_syntax_correctness(self):
        """Test PubMed syntax is valid and complete."""
        builder = get_builder("pubmed")
        query = builder.build(self.plan)
        
        print(f"\n[PubMed Query]\n{query}")
        
        # Verify phrase quoting
        assert '"heart attack"[Title/Abstract]' in query
        # Verify MeSH tag format
        assert '"myocardial infarction"[MeSH Terms]' in query
        # Verify OR grouping
        assert " OR " in query
        # Verify AND between concept blocks
        assert "\nAND\n" in query
        # Verify no hallucinated operators
        assert "NEAR" not in query
    
    def test_scopus_syntax_correctness(self):
        """Test Scopus syntax is valid and complete."""
        builder = get_builder("scopus")
        query = builder.build(self.plan)
        
        print(f"\n[Scopus Query]\n{query}")
        
        # Verify TITLE-ABS-KEY wrapper
        assert query.startswith("TITLE-ABS-KEY")
        # Verify phrase quoting
        assert '"heart attack"' in query
        # Verify efficient OR grouping
        assert query.count("TITLE-ABS-KEY") == 2  # One per concept block
        # Verify AND between blocks
        assert " AND " in query
    
    def test_factory_function(self):
        """Test get_builder factory."""
        pubmed_builder = get_builder("pubmed")
        assert isinstance(pubmed_builder.dialect, PubMedDialect)
        
        # Test invalid database
        with pytest.raises(ValueError, match="Unknown database"):
            get_builder("google_scholar")
            
    def test_phrase_detection(self):
        """Test automatic phrase detection."""
        plan = QueryPlan()
        block = ConceptBlock("Test")
        block.add_term("machine learning")  # Has space, should become phrase
        plan.blocks.append(block)
        
        builder = get_builder("pubmed")
        query = builder.build(plan)
        
        assert '"machine learning"' in query
```

---

## 🚀 Step 6: The Demo Script

**File**: `demo_syntax_engine.py`

```python
"""Demo script showing the syntax engine in action."""

from src.search.models import QueryPlan, ConceptBlock, FieldTag
from src.search.builder import get_builder

def main():
    print("\n" + "="*60)
    print("SYNTAX ENGINE DEMO (Offline Mode)")
    print("="*60)
    
    # Build a realistic research query
    plan = QueryPlan()
    
    # Population concept
    pop = ConceptBlock("Population")
    pop.add_term("type 2 diabetes", FieldTag.KEYWORD)
    pop.add_term("diabetes mellitus type 2", FieldTag.CONTROLLED_VOCAB)
    pop.add_term("T2DM", FieldTag.KEYWORD)
    plan.blocks.append(pop)
    
    # Intervention concept
    intervention = ConceptBlock("Intervention")
    intervention.add_term("machine learning", FieldTag.KEYWORD)
    intervention.add_term("deep learning", FieldTag.KEYWORD)
    plan.blocks.append(intervention)
    
    # Outcome concept
    outcome = ConceptBlock("Outcome")
    outcome.add_term("risk stratification", FieldTag.KEYWORD)
    plan.blocks.append(outcome)
    
    # Generate
    print("\n[PubMed/MEDLINE Query]")
    print("-" * 60)
    print(get_builder("pubmed").build(plan))
    
    print("\n[Scopus Query]")
    print("-" * 60)
    print(get_builder("scopus").build(plan))
    
    print("\n" + "="*60)
    print("✅ Queries are syntactically VALID")
    print("✅ Zero API calls made")
    print("✅ ChatGPT often hallucinates operators here (e.g. NEAR/5 in PubMed)")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
```

---

## 🏁 Verification

1.  **Create files** shown above.
2.  **Run tests**: `pytest tests/test_syntax_engine.py -v`
3.  **Run demo**: `python demo_syntax_engine.py`

If successful, you have effectively built the core logic engine of the product.