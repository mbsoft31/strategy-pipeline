# Sprint 2: Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `openai>=1.3.0` - For OpenAI API (optional)
- `requests>=2.31.0` - For OpenAlex validation
- `pydantic>=2.5.0` - For configuration
- `pytest>=7.4.0` - For testing

### Step 2: Configure Provider

**Option A: Free Testing (No API key needed)**

```bash
# .env file (or leave default)
LLM__PROVIDER=mock
```

**Option B: Production with OpenAI**

```bash
# .env file
LLM__PROVIDER=openai
LLM__OPENAI_API_KEY=sk-proj-your-key-here
LLM__OPENAI_MODEL=gpt-4o-mini
LLM__OPENAI_TEMPERATURE=0.7
```

Get your API key from: https://platform.openai.com/api-keys

### Step 3: Run the Demo

```bash
python demo_sprint2.py
```

You'll see:
1. ✅ Project context generated from raw idea
2. ✅ AI critique with feasibility score
3. ✅ Refined problem framing
4. ✅ Concepts extracted and validated
5. ✅ Full critique report with OpenAlex validation

### Step 4: Verify Tests (Optional)

```bash
pytest tests/test_llm_provider.py tests/test_validation_service.py -v
```

Expected: 19+ tests passing

---

## 📖 Usage Examples

### Example 1: Basic Workflow

```python
from src.services.intelligent_model_service import IntelligentModelService

# Initialize service (uses config from .env)
service = IntelligentModelService()

# Stage 0: Generate project context
raw_idea = "I want to research LLM hallucinations in healthcare"
context, meta = service.suggest_project_context(raw_idea)

print(f"Title: {context.title}")
print(f"Keywords: {context.initial_keywords}")

# Stage 1: Generate problem framing with validation
framing, concepts, meta = service.generate_problem_framing(context)

print(f"\nProblem: {framing.problem_statement}")
print(f"Goals: {framing.goals}")
print(f"Concepts: {[c.label for c in concepts.concepts]}")

# View full critique + validation report
print(f"\n{framing.critique_report}")
```

### Example 2: Direct Provider Usage

```python
from src.services.llm_provider import get_llm_provider, MockProvider
from src.services.prompts import SYSTEM_PROMPT_METHODOLOGIST, PROMPT_STAGE0_CONTEXT

# Get configured provider
provider = get_llm_provider()

# Or use specific provider
provider = MockProvider()

# Generate response
prompt = PROMPT_STAGE0_CONTEXT.format(raw_idea="Research AI ethics")
response = provider.generate(SYSTEM_PROMPT_METHODOLOGIST, prompt)
data = provider.clean_json_response(response)

print(data["title"])
print(data["discipline"])
```

### Example 3: Validation Service

```python
from src.services.validation_service import ValidationService

validator = ValidationService()

# Validate single term
result = validator.validate_term("machine learning")
print(f"Hit count: {result.hit_count}")
print(f"Valid: {result.is_valid}")
print(f"Severity: {result.severity}")

# Validate batch
terms = ["deep learning", "neural networks", "fake term xyz"]
report = validator.validate_concept_list(terms)

print(f"\nSummary: {report.summary}")
print(f"Valid: {report.valid_count}/{report.total_terms}")
print(f"Warnings: {report.warning_count}")
print(f"Critical: {report.critical_count}")

for term, res in report.results.items():
    print(f"  {term}: {res.hit_count} works ({res.severity})")
```

---

## 🔧 Configuration Options

### LLM Settings

```bash
# Provider selection
LLM__PROVIDER=mock              # mock, openai, cached

# OpenAI settings (if provider=openai)
LLM__OPENAI_API_KEY=sk-...      # Your API key
LLM__OPENAI_MODEL=gpt-4o-mini   # or gpt-4, gpt-3.5-turbo
LLM__OPENAI_TEMPERATURE=0.7     # 0.0 to 2.0
LLM__OPENAI_MAX_TOKENS=         # Leave empty for default
LLM__TIMEOUT=30                 # Request timeout in seconds
```

### Validation Settings

```bash
# OpenAlex validation (free, no auth)
VALIDATION__OPENALEX_MAILTO=your.email@example.com  # Optional but polite
VALIDATION__OPENALEX_RATE_LIMIT=9.0                # Requests per second
VALIDATION__OPENALEX_TIMEOUT=30                     # Request timeout
VALIDATION__OPENALEX_CACHE_ENABLED=True            # Cache results
VALIDATION__OPENALEX_CACHE_TTL=86400               # Cache TTL (24 hours)
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_llm_provider.py -v
pytest tests/test_validation_service.py -v
```

### Run With Coverage

```bash
pytest tests/ --cov=src/services --cov-report=html
```

### Skip OpenAI Tests (if openai not installed)

```bash
pytest tests/ -v -m "not skipif"
```

---

## 🐛 Troubleshooting

### Issue: "OpenAI API key not found"

**Solution:**
```bash
# Check .env file exists
ls .env

# Check value is set
cat .env | grep OPENAI_API_KEY

# Or use environment variable
export LLM__OPENAI_API_KEY=sk-your-key
```

### Issue: "openai package not installed"

**Solution:**
```bash
pip install openai>=1.3.0
```

Or use Mock provider:
```bash
# .env
LLM__PROVIDER=mock
```

### Issue: "OpenAlex API timeout"

**Solution:**
```bash
# Increase timeout in .env
VALIDATION__OPENALEX_TIMEOUT=60

# Or check internet connection
ping api.openalex.org
```

### Issue: Tests failing

**Solution:**
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Clear cache
pytest --cache-clear

# Run with verbose output
pytest tests/ -vv
```

---

## 📊 Expected Output

### demo_sprint2.py Output:

```
================================================================================
 SPRINT 2 DEMO: LLM Integration with Validation
================================================================================

📊 Configuration:
   LLM Provider: mock
   Model: gpt-4o-mini
   Temperature: 0.7

🔧 Initializing IntelligentModelService...

================================================================================
 STAGE 0: Project Context Generation
================================================================================

💡 Raw Research Idea:
    I want to research how large language models like GPT-4 and Claude 
    sometimes generate false information when used in clinical decision 
    support systems...

✅ Project Context Generated:
   Title: Mock Project: AI in Healthcare Decision Support
   Discipline: Health Informatics
   Keywords: LLM, Hallucination, Clinical Decision Support, Patient Safety, Medical AI
   Model: mock

================================================================================
 STAGE 1: Problem Framing (Draft → Critique → Refine → Validate)
================================================================================

⏳ Running critique loop and validation...

✅ Problem Framing Complete!

📝 Problem Statement:
   Healthcare systems lack validated methods to detect and quantify 
   hallucinations in Large Language Model outputs used for clinical 
   decision support, creating potential patient safety risks.

🔍 Research Gap:
   No standardized metrics exist for measuring LLM factuality in clinical 
   contexts...

🎯 Goals:
   1. Define operational metrics for detecting LLM hallucinations
   2. Benchmark hallucination rates across GPT-4, Claude, and Llama-2
   3. Propose a validation framework for medical AI systems

✅ Scope IN:
   • Clinical notes and summaries
   • Commercial LLMs (GPT-4, Claude, Llama-2)
   • English language medical text
   • Factual accuracy as primary outcome

❌ Scope OUT:
   • Medical imaging or diagnostic AI
   • Patient-facing chatbots
   • Non-English languages
   • Predictive models or risk scores

🧩 Concepts Extracted: 5
   • Large Language Models (Intervention)
   • Clinical Notes (Population)
   • Hallucination Detection (Outcome)
   • Patient Safety (Outcome)
   • Validation Framework (Methodology)

================================================================================
 CRITIQUE & VALIDATION REPORT
================================================================================

[Full critique report with OpenAlex validation results...]

================================================================================
 SUMMARY
================================================================================

✅ Workflow Complete!
   Model: mock
   Mode: critique-refine-validate
   Concepts: 5
   Goals: 3

💡 Next Steps:
   1. Review the critique report for validation warnings
   2. Check OpenAlex hit counts for each concept
   3. Refine any terms with 0 hits (hallucinations)
   4. Approve the framing to move to Stage 2

🎉 Demo complete! This is production-ready validated AI.
```

---

## 🎓 Learn More

- **Full Documentation**: `SPRINT2_COMPLETE.md`
- **Implementation Plan**: `plan-llmIntegrationWithValidation.prompt.md`
- **Final Summary**: `SPRINT2_FINAL_SUMMARY.md`
- **Architecture**: `docs/architecture-overview.md`

---

## 💡 Tips

1. **Start with Mock** - Test the workflow for free before using OpenAI
2. **Review Critique Reports** - The AI's reasoning is valuable for learning
3. **Check Validation** - Always verify terms with 0 hits (hallucinations)
4. **Use GPT-4o-mini** - Costs 10x less than GPT-4, almost as good
5. **Cache Results** - Enable OpenAlex caching to speed up repeated queries

---

## 🚀 You're Ready!

Sprint 2 is complete and production-ready. The validated AI research assistant is working and tested.

**Try it now:**
```bash
python demo_sprint2.py
```

Have fun exploring the critique loop and validation! 🎉

