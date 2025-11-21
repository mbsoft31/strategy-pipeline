# Utility Scripts

This folder contains utility and verification scripts for development, testing, and maintenance.

## 📁 Contents

### Verification Scripts

**verify_implementation.py**
- Verifies core implementation is working
- Checks all stages are registered
- Validates configuration
- **Usage:** `python scripts/utilities/verify_implementation.py`

**verify_sprint2.py**
- Sprint 2 verification script
- Tests problem framing and research questions
- **Usage:** `python scripts/utilities/verify_sprint2.py`

### Validation Scripts

**validate_dialects.py**
- Validates database dialect implementations
- Checks syntax generation for all databases
- Tests Anti-Hallucination layer
- **Usage:** `python scripts/utilities/validate_dialects.py`

### Test Scripts

**test_new_dialects.py**
- Tests newly added database dialects
- Verifies syntax correctness
- **Usage:** `python scripts/utilities/test_new_dialects.py`

**test_openrouter.py**
- Tests OpenRouter API integration
- Verifies LLM provider setup
- **Usage:** `python scripts/utilities/test_openrouter.py`

**test_orchestrator.py**
- Tests orchestrator functionality
- Validates stage coordination
- **Usage:** `python scripts/utilities/test_orchestrator.py`

**test_slr_integration.py**
- Tests SLR (Systematic Literature Review) integration
- Verifies search service functionality
- **Usage:** `python scripts/utilities/test_slr_integration.py`

### Maintenance Scripts

**fix_slr_imports.py**
- Fixes SLR import issues
- Maintenance utility for search integration
- **Usage:** `python scripts/utilities/fix_slr_imports.py`

---

## 🚀 Quick Start

### Run All Verifications

```bash
# Verify implementation
python scripts/utilities/verify_implementation.py

# Validate dialects
python scripts/utilities/validate_dialects.py

# Test OpenRouter
python scripts/utilities/test_openrouter.py
```

### Common Tasks

**Check if everything is working:**
```bash
python scripts/utilities/verify_implementation.py
```

**Validate query generation:**
```bash
python scripts/utilities/validate_dialects.py
```

**Test LLM integration:**
```bash
python scripts/utilities/test_openrouter.py
```

---

## 📋 Prerequisites

- Python 3.11+
- Virtual environment activated
- Dependencies installed: `pip install -r requirements.txt`
- `.env` configured (for LLM tests)

---

## 🔧 Script Details

### verify_implementation.py

**What it checks:**
- ✅ All stages registered in controller
- ✅ Services are importable
- ✅ Configuration loads correctly
- ✅ File structure is correct

**Expected output:**
```
✅ Stage 0: project-setup registered
✅ Stage 1: problem-framing registered
✅ Stage 2: research-questions registered
...
All verifications passed!
```

### validate_dialects.py

**What it validates:**
- ✅ All 7 database dialects work
- ✅ Query syntax is valid
- ✅ Field tags are correct
- ✅ Boolean operators are proper

**Expected output:**
```
Testing PubMed dialect... ✅
Testing Scopus dialect... ✅
Testing arXiv dialect... ✅
...
All dialects validated!
```

### test_openrouter.py

**What it tests:**
- ✅ API key is valid
- ✅ Model selection works
- ✅ Streaming is functional
- ✅ Error handling works

**Required:**
- `.env` with `LLM__OPENROUTER_API_KEY`

---

## 🐛 Troubleshooting

### Import Errors

```bash
# Make sure you're in project root
cd C:\Users\mouadh\Desktop\strategy-pipeline

# Then run scripts
python scripts/utilities/verify_implementation.py
```

### ModuleNotFoundError

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### API Key Errors (test_openrouter.py)

```bash
# Check your .env file
cat .env | grep OPENROUTER

# Or use environment variable
$env:LLM__OPENROUTER_API_KEY="sk-or-xxxxx"
python scripts/utilities/test_openrouter.py
```

---

## 📊 When to Use Each Script

| Scenario | Script |
|----------|--------|
| After fresh install | verify_implementation.py |
| After adding new dialect | validate_dialects.py, test_new_dialects.py |
| Testing LLM setup | test_openrouter.py |
| Before deployment | All verification scripts |
| Debugging imports | fix_slr_imports.py |
| After code changes | verify_implementation.py |

---

## 🔄 CI/CD Integration

These scripts can be used in continuous integration:

```yaml
# Example GitHub Actions workflow
- name: Verify Implementation
  run: python scripts/utilities/verify_implementation.py

- name: Validate Dialects
  run: python scripts/utilities/validate_dialects.py
```

---

## 📝 Adding New Utility Scripts

**Naming convention:**
- Verification: `verify_{feature}.py`
- Testing: `test_{feature}.py`
- Validation: `validate_{feature}.py`
- Maintenance: `fix_{issue}.py`

**Template:**
```python
"""Utility: {Description}

Usage:
    python scripts/utilities/{script_name}.py
"""

def main():
    print("Running {feature} utility...")
    # Your utility code here
    print("✅ Complete!")

if __name__ == "__main__":
    main()
```

---

## 💡 Best Practices

1. **Run before commits:** Use verification scripts before committing
2. **Test in isolation:** Each script should be self-contained
3. **Clear output:** Scripts should print what they're testing
4. **Exit codes:** Use `sys.exit(1)` on failure for CI/CD
5. **Documentation:** Update this README when adding scripts

---

## 🤝 Contributing

Adding a new utility script?

1. Create the script in `scripts/utilities/`
2. Add documentation to this README
3. Test it works from project root
4. Include usage example
5. Add to verification checklist if relevant

---

**Need help?** Check the main README.md or docs/INDEX.md

