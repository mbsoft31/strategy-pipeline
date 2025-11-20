# Day 2 Quick Start Guide

## ✅ Day 1 Recap

You completed:
- Configuration system (`src/config.py`)
- Exception hierarchy (`src/utils/exceptions.py`)
- Test infrastructure (19/19 tests passing)

## 🎯 Day 2 Objective

Build the **Syntax Engine** - the deterministic Boolean query generator that proves your technical "moat".

**Why This Matters**: ChatGPT hallucinates invalid syntax. Your engine guarantees correctness.

---

## What You'll Build Today

### 1. Query Data Models (`src/search/models.py`)
```python
- SearchTerm (atomic search unit)
- ConceptBlock (synonyms joined with OR)
- QueryPlan (complete strategy with AND)
- FieldTag enum (keyword, controlled_vocab, all_fields)
```

### 2. Database Dialects (`src/search/dialects.py`)
```python
- DatabaseDialect (abstract base)
- PubMedDialect (MeSH terms, [Title/Abstract] tags)
- ScopusDialect (TITLE-ABS-KEY wrapper)
```

### 3. Query Builder (`src/search/builder.py`)
```python
- SyntaxBuilder (orchestrates dialect)
- get_builder() factory function
```

### 4. Tests (`tests/test_syntax_engine.py`)
```python
- PubMed syntax correctness
- Scopus syntax correctness
- Edge cases (empty, single term, etc.)
- Comparison demo vs ChatGPT
```

### 5. Demo Script (`demo_syntax_engine.py`)
```python
- Realistic research query example
- Both PubMed and Scopus output
- Visual proof of correctness
```

---

## File Checklist

Create these files in order:

- [ ] `src/search/__init__.py`
- [ ] `src/search/models.py`
- [ ] `src/search/dialects.py`
- [ ] `src/search/builder.py`
- [ ] `tests/test_syntax_engine.py`
- [ ] `demo_syntax_engine.py`

All code is in `guide-phase1Foundation.prompt.md` - just copy and execute!

---

## Expected Output

After Day 2, you should be able to run:

```bash
python demo_syntax_engine.py
```

And see:
```
[PubMed/MEDLINE Query]
------------------------------------------------------------
("type 2 diabetes"[Title/Abstract] OR "diabetes mellitus type 2"[MeSH Terms] OR "T2DM"[Title/Abstract])
AND
("machine learning"[Title/Abstract] OR "deep learning"[Title/Abstract])
AND
("prediction"[Title/Abstract] OR "risk stratification"[Title/Abstract])

[Scopus Query]
------------------------------------------------------------
TITLE-ABS-KEY("type 2 diabetes" OR "diabetes mellitus type 2" OR "T2DM") 
AND 
TITLE-ABS-KEY("machine learning" OR "deep learning") 
AND 
TITLE-ABS-KEY("prediction" OR "risk stratification")

✅ Both queries are syntactically VALID
✅ Ready to paste directly into databases
✅ ChatGPT cannot guarantee this!
```

---

## Success Criteria

Day 2 is complete when:
- ✅ All syntax engine tests pass
- ✅ Demo script runs successfully
- ✅ Can generate valid PubMed queries
- ✅ Can generate valid Scopus queries
- ✅ No hallucinated operators (like `NEAR/5` in PubMed)

---

## Time Estimate

**4 hours total**:
- 1 hour: Models + Dialects
- 1 hour: Builder + Factory
- 1 hour: Tests
- 1 hour: Demo + Documentation

---

## Quick Commands

```bash
# Run all tests
pytest tests/ -v

# Run only syntax tests
pytest tests/test_syntax_engine.py -v

# Run demo
python demo_syntax_engine.py

# Check for errors
pytest tests/ -q
```

---

## Tips

1. **Copy from Guide**: All code is ready in `guide-phase1Foundation.prompt.md`
2. **Test as You Go**: Run tests after each file
3. **Use the Demo**: The demo script is your validation
4. **No Dependencies**: Pure Python string manipulation

---

## What Comes After Day 2?

**Day 3**: Tests + Demo + Documentation
- Comprehensive test suite
- Comparison with ChatGPT failures
- README updates
- Sprint 1 complete!

**Sprint 2** (Days 4-6): LLM Integration
- Rate limiting (needed for APIs)
- LLM provider layer
- Critique loop

---

## Ready?

Open `guide-phase1Foundation.prompt.md` and start with Section 3.1 (Day 2: The Syntax Engine).

**Let's build the moat! 🚀**

