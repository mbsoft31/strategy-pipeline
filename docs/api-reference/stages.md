# Pipeline Stages

All 8 pipeline stages inherit from `BaseStage` and follow a consistent pattern for execution, validation, and artifact generation.

## BaseStage

Base class for all pipeline stages. Provides common functionality for artifact persistence and validation.

::: src.stages.base.BaseStage
    options:
      show_source: true
      heading_level: 3
      show_signature_annotations: true
      members:
        - execute
        - validate_inputs

---

## Stage 0: Project Setup

Initialize a new project by creating the initial `ProjectContext` artifact.

::: src.stages.project_setup.ProjectSetupStage
    options:
      show_source: true
      heading_level: 3
      show_signature_annotations: true
      members:
        - execute

---

## Stage 1: Problem Framing

Extract PICO elements and define research scope from the raw research question.

::: src.stages.problem_framing.ProblemFramingStage
    options:
      show_source: true
      heading_level: 3
      show_signature_annotations: true
      members:
        - execute

---

## Stage 2: Research Questions

Generate structured research questions from the problem framing.

::: src.stages.research_questions.ResearchQuestionStage
    options:
      show_source: true
      heading_level: 3
      show_signature_annotations: true
      members:
        - execute

---

## Stage 3: Concept Expansion

Expand keywords using MeSH terms and synonyms to build comprehensive search concept blocks.

::: src.stages.search_concept_expansion.SearchConceptExpansionStage
    options:
      show_source: true
      heading_level: 3
      show_signature_annotations: true
      members:
        - execute

---

## Stage 4: Database Query Plan

Generate validated boolean queries for multiple academic databases with anti-hallucination engine.

::: src.stages.database_query_plan.DatabaseQueryPlanStage
    options:
      show_source: true
      heading_level: 3
      show_signature_annotations: true
      members:
        - execute

---

## Stage 5: Screening Criteria

Generate PRISMA-aligned inclusion/exclusion criteria using deterministic PICO extraction.

::: src.stages.screening_criteria.ScreeningCriteriaStage
    options:
      show_source: true
      heading_level: 3
      show_signature_annotations: true
      members:
        - execute

---

## Stage 7: Query Execution

Execute database searches, retrieve papers, and perform auto-deduplication.

::: src.stages.query_execution.QueryExecutionStage
    options:
      show_source: true
      heading_level: 3
      show_signature_annotations: true
      members:
        - execute

---

## Stage 6: Strategy Export

Export papers and protocol in multiple formats (CSV, BibTeX, RIS, PRISMA Markdown).

::: src.stages.strategy_export.StrategyExportStage
    options:
      show_source: true
      heading_level: 3
      show_signature_annotations: true
      members:
        - execute

---

## StageResult

Result object returned by all stage executions.

::: src.stages.base.StageResult
    options:
      show_source: false
      heading_level: 3
      show_signature_annotations: true

