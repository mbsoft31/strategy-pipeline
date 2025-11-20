"""
DEMONSTRATION OF NEW DATABASE DIALECTS
=======================================

This file shows example output from all 6 supported database dialects.

Research Question:
"What is known about hallucination and factuality in large language models?"

Query Structure:
- Concept 1 (Population): "large language models" OR "LLM"
- Concept 2 (Outcome): "hallucination" OR "factuality"

---

PUBMED QUERY:
("large language models"[Title/Abstract] OR LLM[Title/Abstract])
AND
("hallucination"[Title/Abstract] OR factuality[Title/Abstract])

---

SCOPUS QUERY:
TITLE-ABS-KEY("large language models" OR LLM) AND TITLE-ABS-KEY("hallucination" OR factuality)

---

ARXIV QUERY:
(all:"large language models" OR all:LLM) AND (all:"hallucination" OR all:factuality)

---

OPENALEX QUERY:
("large language models" OR LLM) AND ("hallucination" OR factuality)

---

SEMANTICSCHOLAR QUERY:
("large language models" OR LLM) AND ("hallucination" OR factuality)

---

CROSSREF QUERY:
("large language models" OR LLM) AND ("hallucination" OR factuality)

---

KEY OBSERVATIONS:

1. **PubMed** uses [Title/Abstract] field tags and newline-separated AND
2. **Scopus** wraps everything in TITLE-ABS-KEY() for efficiency  
3. **arXiv** uses the all: prefix for field specification
4. **OpenAlex, Semantic Scholar, CrossRef** use standard Boolean syntax

The SAME internal QueryPlan generates ALL of these!

This is the power of the Strategy Pattern:
- One conceptual model (QueryPlan)
- Multiple execution strategies (DatabaseDialects)
- Zero hallucination risk
- Perfect syntax for each database

---

HOW TO USE:

```python
from src.search.models import QueryPlan, ConceptBlock, FieldTag
from src.search.builder import get_builder

# Define your research query once
plan = QueryPlan()

pop = ConceptBlock("Population")
pop.add_term("large language models", FieldTag.KEYWORD)
pop.add_term("LLM", FieldTag.KEYWORD)
plan.blocks.append(pop)

outcome = ConceptBlock("Outcome")
outcome.add_term("hallucination", FieldTag.KEYWORD)
outcome.add_term("factuality", FieldTag.KEYWORD)
plan.blocks.append(outcome)

# Generate syntax for any database
pubmed_query = get_builder("pubmed").build(plan)
scopus_query = get_builder("scopus").build(plan)
arxiv_query = get_builder("arxiv").build(plan)
openalex_query = get_builder("openalex").build(plan)
semanticscholar_query = get_builder("semanticscholar").build(plan)
crossref_query = get_builder("crossref").build(plan)
```

---

ADDING NEW DATABASES:

To add support for a new database (e.g., Google Scholar):

1. Create a new dialect class in `src/search/dialects.py`:
   ```python
   class GoogleScholarDialect(DatabaseDialect):
       def format_term(self, term: SearchTerm) -> str:
           # Implement Google Scholar syntax rules
           ...
       
       def join_or(self, terms: List[str]) -> str:
           ...
       
       def join_and(self, groups: List[str]) -> str:
           ...
   ```

2. Register it in `src/search/builder.py`:
   ```python
   elif db_name_lower == "googlescholar":
       return SyntaxBuilder(GoogleScholarDialect)
   ```

3. Export it in `src/search/__init__.py`

That's it! The entire pipeline now supports the new database.

---

WHY THIS MATTERS:

Traditional Approach (ChatGPT):
❌ Hallucination risk in syntax
❌ Inconsistent across databases
❌ No guarantees of correctness
❌ Manual copy-paste errors
❌ Hard to maintain

Strategy Pattern Approach (This Tool):
✅ Mathematically correct syntax
✅ Consistent transformation logic
✅ Tested and validated
✅ Easy to extend
✅ Maintainable codebase

This is your competitive moat.
"""
