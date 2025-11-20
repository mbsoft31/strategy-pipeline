This extension replaces the mock logic with a real connection to the **OpenAI API** (or a compatible interface). This is where the tool stops "pretending" and starts actually "thinking."

We will use the **Adapter Pattern** for the LLM provider so you can easily switch between OpenAI (Cloud) and Ollama (Local/Free) later without rewriting your pipeline.

---

### Prerequisites

You will need to install these packages:

```bash
pip install openai python-dotenv
```

### 1. Configuration (`.env` and `src/config.py`)

First, we standardize how we handle secrets. Never hardcode API keys.

**Create a file named `.env` in your root folder:**

```ini
# .env
LLM_PROVIDER=openai  # or "ollama"
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx  # Put your real key here
OPENAI_MODEL=gpt-4o-mini  # Cheap, fast, smart enough for dev
OLLAMA_BASE_URL=http://localhost:11434/v1
```

**Create `src/config.py`:**

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
    
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Ollama / Local Settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

    @classmethod
    def validate(cls):
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("Missing OPENAI_API_KEY in .env file.")
```

---

### 2. The Provider Layer (`src/services/llm_provider.py`)

This handles the raw network calls and ensures consistent behavior (like enforcing JSON output).

```python
import json
import re
from abc import ABC, abstractmethod
from openai import OpenAI
from src.config import Config

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        pass

    def clean_json_response(self, response: str) -> dict:
        """
        Helper to strip Markdown code blocks (```json ... ```) 
        and parse valid JSON from LLM output.
        """
        # Remove markdown backticks
        clean_str = re.sub(r"```json\s*", "", response)
        clean_str = re.sub(r"```\s*$", "", clean_str)
        clean_str = clean_str.strip()
        
        try:
            return json.loads(clean_str)
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error. Raw output: {response}")
            raise e

class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling OpenAI: {str(e)}"

class MockProvider(LLMProvider):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Return a dummy JSON string for testing without costs
        return '{"title": "Mock Title", "short_description": "Mock Desc", "discipline": "Mock Disc", "initial_keywords": ["test"]}'

def get_provider() -> LLMProvider:
    """Factory function to return the configured provider."""
    if Config.LLM_PROVIDER == "openai":
        return OpenAIProvider()
    else:
        print("Using Mock Provider (Check .env to switch to OpenAI)")
        return MockProvider()
```

---

### 3. The Prompts (`src/services/prompts.py`)

We write prompts that force the LLM to output specific JSON structures matching our Data Classes.

```python
# System Prompts
SYSTEM_PROMPT_GENERAL = (
    "You are an expert academic research consultant. "
    "You help PhD students structure their research projects. "
    "You strictly output valid JSON when requested."
)

SYSTEM_PROMPT_CRITIC = (
    "You are a strict research supervisor. "
    "Your job is to find flaws in research logic, vague definitions, and feasibility issues."
)

# User Prompts
PROMPT_STAGE0_CONTEXT = """
Analyze the following raw research idea and extract a structured Project Context.

Raw Idea: "{raw_idea}"

Return a JSON object with exactly these keys:
- "title": A formal academic title.
- "discipline": The primary field of study.
- "short_description": A 2-sentence academic summary.
- "initial_keywords": A list of 5-7 relevant search keywords.
- "constraints": A dictionary of implied constraints (e.g., time, method) if detected, else empty.
"""

PROMPT_STAGE1_CRITIQUE = """
Critique this draft context. Is the scope too broad? Is the language precise?
Context Title: {title}
Description: {description}

Return a JSON object with:
- "critique_summary": A paragraph explaining the flaws.
- "feasibility_score": A number 1-10.
"""

PROMPT_STAGE1_REFINE = """
Based on the critique below, generate a formal Problem Framing.

Context: {context_str}
Critique: {critique_str}

Return JSON with:
- "problem_statement": The refined problem.
- "research_gap": The gap in literature.
- "goals": List of 3 specific goals.
- "scope_in": List of what is IN scope.
- "scope_out": List of what is OUT of scope.
- "key_concepts": A list of objects {"label": "...", "type": "..."} (Types: Population, Intervention, Outcome).
"""
```

---

### 4. The Updated `ModelService` (`src/services/model_service.py`)

Now we wire it all together. The service calls the provider, parses the JSON, and populates the Python objects.

```python
from src.models import (
    ProjectContext, ModelMetadata, ProblemFraming, 
    ConceptModel, Concept, ConceptType, ApprovalStatus
)
from src.services.llm_provider import get_provider
from src.services.prompts import (
    SYSTEM_PROMPT_GENERAL, SYSTEM_PROMPT_CRITIC,
    PROMPT_STAGE0_CONTEXT, PROMPT_STAGE1_CRITIQUE, PROMPT_STAGE1_REFINE
)
from src.config import Config
import uuid

class ModelService:
    def __init__(self):
        # Load the configured provider (OpenAI or Mock)
        Config.validate()
        self.provider = get_provider()

    def suggest_project_context(self, raw_idea: str) -> tuple[ProjectContext, ModelMetadata]:
        """Stage 0: Convert raw text to structured Context."""
        
        # 1. Build Prompt
        user_prompt = PROMPT_STAGE0_CONTEXT.format(raw_idea=raw_idea)
        
        # 2. Call LLM
        print(f"   [ModelService] Calling {Config.LLM_PROVIDER} to frame idea...")
        raw_response = self.provider.generate(SYSTEM_PROMPT_GENERAL, user_prompt)
        
        # 3. Parse JSON
        data = self.provider.clean_json_response(raw_response)
        
        # 4. Map to Artifact
        draft = ProjectContext.create_empty(raw_idea)
        draft.title = data.get("title", "Untitled")
        draft.discipline = data.get("discipline", "General")
        draft.short_description = data.get("short_description", "")
        draft.initial_keywords = data.get("initial_keywords", [])
        draft.constraints = data.get("constraints", {})
        
        # 5. Metadata
        metadata = ModelMetadata(
            model_name=Config.OPENAI_MODEL,
            mode="api-call",
            notes="Generated via Stage 0 Prompt"
        )
        
        return draft, metadata

    def generate_problem_framing(self, context: ProjectContext) -> tuple[ProblemFraming, ConceptModel, ModelMetadata]:
        """Stage 1: The Critique Loop."""
        
        # Step A: Critique
        print(f"   [ModelService] Requesting Critique for '{context.title}'...")
        critique_prompt = PROMPT_STAGE1_CRITIQUE.format(
            title=context.title, 
            description=context.short_description
        )
        critique_raw = self.provider.generate(SYSTEM_PROMPT_CRITIC, critique_prompt)
        critique_data = self.provider.clean_json_response(critique_raw)
        
        critique_text = critique_data.get("critique_summary", "No critique generated.")
        
        # Step B: Refine & Frame
        print(f"   [ModelService] Refining Strategy based on critique...")
        refine_prompt = PROMPT_STAGE1_REFINE.format(
            context_str=context.short_description,
            critique_str=critique_text
        )
        refine_raw = self.provider.generate(SYSTEM_PROMPT_GENERAL, refine_prompt)
        refine_data = self.provider.clean_json_response(refine_raw)
        
        # Step C: Map to Artifacts
        # 1. Framing
        framing = ProblemFraming(
            project_id=context.id,
            problem_statement=refine_data.get("problem_statement", ""),
            research_gap=refine_data.get("research_gap", ""),
            goals=refine_data.get("goals", []),
            scope_in=refine_data.get("scope_in", []),
            scope_out=refine_data.get("scope_out", []),
            critique_report=critique_text
        )
        
        # 2. Concepts
        concepts_list = []
        for c_data in refine_data.get("key_concepts", []):
            # Simple mapper for types
            ctype_str = c_data.get("type", "Undefined").upper()
            try:
                ctype = ConceptType[ctype_str]
            except KeyError:
                ctype = ConceptType.UNDEFINED
                
            concepts_list.append(Concept(
                id=str(uuid.uuid4()),
                label=c_data.get("label", "Unknown"),
                type=ctype,
                description=c_data.get("label", "")
            ))
            
        concept_model = ConceptModel(
            project_id=context.id,
            concepts=concepts_list,
            relations=[] # We leave relations empty for now, or infer them in a future step
        )
        
        metadata = ModelMetadata(
            model_name=Config.OPENAI_MODEL,
            mode="chain-of-thought",
            notes=f"Critique Score: {critique_data.get('feasibility_score', 'N/A')}"
        )
        
        return framing, concept_model, metadata
```

---

### How to Test "The Magic"

1.  Fill in your `.env` file with a real OpenAI API Key.
2.  Run your existing `main_cli.py` (no changes needed there!).
3.  **Watch the console:**
    *   You will see slightly longer pauses (waiting for API).
    *   The output will be **significantly better**.
    *   The "Critique Report" will actually make sense based on your specific input.

**Example Real Output you might see:**
> **Input:** "using ai for farming"
>
> **Stage 0 Output:**
> Title: *AI-Driven Precision Agriculture Optimizations*
> Keywords: *["Computer Vision", "Crop Yield", "IoT", "Smart Farming"]*
>
> **Critique:** *"The term 'farming' is too broad. It implies both livestock and crop management. The proposal lacks specificity regarding the scale (industrial vs. smallholder)."*
>
> **Refined Scope:**
> *   **In Scope:** Smallholder crop monitoring, Pest detection via image recognition.
> *   **Out Scope:** Livestock automation, Heavy machinery robotics.

This is the moment your tool transforms from a "script" to an "intelligent agent."