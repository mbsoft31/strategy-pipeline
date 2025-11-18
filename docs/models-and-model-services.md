# Core Data Models and Model-Service Abstractions

This document defines the core Python-facing models (artifacts) used in the HITL research-strategy pipeline, and a high-level abstraction for language-model (LLM) and small/local-model (SLM) services.

The goal is to:
- Keep stages **model-agnostic** (they don’t talk directly to specific APIs).
- Make it easy to swap an online LLM (e.g., cloud-hosted) and a local SLM/NLP pipeline.
- Support `draft` vs `approved` states and log how artifacts were generated.

This is a design document; implementation details (which library, which provider) come later.

---

## 1. Core data models (artifacts)

Below are conceptual Python models; in code these will likely be `@dataclass`-es or Pydantic models.

### 1.1 Common types

**Model metadata** – tracks how any artifact was generated/assisted by models:

- `ModelMetadata`:
  - `model_name: str` – identifier for the model used (e.g., `openai:gpt-4.1`, `local:miniLM`).
  - `mode: str` – e.g., `"llm"`, `"slm"`, `"hybrid"`.
  - `prompt_version: Optional[str]` – version or id of the prompt template.
  - `generated_at: datetime` – timestamp of generation.
  - `notes: Optional[str]` – free-form notes (e.g., temperature, max_tokens, etc.).

**Approval/checkpoint status** – for HITL states:

- `ApprovalStatus` (enum-like):
  - `DRAFT`
  - `UNDER_REVIEW`
  - `APPROVED`
  - `APPROVED_WITH_NOTES`
  - `REQUIRES_REVISION`

Many artifacts will have:

- `status: ApprovalStatus`
- `model_metadata: Optional[ModelMetadata]`
- `user_notes: Optional[str]`

### 1.2 ProjectContext

Represents the project-level metadata and initial framing.

Fields (initial proposal):

- `id: str` – unique project id.
- `title: str`
- `short_description: str`
- `discipline: Optional[str]`
- `subfield: Optional[str]`
- `application_area: Optional[str]`
- `constraints: Dict[str, Any]` – e.g., `{"time_horizon": "6 months", "methods_preference": "mixed"}`.
- `initial_keywords: List[str]`
- `created_at: datetime`
- `updated_at: datetime`
- `status: ApprovalStatus`
- `model_metadata: Optional[ModelMetadata]`
- `user_notes: Optional[str]`

### 1.3 ProblemFraming

Summarizes the problem statement, goals, and scope.

Fields:

- `project_id: str`
- `problem_statement: str`
- `goals: List[str]`
- `scope_in: List[str]` – aspects explicitly in scope.
- `scope_out: List[str]` – aspects explicitly out of scope.
- `stakeholders: List[str]`
- `created_at: datetime`
- `updated_at: datetime`
- `status: ApprovalStatus`
- `model_metadata: Optional[ModelMetadata]`
- `user_notes: Optional[str]`

### 1.4 ConceptModel

Captures key concepts and relations derived from the problem framing.

**Concept:**

- `id: str`
- `label: str`
- `description: str`
- `type: str` – e.g., `"population"`, `"intervention"`, `"outcome"`, `"method"`, `"context"`.

**Relation:**

- `id: str`
- `source_id: str` – concept id.
- `target_id: str` – concept id.
- `relation_type: str` – e.g., `"influences"`, `"associated_with"`, `"compared_to"`.
- `description: Optional[str]`

**ConceptModel fields:**

- `project_id: str`
- `concepts: List[Concept]`
- `relations: List[Relation]`
- `created_at: datetime`
- `updated_at: datetime`
- `status: ApprovalStatus`
- `model_metadata: Optional[ModelMetadata]`
- `user_notes: Optional[str]`

### 1.5 ResearchQuestionSet

Represents the structured collection of research questions.

**ResearchQuestion:**

- `id: str`
- `text: str`
- `type: str` – e.g., `"descriptive"`, `"explanatory"`, `"evaluative"`, `"design"`.
- `linked_concept_ids: List[str]` – references into `ConceptModel.concepts`.
- `priority: str` – e.g., `"must_have"`, `"nice_to_have"`.
- `methodological_lens: Optional[str]` – free-text, e.g., `"qualitative"`, `"mixed"`.

**ResearchQuestionSet fields:**

- `project_id: str`
- `questions: List[ResearchQuestion]`
- `created_at: datetime`
- `updated_at: datetime`
- `status: ApprovalStatus`
- `model_metadata: Optional[ModelMetadata]`
- `user_notes: Optional[str]`

### 1.6 SearchConceptBlocks & DatabaseQueryPlan

**SearchConceptBlock:**

Represents a group of synonymous/related terms for one conceptual block.

- `id: str`
- `label: str` – e.g., `"Population"`, `"Intervention"`.
- `description: Optional[str]`
- `terms_included: List[str]`
- `terms_excluded: List[str]`

**SearchConceptBlocks container:**

- `project_id: str`
- `blocks: List[SearchConceptBlock]`
- `created_at: datetime`
- `updated_at: datetime`
- `status: ApprovalStatus`
- `model_metadata: Optional[ModelMetadata]`
- `user_notes: Optional[str]`

**DatabaseQuery:**

- `id: str`
- `database_name: str` – e.g., `"pubmed"`, `"scopus"`.
- `query_blocks: List[str]` – references or labels for `SearchConceptBlock` ids.
- `boolean_query_string: str` – the final string to paste into the database.
- `notes: Optional[str]`
- `hit_count_estimate: Optional[int]` – set by user after test runs.

**DatabaseQueryPlan:**

- `project_id: str`
- `queries: List[DatabaseQuery]`
- `created_at: datetime`
- `updated_at: datetime`
- `status: ApprovalStatus`
- `model_metadata: Optional[ModelMetadata]`
- `user_notes: Optional[str]`

### 1.7 ScreeningCriteria & ScreeningChecklist

**Criterion:**

- `id: str`
- `text: str`
- `category: str` – e.g., `"population"`, `"design"`, `"outcome"`, `"time"`.
- `type: str` – `"inclusion"` or `"exclusion"`.
- `mandatory: bool`
- `examples: Optional[List[str]]`

**ScreeningCriteria:**

- `project_id: str`
- `criteria: List[Criterion]`
- `version: str`
- `created_at: datetime`
- `updated_at: datetime`
- `status: ApprovalStatus`
- `model_metadata: Optional[ModelMetadata]`
- `user_notes: Optional[str]`

**ScreeningQuestion:**

- `id: str`
- `text: str`
- `applies_to_stage: str` – e.g., `"title_abstract"`, `"full_text"`.

**ScreeningChecklist:**

- `project_id: str`
- `questions: List[ScreeningQuestion]`
- `created_at: datetime`
- `updated_at: datetime`
- `status: ApprovalStatus`
- `model_metadata: Optional[ModelMetadata]`
- `user_notes: Optional[str]`

### 1.8 StrategyPackage

Represents a bundle that ties together all artifacts for export.

Fields:

- `project_id: str`
- `context: ProjectContext`
- `problem_framing: ProblemFraming`
- `concept_model: ConceptModel`
- `research_questions: ResearchQuestionSet`
- `search_concept_blocks: SearchConceptBlocks`
- `database_query_plan: DatabaseQueryPlan`
- `screening_criteria: ScreeningCriteria`
- `screening_checklist: Optional[ScreeningChecklist]`
- `generated_summary_markdown: str`
- `metadata: Dict[str, Any]` – includes version, timestamps, tool version, author.

---

## 2. Model-service abstractions (LLM & SLM)

To leverage both LLMs and local SLM/NLP components, we define a high-level `ModelService` interface, and optionally sub-interfaces for LLM and SLM.

Stages call **semantic methods** on this service instead of calling providers directly.

### 2.1 High-level ModelService interface (conceptual)

Key responsibilities:

- Generate draft artifacts or parts of artifacts.
- Provide language-aware utilities (synonyms, rephrasing, classification).
- Combine LLM and SLM under one API.

Example conceptual interface (Python-ish, not final code):

- `class ModelService:`
  - `def suggest_project_context(self, raw_idea: str) -> Tuple[ProjectContext, ModelMetadata]: ...`
  - `def generate_problem_framing(self, context: ProjectContext) -> Tuple[ProblemFraming, ConceptModel, ModelMetadata]: ...`
  - `def generate_research_questions(self, framing: ProblemFraming, concepts: ConceptModel) -> Tuple[ResearchQuestionSet, ModelMetadata]: ...`
  - `def expand_search_terms(self, concepts: ConceptModel, rqs: ResearchQuestionSet) -> Tuple[SearchConceptBlocks, ModelMetadata]: ...`
  - `def build_database_queries(self, blocks: SearchConceptBlocks, db_names: List[str]) -> Tuple[DatabaseQueryPlan, ModelMetadata]: ...`
  - `def draft_screening_criteria(self, rqs: ResearchQuestionSet, blocks: SearchConceptBlocks) -> Tuple[ScreeningCriteria, Optional[ScreeningChecklist], ModelMetadata]: ...`
  - `def summarize_strategy(self, pkg: "StrategyPackage") -> Tuple[str, ModelMetadata]: ...`

Each method returns:
- A draft artifact (or artifacts).
- `ModelMetadata` describing which model(s) were involved.

### 2.2 LLMService and SLMService

Optionally, you can split responsibilities:

- `class LLMService:`
  - Focused on:
    - Free-text generation (titles, summaries, RQs, criteria).
    - Complex reasoning tasks (e.g., mapping concepts to question types).

- `class SLMService:`
  - Focused on:
    - Keyword extraction.
    - Similarity search / embedding-based synonym suggestion.
    - Syntax validation for Boolean queries.

Then `ModelService` can orchestrate:

- Call `SLMService` first for raw candidates.
- Pass candidates to `LLMService` for cleaning and structuring.

### 2.3 Configuration and modes

`ModelService` should be configurable, for example via a config object or environment variables:

- `mode: str` – `"offline"`, `"llm-only"`, `"hybrid"`.
- `preferred_llm: Optional[str]` – model name/id.
- `preferred_slm: Optional[str]` – which local pipeline to use.

Stages do not care about these details; they just call the `ModelService` methods.

---

## 3. Implications for stage implementation

When you implement pipeline stages, you can:

- Accept both a `ModelService` instance and a persistence layer (for saving artifacts).
- Use the `ModelService` to obtain **draft** artifacts.
- Present drafts to the user for HITL approval/editing.
- On approval, save artifacts with:
  - `status = APPROVED` (or `APPROVED_WITH_NOTES`).
  - The returned `model_metadata` from `ModelService`.

Example flow for a stage:

1. Load or construct input artifacts from previous stage.
2. Call a `ModelService` method to get a draft artifact.
3. Show the draft to the user (CLI/UI) and allow edits.
4. Set `status` and `user_notes` based on the user’s decision.
5. Persist the approved artifact.

This keeps LLM/SLM usage **transparent**, **replaceable**, and tightly integrated with the HITL checkpoints.

---

## 4. Next steps

- Implement these models as Python `@dataclass`-es or Pydantic models (e.g., in a `models.py` file).
- Implement a first `ModelService` stub that:
  - Uses simple heuristics/placeholder logic instead of real LLM/SLM calls (for early testing).
- Once stable, introduce actual LLM and SLM backends and wire them into `ModelService`.

This document should evolve alongside the code to keep the mental model of developers and the actual implementation aligned.
