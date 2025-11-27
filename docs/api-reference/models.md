# Data Models

All pipeline artifacts use dataclasses with type hints for clear contracts between stages.

## Core Artifact Models

### ProjectContext

Initial project metadata created by Stage 0.

::: src.models.ProjectContext
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true
      members: true

---

### ProblemFraming

PICO elements and research scope from Stage 1.

::: src.models.ProblemFraming
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true
      members: true

---

### ConceptModel

Extracted concepts with types (population, intervention, outcome, etc.) from Stage 1.

::: src.models.ConceptModel
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true
      members: true

---

### ResearchQuestionSet

Generated research questions from Stage 2.

::: src.models.ResearchQuestionSet
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true
      members: true

---

### SearchConceptBlocks

Keyword blocks for query generation from Stage 3.

::: src.models.SearchConceptBlocks
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true
      members: true

---

### DatabaseQueryPlan

Validated boolean queries for multiple databases from Stage 4.

::: src.models.DatabaseQueryPlan
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true
      members: true

---

### ScreeningCriteria

PRISMA-aligned inclusion/exclusion criteria from Stage 5.

::: src.models.ScreeningCriteria
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true
      members: true

---

### SearchResults

Metadata for executed searches from Stage 7. Points to paper JSON files.

**Note:** This artifact contains only metadata, not the papers themselves. Papers are stored in separate JSON files to avoid artifact bloat.

::: src.models.SearchResults
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true
      members: true

---

### StrategyExportBundle

Export metadata from Stage 6.

::: src.models.StrategyExportBundle
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true
      members: true

---

## Supporting Models

### Concept

Individual PICO concept with type and description.

::: src.models.Concept
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true

---

### ResearchQuestion

Single research question with priority and rationale.

::: src.models.ResearchQuestion
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true

---

### SearchConceptBlock

Block of related search terms.

::: src.models.SearchConceptBlock
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true

---

### DatabaseQuery

Single database query with validation metadata.

::: src.models.DatabaseQuery
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true

---

### ModelMetadata

Metadata about LLM generation (model used, timestamp, etc.).

::: src.models.ModelMetadata
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true

---

## Enums

### ApprovalStatus

Artifact approval states.

::: src.models.ApprovalStatus
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true
      members:
        - DRAFT
        - APPROVED
        - REJECTED

---

## Base Classes

### BaseArtifact

Base class for all pipeline artifacts.

::: src.models.BaseArtifact
    options:
      show_source: false
      heading_level: 4
      show_signature_annotations: true

