# Examples & Demos

This folder contains example scripts and demonstrations of the Strategy Pipeline functionality.

## 📁 Structure

```
examples/
├── demos/              # Demo scripts showing different features
└── README.md          # This file
```

## 🎯 Demo Scripts

### Core Pipeline Demos

**demo_full_pipeline.py**
- Complete pipeline execution (Stages 0-4)
- Uses IntelligentModelService with LLM
- Shows all stages in sequence
- **Usage:** `python examples/demos/demo_full_pipeline.py`

**demo_workflow.py**
- Workflow demonstration
- Shows stage progression and gating
- **Usage:** `python examples/demos/demo_workflow.py`

### Feature-Specific Demos

**demo_syntax_engine.py**
- Demonstrates Anti-Hallucination syntax engine
- Shows query generation for different databases
- Proves "moat" against ChatGPT
- **Usage:** `python examples/demos/demo_syntax_engine.py`

**demo_synthesis.py**
- LLM synthesis and critique loop demonstration
- Shows problem framing with validation
- **Usage:** `python examples/demos/demo_synthesis.py`

### Integration Demos

**demo_slr_integration.py**
- Systematic Literature Review integration
- Shows search service usage
- **Usage:** `python examples/demos/demo_slr_integration.py`

**demo_autonomous_agent.py**
- Autonomous agent demonstration
- AI-driven research workflow
- **Usage:** `python examples/demos/demo_autonomous_agent.py`

### Sprint Demos

**demo_sprint2.py**
- Sprint 2 features demonstration
- Problem framing and research questions
- **Usage:** `python examples/demos/demo_sprint2.py`

---

## 🚀 Quick Start

### Run the Full Pipeline Demo

```bash
# Make sure you're in the project root
cd C:\Users\mouadh\Desktop\strategy-pipeline

# Activate virtual environment
.venv\Scripts\activate

# Run demo
python examples/demos/demo_full_pipeline.py
```

### Run Syntax Engine Demo

```bash
python examples/demos/demo_syntax_engine.py
```

---

## 📋 Prerequisites

All demos require:
- Python 3.11+
- Virtual environment activated
- Dependencies installed: `pip install -r requirements.txt`

Some demos require:
- `.env` file configured with LLM provider
- OpenAI/OpenRouter API key (or use mock mode)

---

## 🎓 Learning Path

**New to the project?** Run demos in this order:

1. **demo_syntax_engine.py** - Understand the Anti-Hallucination layer
2. **demo_workflow.py** - See how stages connect
3. **demo_full_pipeline.py** - Experience the complete pipeline
4. **demo_synthesis.py** - Understand LLM integration
5. **demo_slr_integration.py** - Explore search capabilities

---

## 🔧 Configuration

### Using Mock Mode (No API Key Needed)

Edit your `.env`:
```env
LLM__PROVIDER=mock
```

### Using Real LLM

Edit your `.env`:
```env
LLM__PROVIDER=openai
LLM__OPENAI_API_KEY=sk-proj-xxxxx
LLM__OPENAI_MODEL=gpt-4o-mini
```

Or use OpenRouter:
```env
LLM__PROVIDER=openrouter
LLM__OPENROUTER_API_KEY=sk-or-xxxxx
LLM__OPENROUTER_MODEL=mistralai/mistral-nemo
```

---

## 📊 What Each Demo Shows

| Demo | Shows | LLM Required |
|------|-------|--------------|
| demo_full_pipeline.py | Complete pipeline Stages 0-4 | Optional |
| demo_syntax_engine.py | Query generation without LLM | No |
| demo_synthesis.py | LLM critique loop | Yes |
| demo_workflow.py | Stage progression | Optional |
| demo_slr_integration.py | Search APIs | No |
| demo_autonomous_agent.py | AI automation | Yes |
| demo_sprint2.py | Sprint 2 features | Optional |

---

## 💡 Tips

- **Start simple:** Begin with `demo_syntax_engine.py` (no API key needed)
- **Use mock mode:** Test pipeline logic without LLM costs
- **Check logs:** Demos show progress and debug information
- **Modify freely:** Demos are meant to be experimented with!

---

## 🐛 Troubleshooting

**ImportError:**
```bash
# Make sure you're in project root
cd C:\Users\mouadh\Desktop\strategy-pipeline
python examples/demos/demo_full_pipeline.py
```

**API Key Error:**
```bash
# Use mock mode
# Edit .env and set: LLM__PROVIDER=mock
```

**ModuleNotFoundError:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📝 Creating Your Own Demo

Copy an existing demo and modify it:

```python
"""My Custom Demo"""
from src.controller import PipelineController
from src.services import IntelligentModelService, FilePersistenceService

# Your custom demo code here
controller = PipelineController(
    model_service=IntelligentModelService(),
    persistence_service=FilePersistenceService()
)

# Run stages and experiment!
```

---

## 🤝 Contributing

Have a cool demo? Add it here and update this README!

**Guidelines:**
- Name format: `demo_{feature}.py`
- Include docstring at top
- Add usage example in this README
- Keep it simple and focused

---

**Need help?** Check the main README.md or docs/INDEX.md

