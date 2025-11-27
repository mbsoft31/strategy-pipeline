# Installation Guide
**Having Issues?** [Report a Bug](https://github.com/mbsoft31/strategy-pipeline/issues)

---

```
python -m pytest tests/
# Run tests to verify

pip install -r requirements.txt --upgrade
# Update dependencies

git pull origin main
# Pull latest changes
```bash

## Updating

| Windows | ✅ Fully Supported | Windows 10+, PowerShell 5.1+ |
| macOS | ✅ Fully Supported | macOS 11+ |
| Linux | ✅ Fully Supported | Ubuntu 20.04+, Debian 11+ |
|----------|--------|-------|
| Platform | Status | Notes |

## Platform Support

- SSD for faster artifact loading
- 5GB disk space (for result storage)
- 8GB RAM
- Python 3.11+
### Recommended

- 1GB disk space
- 4GB RAM
- Python 3.10+
### Minimum

## System Requirements

- 🔧 [User Guide](../user-guide/quick-reference.md) - Comprehensive reference
- 📚 [Configuration Guide](configuration.md) - Advanced settings
- 📖 [Quick Start Tutorial](quick-start.md) - Build your first pipeline

## Next Steps

```
# Visit http://localhost:8000
mkdocs serve
# Serve documentation locally

pip install mkdocs mkdocs-material mkdocstrings[python]
# Install MkDocs
```bash

### Documentation Site

```
python -m src.main
cd ../..
# Start backend server

npm run build
npm install
cd frontend/strategy-pipeline-ui
# Install frontend dependencies
```bash

### Web Interface

## Optional Components

- Some APIs require registration (e.g., Semantic Scholar)
- Verify you're not behind a restrictive firewall
- Check internet connection
**Solution:**

**Problem:** `SearchService failed: Connection timeout`

### Database Connection Errors

- Ensure `.env` is in project root, not `src/` directory
- Check key hasn't expired
- Verify `.env` file exists and contains valid API key
**Solution:**

**Problem:** `openai.AuthenticationError: Incorrect API key`

### API Key Errors

```
pip install -e .
# Install in development mode

cd /path/to/strategy-pipeline
# Ensure you're in the project root
```bash
**Solution:**

**Problem:** `ModuleNotFoundError: No module named 'src'`

### Import Errors

## Troubleshooting

```
"
print(f'✅ Project created: {result.draft_artifact.id}')
result = controller.start_project('Test project')

)
    FilePersistenceService()
    SimpleModelService(),  # No API key needed
controller = PipelineController(

from src.services import SimpleModelService, FilePersistenceService
from src.controller import PipelineController
python -c "
# Create a test project
```bash

### 3. Test with Simple Example

```
python -c "from src.controller import PipelineController; print('✅ Installation successful')"
# Check imports

python -m pytest tests/
# Run tests
```bash

### 2. Verify Installation

```
SLR_MAILTO=your.email@example.com  # Required for some APIs
# Database Configuration (optional)

MODEL_MODE=intelligent  # or simple (for testing)
MODEL_NAME=gpt-4  # or claude-3-opus-20240229
# Model Selection (optional)

ANTHROPIC_API_KEY=sk-ant-...
# OR
OPENAI_API_KEY=sk-...
# LLM Provider (choose one)
```bash

Create a `.env` file in the project root:

### 1. API Keys

## Configuration

- Testing and development tools
- FastAPI for web interface (optional)
- arXiv, Crossref, OpenAlex, Semantic Scholar API clients
- OpenAI/Anthropic SDKs for LLM integration
This installs:

```
pip install -r requirements.txt
```bash

### 3. Install Dependencies

```
conda activate strategy-pipeline
conda create -n strategy-pipeline python=3.10
```bash
**Using conda:**

```
venv\Scripts\activate
# Activate on Windows:

source venv/bin/activate
# Activate on Linux/Mac:

python -m venv venv
```bash
**Using venv (recommended):**

### 2. Create Virtual Environment

```
cd strategy-pipeline
git clone https://github.com/mbsoft31/strategy-pipeline.git
```bash

### 1. Clone Repository

## Quick Install

- **API Keys:** OpenAI or Anthropic (for LLM services)
- **Git:** For cloning the repository
- **Package Manager:** pip or conda
- **Python:** 3.10 or higher

## Prerequisites


