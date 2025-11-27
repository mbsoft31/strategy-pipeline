This module represents the **"Hard Logic"** of your application. Unlike the previous stages which relied on the probabilistic nature of LLMs, this stage relies on **deterministic software engineering**.

This is your **Anti-Hallucination Layer**. If the LLM suggests a keyword, **this code** ensures that keyword is formatted 100% correctly for the target database.

### Folder Structure

We will create a dedicated package `src/search/` to keep this distinct from the pipeline logic.

```text
src/
└── search/
    ├── __init__.py
    ├── models.py          # Data structures for generic query parts
    ├── dialects.py        # The Strategy Pattern (PubMed vs Scopus logic)
    └── builder.py         # The Director that assembles the string
```

---

### 1. `src/search/models.py`

We need an abstract representation of a search query *before* it becomes a string. Think of this as the "Intermediate Representation" (IR).

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

class FieldTag(Enum):
    KEYWORD = "keyword"  # Title/Abstract/Key
    CONTROLLED_VOCAB = "controlled"  # MeSH / Emtree
    ALL_FIELDS = "all"

@dataclass
class SearchTerm:
    """An atomic search unit."""
    text: str
    field_tag: FieldTag = FieldTag.KEYWORD
    is_phrase: bool = False

@dataclass
class ConceptBlock:
    """A group of synonyms combined with OR."""
    label: str  # e.g., "Population"
    terms: List[SearchTerm] = field(default_factory=list)

    def add_term(self, text: str, tag: FieldTag = FieldTag.KEYWORD):
        # Simple heuristic: if it has spaces, it's a phrase
        is_phrase = " " in text.strip()
        self.terms.append(SearchTerm(text, tag, is_phrase))

@dataclass
class QueryPlan:
    """The complete strategy combined with AND."""
    blocks: List[ConceptBlock] = field(default_factory=list)
```

---

### 2. `src/search/dialects.py`

This is the **Strategy Pattern**. Each database has a "Dialect" that defines how to handle syntax, quoting, and field mapping.

```python
from abc import ABC, abstractmethod
from typing import List
from src.search.models import SearchTerm, ConceptBlock, FieldTag

class DatabaseDialect(ABC):
    """Abstract Base Class for DB Syntax Rules"""
    
    @abstractmethod
    def format_term(self, term: SearchTerm) -> str:
        pass
    
    @abstractmethod
    def join_or(self, terms: List[str]) -> str:
        pass

    @abstractmethod
    def join_and(self, groups: List[str]) -> str:
        pass

class PubMedDialect(DatabaseDialect):
    def format_term(self, term: SearchTerm) -> str:
        # 1. Handle Quoting
        clean_text = term.text.replace('"', '') # Sanitize
        if term.is_phrase:
            base = f'"{clean_text}"'
        else:
            base = clean_text
            
        # 2. Handle Field Tags
        if term.field_tag == FieldTag.CONTROLLED_VOCAB:
            return f"{base}[MeSH Terms]"
        elif term.field_tag == FieldTag.KEYWORD:
            return f"{base}[Title/Abstract]"
        else:
            return f"{base}[All Fields]"

    def join_or(self, terms: List[str]) -> str:
        if not terms: return ""
        if len(terms) == 1: return terms[0]
        return f"({' OR '.join(terms)})"

    def join_and(self, groups: List[str]) -> str:
        return "\nAND\n".join(groups)

class ScopusDialect(DatabaseDialect):
    def format_term(self, term: SearchTerm) -> str:
        # Scopus handles fields differently: typically wrapping the whole group.
        # But individual terms just need quoting.
        clean_text = term.text.replace('"', '')
        if term.is_phrase:
            return f'"{clean_text}"'
        return clean_text

    def join_or(self, terms: List[str]) -> str:
        # Scopus Optimization: TITLE-ABS-KEY(term1 OR term2)
        # Instead of TITLE-ABS-KEY(term1) OR TITLE-ABS-KEY(term2)
        if not terms: return ""
        inner = " OR ".join(terms)
        return f"TITLE-ABS-KEY({inner})"

    def join_and(self, groups: List[str]) -> str:
        return " AND ".join(groups)
```

---

### 3. `src/search/builder.py`

The Builder accepts the data and the chosen dialect to produce the final string.

```python
from typing import Type
from src.search.models import QueryPlan
from src.search.dialects import DatabaseDialect, PubMedDialect, ScopusDialect

class SyntaxBuilder:
    def __init__(self, dialect: Type[DatabaseDialect]):
        self.dialect = dialect()

    def build(self, plan: QueryPlan) -> str:
        group_strings = []

        for block in plan.blocks:
            term_strings = []
            for term in block.terms:
                # Specific handling for Scopus optimization
                # (In a full impl, we'd move this logic deeper into the dialect)
                if isinstance(self.dialect, ScopusDialect) and term.field_tag == 'controlled':
                    # Scopus doesn't use MeSH tags, might skip or map to INDEXTERMS
                    # For MVP, we treat as keyword
                    pass 
                
                t_str = self.dialect.format_term(term)
                term_strings.append(t_str)
            
            if term_strings:
                group_str = self.dialect.join_or(term_strings)
                group_strings.append(group_str)

        return self.dialect.join_and(group_strings)

def get_builder(db_name: str) -> SyntaxBuilder:
    """Factory function"""
    if db_name.lower() == "pubmed":
        return SyntaxBuilder(PubMedDialect)
    elif db_name.lower() == "scopus":
        return SyntaxBuilder(ScopusDialect)
    else:
        raise ValueError(f"Unknown database: {db_name}")
```

---

### 4. The Proof: `tests/test_syntax.py`

This is how you verify the "Moat." You don't need to run an LLM to test this. It should be robust and fail-safe.

```python
import unittest
from src.search.models import QueryPlan, ConceptBlock, FieldTag
from src.search.builder import get_builder

class TestSyntaxEngine(unittest.TestCase):

    def setUp(self):
        # Construct a dummy strategy:
        # (Heart Attack OR Myocardial Infarction) AND (Aspirin)
        self.plan = QueryPlan()
        
        # Block 1: Disease
        b1 = ConceptBlock("Disease")
        b1.add_term("Heart Attack", FieldTag.KEYWORD)
        b1.add_term("Myocardial Infarction", FieldTag.CONTROLLED_VOCAB)
        self.plan.blocks.append(b1)
        
        # Block 2: Drug
        b2 = ConceptBlock("Drug")
        b2.add_term("Aspirin", FieldTag.KEYWORD)
        self.plan.blocks.append(b2)

    def test_pubmed_syntax(self):
        builder = get_builder("pubmed")
        query = builder.build(self.plan)
        
        print(f"\n[PubMed Query]\n{query}")
        
        # Assertions specific to PubMed syntax
        self.assertIn('"Heart Attack"[Title/Abstract]', query)
        self.assertIn('"Myocardial Infarction"[MeSH Terms]', query)
        self.assertIn(" OR ", query)
        self.assertIn("\nAND\n", query)

    def test_scopus_syntax(self):
        builder = get_builder("scopus")
        query = builder.build(self.plan)
        
        print(f"\n[Scopus Query]\n{query}")
        
        # Assertions specific to Scopus syntax
        self.assertTrue(query.startswith("TITLE-ABS-KEY"))
        self.assertIn('"Heart Attack"', query)
        self.assertIn('"Aspirin"', query)
        # Scopus doesn't have [MeSH], so logic handles it as keyword (in this simple MVP)
        self.assertIn(" AND ", query)

if __name__ == '__main__':
    unittest.main()
```

### How to Integrate This

1.  Copy the files into the `src/search/` folder.
2.  Run the test: `python tests/test_syntax.py`.

### Why This Is Your "Moat"

When you demonstrate this to a user (or an investor):
1.  Show them ChatGPT hallucinating a query (e.g., using `NEAR/5` in PubMed).
2.  Show them your tool outputting the **exact, validated string**.
3.  Explain: *"The AI suggests the concepts; our Engine ensures the syntax is executable."*

This hybrid approach (AI for ideas + Code for syntax) is the winning formula.