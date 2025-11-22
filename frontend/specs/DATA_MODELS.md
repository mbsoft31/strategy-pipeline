# Data Models & JSON Schemas

**Purpose:** Document the structure of all artifacts and API responses for frontend integration.

---

## 📦 Core Artifact Schemas

### ProjectContext

**Artifact Type:** `ProjectContext`  
**Stage:** 0 (Project Setup)

```json
{
  "id": "project_abc123",
  "title": "Retrieval Augmentation for LLM Hallucination Mitigation",
  "short_description": "Systematic investigation of retrieval-augmented generation techniques to reduce factual errors in large language models",
  "discipline": "Computer Science",
  "subfield": "Natural Language Processing",
  "application_area": "Healthcare AI",
  "constraints": {
    "budget": "$10,000",
    "timeline": "3 months",
    "team_size": "2-3 researchers"
  },
  "initial_keywords": [
    "large language models",
    "hallucination",
    "retrieval augmentation",
    "fact-checking"
  ],
  "created_at": "2025-11-20T14:00:00Z",
  "updated_at": "2025-11-20T14:30:00Z",
  "status": "APPROVED",
  "model_metadata": {
    "model_name": "gpt-4o-mini",
    "mode": "llm",
    "prompt_version": null,
    "generated_at": "2025-11-20T14:00:00Z",
    "notes": null
  },
  "user_notes": "Refined scope to focus on healthcare domain"
}
```

**Field Types:**
- `id`: string (unique project identifier)
- `title`: string (max 200 chars)
- `short_description`: string (max 1000 chars)
- `discipline`, `subfield`, `application_area`: string | null
- `constraints`: object (key-value pairs, all strings)
- `initial_keywords`: array of strings
- `status`: enum ("DRAFT" | "APPROVED" | "APPROVED_WITH_NOTES" | "REQUIRES_REVISION")
- `created_at`, `updated_at`: ISO 8601 datetime string
- `model_metadata`: object (see ModelMetadata schema)
- `user_notes`: string | null

---

### ProblemFraming

**Artifact Type:** `ProblemFraming`  
**Stage:** 1 (Problem Framing)

```json
{
  "project_id": "project_abc123",
  "problem_statement": "Current large language models exhibit a 15-30% hallucination rate in medical question-answering tasks, leading to potentially dangerous misinformation. Retrieval-augmented generation has shown promise but lacks systematic evaluation frameworks.",
  "goals": [
    "Reduce factual hallucination rate to <5% in medical QA",
    "Maintain response latency under 500ms",
    "Achieve 95% user trust score in blind studies"
  ],
  "scope_in": [
    "Retrieval-augmented generation techniques",
    "Fact-checking and verification mechanisms",
    "Medical and healthcare domain applications",
    "English language medical texts"
  ],
  "scope_out": [
    "Model fine-tuning approaches",
    "Non-medical domains",
    "Languages other than English",
    "Real-time streaming applications"
  ],
  "stakeholders": [
    "Medical researchers",
    "Healthcare IT specialists",
    "ML engineers",
    "Patient advocacy groups"
  ],
  "research_gap": "Existing literature focuses on post-hoc verification rather than integrated retrieval during generation. No standardized benchmarks exist for healthcare-specific hallucination mitigation.",
  "critique_report": "Draft problem statement is well-scoped. Suggested adding temporal dimension (recent 5 years of research). Goals are SMART-compliant. Consider quantifying 'user trust' metric more precisely.",
  "created_at": "2025-11-20T15:00:00Z",
  "updated_at": "2025-11-20T15:30:00Z",
  "status": "APPROVED",
  "model_metadata": { /* ... */ },
  "user_notes": "Added user trust goal based on stakeholder feedback"
}
```

**Field Types:**
- `project_id`: string
- `problem_statement`: string (rich text, supports markdown)
- `goals`: array of strings
- `scope_in`, `scope_out`: arrays of strings
- `stakeholders`: array of strings
- `research_gap`: string | null
- `critique_report`: string | null (AI-generated validation feedback)
- Rest: same as ProjectContext

---

### ConceptModel

**Artifact Type:** `ConceptModel`  
**Stage:** 1 (Problem Framing, generated alongside ProblemFraming)

```json
{
  "project_id": "project_abc123",
  "concepts": [
    {
      "id": "concept_1",
      "label": "Large Language Models",
      "description": "Neural network models with billions of parameters trained on vast text corpora",
      "type": "intervention"
    },
    {
      "id": "concept_2",
      "label": "Hallucination",
      "description": "Generating factually incorrect or unverifiable information",
      "type": "outcome"
    },
    {
      "id": "concept_3",
      "label": "Retrieval Augmentation",
      "description": "Augmenting generation with retrieved factual documents",
      "type": "method"
    },
    {
      "id": "concept_4",
      "label": "Healthcare Domain",
      "description": "Medical and clinical question-answering contexts",
      "type": "population"
    }
  ],
  "relations": [
    {
      "id": "rel_1",
      "source_id": "concept_3",
      "target_id": "concept_2",
      "relation_type": "mitigates",
      "description": "Retrieval augmentation reduces hallucination risk"
    },
    {
      "id": "rel_2",
      "source_id": "concept_1",
      "target_id": "concept_2",
      "relation_type": "exhibits",
      "description": "LLMs exhibit hallucination behavior"
    }
  ],
  "created_at": "2025-11-20T15:00:00Z",
  "updated_at": "2025-11-20T15:30:00Z",
  "status": "APPROVED",
  "model_metadata": { /* ... */ },
  "user_notes": null
}
```

**Field Types:**
- `concepts`: array of Concept objects
  - `id`: string (unique within project)
  - `label`: string
  - `description`: string
  - `type`: string (e.g., "population", "intervention", "outcome", "method", "context")
- `relations`: array of Relation objects
  - `id`: string
  - `source_id`, `target_id`: string (references concept IDs)
  - `relation_type`: string (e.g., "mitigates", "exhibits", "influences")
  - `description`: string | null

---

### ResearchQuestionSet

**Artifact Type:** `ResearchQuestionSet`  
**Stage:** 2 (Research Questions)

```json
{
  "project_id": "project_abc123",
  "questions": [
    {
      "id": "rq_1",
      "text": "What retrieval strategies are most effective at reducing factual hallucinations in medical question-answering tasks?",
      "type": "evaluative",
      "linked_concept_ids": ["concept_3", "concept_2", "concept_4"],
      "priority": "must_have",
      "methodological_lens": "Comparative analysis"
    },
    {
      "id": "rq_2",
      "text": "How does retrieval timing (pre-generation vs. post-generation) impact hallucination rates?",
      "type": "descriptive",
      "linked_concept_ids": ["concept_3", "concept_2"],
      "priority": "must_have",
      "methodological_lens": "Experimental design"
    },
    {
      "id": "rq_3",
      "text": "What are the latency trade-offs when implementing retrieval augmentation in production systems?",
      "type": "design",
      "linked_concept_ids": ["concept_3"],
      "priority": "nice_to_have",
      "methodological_lens": "Performance benchmarking"
    }
  ],
  "created_at": "2025-11-21T10:00:00Z",
  "updated_at": "2025-11-21T10:30:00Z",
  "status": "APPROVED",
  "model_metadata": { /* ... */ },
  "user_notes": "Added latency question to address stakeholder concerns"
}
```

**Field Types:**
- `questions`: array of ResearchQuestion objects
  - `id`: string
  - `text`: string (the research question)
  - `type`: string ("descriptive" | "explanatory" | "evaluative" | "design" | "predictive")
  - `linked_concept_ids`: array of strings (references ConceptModel)
  - `priority`: string ("must_have" | "nice_to_have")
  - `methodological_lens`: string | null

---

### SearchConceptBlocks

**Artifact Type:** `SearchConceptBlocks`  
**Stage:** 3 (Search Concept Expansion)

```json
{
  "project_id": "project_abc123",
  "blocks": [
    {
      "id": "block_1",
      "label": "Large Language Models",
      "description": "Core AI models for text generation",
      "terms_included": [
        "large language model",
        "LLM",
        "GPT",
        "transformer model",
        "generative AI",
        "large-scale language model"
      ],
      "terms_excluded": [
        "small language model",
        "rule-based system"
      ]
    },
    {
      "id": "block_2",
      "label": "Hallucination",
      "description": "Factual errors and inaccuracies",
      "terms_included": [
        "hallucination",
        "factual error",
        "misinformation",
        "confabulation",
        "unfaithful generation"
      ],
      "terms_excluded": []
    },
    {
      "id": "block_3",
      "label": "Retrieval Augmentation",
      "description": "Document retrieval strategies",
      "terms_included": [
        "retrieval augmentation",
        "retrieval-augmented generation",
        "RAG",
        "document retrieval",
        "fact-checking mechanism"
      ],
      "terms_excluded": [
        "web search"
      ]
    }
  ],
  "created_at": "2025-11-21T14:00:00Z",
  "updated_at": "2025-11-21T14:30:00Z",
  "status": "APPROVED",
  "model_metadata": { /* ... */ },
  "user_notes": "Added 'confabulation' as synonym based on librarian feedback"
}
```

**Field Types:**
- `blocks`: array of SearchConceptBlock objects
  - `id`: string
  - `label`: string (concept name)
  - `description`: string | null
  - `terms_included`: array of strings (search terms)
  - `terms_excluded`: array of strings (NOT terms)

---

### DatabaseQueryPlan

**Artifact Type:** `DatabaseQueryPlan`  
**Stage:** 4 (Database Query Plan)

```json
{
  "project_id": "project_abc123",
  "queries": [
    {
      "id": "query_1",
      "database_name": "pubmed",
      "query_blocks": ["block_1", "block_2", "block_3"],
      "boolean_query_string": "(\"large language model\"[tiab] OR \"LLM\"[tiab] OR \"GPT\"[tiab] OR \"transformer model\"[tiab]) AND (\"hallucination\"[tiab] OR \"factual error\"[tiab] OR \"misinformation\"[tiab]) AND (\"retrieval augmentation\"[tiab] OR \"RAG\"[tiab]) NOT (\"rule-based system\"[tiab])",
      "notes": "Consider adding MeSH terms: Artificial Intelligence, Neural Networks",
      "hit_count_estimate": null,
      "complexity_analysis": {
        "complexity_level": "balanced",
        "total_terms": 18,
        "num_blocks": 3,
        "expected_results": "100-1,000",
        "guidance": "Well-balanced query - recommended complexity for systematic reviews.",
        "warnings": []
      }
    },
    {
      "id": "query_2",
      "database_name": "scopus",
      "query_blocks": ["block_1", "block_2", "block_3"],
      "boolean_query_string": "TITLE-ABS-KEY((\"large language model\" OR \"LLM\" OR \"GPT\" OR \"transformer model\") AND (\"hallucination\" OR \"factual error\" OR \"misinformation\") AND (\"retrieval augmentation\" OR \"RAG\")) AND NOT TITLE-ABS-KEY(\"rule-based system\")",
      "notes": null,
      "hit_count_estimate": null,
      "complexity_analysis": { /* ... */ }
    }
  ],
  "created_at": "2025-11-21T16:00:00Z",
  "updated_at": "2025-11-21T16:15:00Z",
  "status": "DRAFT",
  "model_metadata": { /* ... */ },
  "user_notes": null
}
```

**Field Types:**
- `queries`: array of DatabaseQuery objects
  - `id`: string
  - `database_name`: string ("pubmed" | "scopus" | "arxiv" | "openalex" | "wos" | "semantic_scholar" | "crossref")
  - `query_blocks`: array of strings (references SearchConceptBlock IDs)
  - `boolean_query_string`: string (database-specific Boolean query)
  - `notes`: string | null
  - `hit_count_estimate`: number | null
  - `complexity_analysis`: object
    - `complexity_level`: string ("very_broad" | "broad" | "balanced" | "narrow" | "very_narrow")
    - `total_terms`: number
    - `num_blocks`: number
    - `expected_results`: string (e.g., "100-1,000")
    - `guidance`: string (human-readable advice)
    - `warnings`: array of strings

---

### ScreeningCriteria

**Artifact Type:** `ScreeningCriteria`  
**Stage:** 5 (Screening Criteria)

```json
{
  "project_id": "project_abc123",
  "inclusion_criteria": [
    "Studies addressing retrieval augmentation techniques for LLMs",
    "Population includes: Healthcare Domain, Medical QA Systems",
    "Addresses at least one primary research question (n=3)",
    "Peer-reviewed publications from 2020-2025",
    "English language publications"
  ],
  "exclusion_criteria": [
    "Non-scholarly sources (blogs, forums, unrefereed opinions)",
    "Studies lacking full text access",
    "Irrelevant application domains outside healthcare",
    "Case studies with n<10 participants",
    "Exclude overly general surveys unless directly addressing retrieval-augmentation relationship"
  ],
  "created_at": "2025-11-21T18:00:00Z",
  "updated_at": "2025-11-21T18:15:00Z",
  "status": "DRAFT",
  "model_metadata": { /* ... */ },
  "user_notes": null
}
```

**Field Types:**
- `inclusion_criteria`: array of strings
- `exclusion_criteria`: array of strings

---

### StrategyExportBundle

**Artifact Type:** `StrategyExportBundle`  
**Stage:** 6 (Strategy Export)

```json
{
  "project_id": "project_abc123",
  "exported_files": [
    "ProjectContext.json",
    "ProblemFraming.json",
    "ConceptModel.json",
    "ResearchQuestionSet.json",
    "SearchConceptBlocks.json",
    "DatabaseQueryPlan.json",
    "ScreeningCriteria.json",
    "export/STRATEGY_SUMMARY.md"
  ],
  "notes": "Complete strategy bundle ready for protocol submission",
  "created_at": "2025-11-22T10:00:00Z",
  "updated_at": "2025-11-22T10:00:00Z",
  "status": "APPROVED",
  "model_metadata": { /* ... */ },
  "user_notes": null
}
```

**Field Types:**
- `exported_files`: array of strings (relative paths under data/<project_id>/)
- `notes`: string | null

---

## 🧬 Common Nested Schemas

### ModelMetadata

```json
{
  "model_name": "gpt-4o-mini",
  "mode": "llm",
  "prompt_version": "v1.2",
  "generated_at": "2025-11-20T14:00:00Z",
  "notes": "Used critique loop with 2 iterations"
}
```

**Fields:**
- `model_name`: string (e.g., "gpt-4o-mini", "mock", "heuristic")
- `mode`: string ("llm" | "slm" | "hybrid" | "deterministic" | "mock")
- `prompt_version`: string | null
- `generated_at`: ISO 8601 datetime string
- `notes`: string | null

---

## 📊 API Response Schemas

### StageResult

Returned when executing a stage:

```json
{
  "stage_name": "problem-framing",
  "draft_artifact": { /* ProblemFraming object */ },
  "metadata": { /* ModelMetadata object */ },
  "prompts": [
    "Review the problem statement for clarity",
    "Ensure goals are SMART-compliant"
  ],
  "validation_errors": [],
  "extra_data": {
    "ConceptModel": { /* ConceptModel object */ }
  }
}
```

**Fields:**
- `stage_name`: string (hyphenated stage identifier)
- `draft_artifact`: object | null (artifact matching stage output)
- `metadata`: ModelMetadata object
- `prompts`: array of strings (user guidance)
- `validation_errors`: array of strings (empty if valid)
- `extra_data`: object (optional additional artifacts)

---

## 🔄 Status Enum Values

```typescript
enum ApprovalStatus {
  DRAFT = "DRAFT",
  UNDER_REVIEW = "UNDER_REVIEW",
  APPROVED = "APPROVED",
  APPROVED_WITH_NOTES = "APPROVED_WITH_NOTES",
  REQUIRES_REVISION = "REQUIRES_REVISION"
}
```

---

## 🧪 TypeScript Type Definitions (Optional Reference)

```typescript
// Example TypeScript interfaces for frontend use

interface ProjectContext {
  id: string;
  title: string;
  short_description: string;
  discipline?: string;
  subfield?: string;
  application_area?: string;
  constraints: Record<string, string>;
  initial_keywords: string[];
  created_at: string;
  updated_at: string;
  status: ApprovalStatus;
  model_metadata?: ModelMetadata;
  user_notes?: string;
}

interface DatabaseQuery {
  id: string;
  database_name: string;
  query_blocks: string[];
  boolean_query_string: string;
  notes?: string;
  hit_count_estimate?: number;
  complexity_analysis?: {
    complexity_level: string;
    total_terms: number;
    num_blocks: number;
    expected_results: string;
    guidance: string;
    warnings: string[];
  };
}

// ... (add more as needed)
```

---

**Note:** All datetime fields use ISO 8601 format (UTC). Frontend should parse and display in user's local timezone.

