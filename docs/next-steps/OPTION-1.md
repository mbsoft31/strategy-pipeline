This is a fully detailed architectural expansion for **Stage 1**.

We are moving beyond simple "text generation" into **Agentic Workflow Patterns**. specifically the **Reflection Pattern** (Draft $\rightarrow$ Critique $\rightarrow$ Refine).

### The Architecture Changes

1.  **New Artifacts (`src/models.py`)**: We need rigid structures for `ProblemFraming` (textual) and `ConceptModel` (graph-based).
2.  **Prompt Engineering (`src/prompts.py`)**: We separate prompts from code. This is vital for maintainability.
3.  **The "Supervisor" Logic (`src/services/model_service.py`)**: We simulate a multi-step chain-of-thought process.
4.  **The Stage Logic (`src/stages/problem_framing.py`)**: Orchestrates the flow.

---

### 1. `src/models.py` (Updated)

We add the specific artifacts required for academic framing.

```python
# ... (previous imports)
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

# ... (Previous ModelMetadata, ApprovalStatus, ProjectContext remain the same)

# --- NEW ENUMS ---
class ConceptType(Enum):
    POPULATION = "Population"
    INTERVENTION = "Intervention/Exposure"
    COMPARATOR = "Comparator"
    OUTCOME = "Outcome"
    METHOD = "Methodology"
    CONTEXT = "Context"
    UNDEFINED = "Undefined"

class RelationType(Enum):
    INFLUENCES = "Influences"
    ASSOCIATED_WITH = "Associated With"
    COMPARED_TO = "Compared To"
    PREVENTS = "Prevents"
    CAUSES = "Causes"

# --- NEW ARTIFACTS ---

@dataclass
class Concept:
    id: str
    label: str
    type: ConceptType
    description: str

@dataclass
class Relation:
    id: str
    source_concept_id: str
    target_concept_id: str
    type: RelationType
    description: Optional[str] = None

@dataclass
class ConceptModel:
    """Represents the mental graph of the research."""
    project_id: str
    concepts: List[Concept] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    
    # Metadata
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ApprovalStatus = ApprovalStatus.DRAFT
    model_metadata: Optional['ModelMetadata'] = None

@dataclass
class ProblemFraming:
    """The narrative structure of the research."""
    project_id: str
    problem_statement: str  # The "Hook"
    research_gap: str       # What is missing in literature
    goals: List[str]        # e.g. "To evaluate...", "To design..."
    scope_in: List[str]     # What is explicitly included
    scope_out: List[str]    # What is explicitly excluded
    critique_report: str    # <--- THE CRITIC'S FEEDBACK STORED HERE
    
    # Metadata
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ApprovalStatus = ApprovalStatus.DRAFT
    model_metadata: Optional['ModelMetadata'] = None
```

---

### 2. `src/services/prompts.py` (New File)

We extract the "intelligence" into templates. This allows you to tweak the "Supervisor's" personality without breaking the code.

```python
# src/services/prompts.py

SYSTEM_PROMPT_ACADEMIC = """
You are a strict Senior Research Supervisor. 
You value precision, feasibility, and methodological rigor. 
You hate vague terms like "impact" or "issues" without definition.
"""

PROMPT_DRAFT_FRAMING = """
Context: {project_context}

Task: Draft a preliminary problem framing.
1. Write a 1-sentence Problem Statement.
2. Identify the Research Gap.
3. List 3 specific Research Goals.
4. Define strictly what is In Scope vs Out of Scope.
"""

PROMPT_CRITIQUE = """
Critique the following draft research framing:
{draft_framing}

Check for:
1. Vagueness: Are the population and intervention defined?
2. Feasibility: Is this too broad for a single PhD/Study?
3. Tautology: Is the research question circular?

Return a critique summary.
"""

PROMPT_REFINE_AND_EXTRACT = """
Original Draft: {draft_framing}
Critique: {critique}

Task: 
1. Rewrite the Problem Statement and Scope to address the critique.
2. Extract key Concepts (Variables) and classify them (Population, Intervention, Outcome).
3. Return the result as JSON.
"""
```

---

### 3. `src/services/model_service.py` (The Critic Loop)

Here we implement the logic. Note: Since we don't have a live LLM key here, I have implemented a **"Mock Simulation"** of what an LLM would do. In a real implementation, `_call_llm` would hit OpenAI.

```python
import time
import uuid
from src.models import (
    ProjectContext, ProblemFraming, ConceptModel, 
    Concept, Relation, ConceptType, RelationType, 
    ModelMetadata, ApprovalStatus
)
from src.services.prompts import PROMPT_DRAFT_FRAMING, PROMPT_CRITIQUE

class ModelService:
    def __init__(self):
        self.mode = "mock-chain-of-thought"

    def generate_problem_framing(self, context: ProjectContext) -> tuple[ProblemFraming, ConceptModel, ModelMetadata]:
        """
        Orchestrates the Draft -> Critique -> Refine loop.
        """
        print(f"   [ModelService] 1. Drafting initial ideas for '{context.title}'...")
        # In real life: draft = llm.call(PROMPT_DRAFT_FRAMING.format(context))
        time.sleep(0.5) 
        
        print(f"   [ModelService] 2. Running 'Critic' module (Supervisor Persona)...")
        # In real life: critique = llm.call(PROMPT_CRITIQUE.format(draft))
        time.sleep(0.5)
        
        # Simulate a specific critique based on the input to show value
        simulated_critique = (
            "The initial scope was too broad. 'Climate Change' is not a variable. "
            "Refined to 'localized flood risk' to ensure feasibility. "
            "Added explicit exclusion of 'policy making' to focus on technical adaptation."
        )
        
        print(f"   [ModelService] 3. Refining and extracting concepts based on critique...")
        time.sleep(0.5)

        # --- CONSTRUCTING THE REFINED OUTPUT (MOCK) ---
        
        # 1. The Framing Artifact
        framing = ProblemFraming(
            project_id=context.id,
            problem_statement=f"Current approaches to {context.initial_keywords[0] if context.initial_keywords else 'the topic'} lack granular data integration, leading to suboptimal adaptation strategies.",
            research_gap="Lack of real-time sensor integration in current predictive models.",
            goals=["To characterize the latency of current models", "To design a fusion architecture", "To evaluate performance against historical data"],
            scope_in=["Technical implementation", "Deep Learning models (CNN/LSTM)", "Historical weather data"],
            scope_out=["Policy formulation", "Economic cost-benefit analysis", "Hardware sensor design"],
            critique_report=simulated_critique # <--- Storing the critique!
        )
        
        # 2. The Concept Model Artifact
        c1 = Concept(str(uuid.uuid4()), "Deep Learning", ConceptType.INTERVENTION, "CNN and LSTM architectures")
        c2 = Concept(str(uuid.uuid4()), "Flood Risk", ConceptType.OUTCOME, "Probability of water level > threshold")
        c3 = Concept(str(uuid.uuid4()), "Coastal Urban Areas", ConceptType.POPULATION, "High-density cities <10m elevation")
        
        relation = Relation(str(uuid.uuid4()), c1.id, c2.id, RelationType.PREVENTS, "Predicts and allows mitigation of")

        concept_model = ConceptModel(
            project_id=context.id,
            concepts=[c1, c2, c3],
            relations=[relation]
        )

        metadata = ModelMetadata(
            model_name="mock-gpt-4-turbo", 
            mode="chain-of-thought",
            notes="Performed 3-step critique loop."
        )

        return framing, concept_model, metadata
```

---

### 4. `src/stages/problem_framing.py` (The Stage)

This stage is slightly more complex because it produces **two** artifacts (`Framing` and `ConceptModel`).

```python
from src.stages.base import BaseStage, StageResult
from src.models import ProjectContext, ProblemFraming, ConceptModel

class ProblemFramingStage(BaseStage):
    def execute(self, project_id: str) -> StageResult:
        # 1. Load the Dependency (Project Context)
        # In a real app, we load from persistence. 
        # For this demo, we assume the controller passes the context object or we load it.
        context = self.persistence_service.load_artifact("ProjectContext", project_id, ProjectContext)
        
        if not context:
            raise ValueError(f"Cannot run Stage 1: ProjectContext for {project_id} not found.")

        # 2. Execute the AI Loop
        framing_draft, concept_draft, metadata = self.model_service.generate_problem_framing(context)

        # 3. Persist Drafts
        self.persistence_service.save_artifact(framing_draft, framing_draft.id, "ProblemFraming")
        self.persistence_service.save_artifact(concept_draft, concept_draft.id, "ConceptModel")

        # 4. Construct UI Return
        # We explicitly highlight the critique to the user
        return StageResult(
            draft_artifact={"framing": framing_draft, "concepts": concept_draft},
            metadata=metadata,
            ui_prompt=(
                f"I have framed the problem. \n"
                f"CRITIC REPORT: {framing_draft.critique_report}\n"
                f"Please review the Scope (In/Out) and the Concept Map."
            ),
            next_steps=["Refine Scope", "Add/Remove Concepts", "Approve"]
        )
```

---

### 5. `main_cli.py` (Integration Test)

Let's update the CLI to run Stage 0, then automatically transition to Stage 1 to show the flow.

```python
# ... (imports from previous example)
from src.stages.project_setup import ProjectSetupStage
from src.stages.problem_framing import ProblemFramingStage
from src.models import ProjectContext

# ... (previous code)

def main():
    # 1. Setup
    model_service = ModelService()
    persistence_service = PersistenceService()
    
    # 2. Run Stage 0 (Project Setup)
    print("\n--- STAGE 0: PROJECT SETUP ---")
    raw_idea = "Deep learning for climate adaptation"
    setup_stage = ProjectSetupStage(model_service, persistence_service)
    result_0 = setup_stage.execute(raw_idea=raw_idea)
    
    # Simulate User Approval
    context = result_0.draft_artifact
    context.title = "Deep Learning for Coastal Flood Prediction" # User edit
    persistence_service.save_artifact(context, context.id, "ProjectContext") # Save approved
    print(f"[User] Approved Context: {context.title}")

    # 3. Run Stage 1 (Problem Framing)
    print("\n--- STAGE 1: PROBLEM FRAMING & CRITIC ---")
    framing_stage = ProblemFramingStage(model_service, persistence_service)
    
    # Pass the Project ID from Stage 0
    result_1 = framing_stage.execute(project_id=context.id)
    
    framing = result_1.draft_artifact['framing']
    concepts = result_1.draft_artifact['concepts']

    # 4. Display the "Critic" Result
    print("\n" + "="*20 + " AI CRITIQUE REPORT " + "="*20)
    print(f"\"{framing.critique_report}\"")
    print("="*60)
    
    print("\n[Draft Problem Statement]")
    print(framing.problem_statement)
    
    print("\n[Draft Scope]")
    print(f"IN SCOPE: {framing.scope_in}")
    print(f"OUT SCOPE: {framing.scope_out}")
    
    print("\n[Concept Model]")
    for c in concepts.concepts:
        print(f"- [{c.type.value}] {c.label}: {c.description}")

if __name__ == "__main__":
    main()
```

### How this moves you forward

1.  **Complexity Handling:** You are now handling multiple artifacts (`Framing` + `ConceptModel`) linked by a `project_id`.
2.  **The "Critic" Pattern:** The `critique_report` field in the artifact demonstrates that the AI isn't just generating text; it's *evaluating* itself.
3.  **Visual Potential:** The `ConceptModel` output (Nodes/Edges) is ready to be plugged into a graph visualizer in the future.

**Next Step:** Copy these updated files into your project structure. Run `main_cli.py`. You will see the simulated "Thinking" steps and the critique output.