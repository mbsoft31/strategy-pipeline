# HITL Research-Strategy Pipeline Design

This document captures the initial design for a human-in-the-loop (HITL) research-strategy pipeline tool aimed at PhD students, early-career researchers, and research groups.

The pipeline guides users from an initial vague idea to:
- Structured research questions.
- Database-specific Boolean queries for literature searches.
- Inclusion and exclusion criteria for screening scholarly works.

The design emphasizes modular stages, explicit HITL checkpoints, and artifacts that can be persisted and shared.

---

## 1. End-to-end pipeline stages

High-level stages:

0. Project setup & context capture
1. Problem framing & concept decomposition
2. Research question structuring
3. Database-aware search strategy design
4. Screening criteria (inclusion/exclusion) design
5. Strategy package & export

Each stage:
- Takes in one or more **artifacts** from previous stages plus new user input.
- Produces updated, more structured artifacts.
- Ends with a **HITL checkpoint** where the user reviews, edits, and approves.

---

## 2. Stage definitions

### Stage 0 – Project setup & context capture

**Goal:** Capture high-level project context and user constraints.

**Inputs:**
- Free-text description of the research idea/problem.
- Optional: discipline, time horizon, target venues, known keywords.
- Optional: project metadata (project title, supervisor, group, etc.).

**Processing (conceptual):**
- Normalize and store metadata.
- Optionally run light NLP/LLM to extract:
  - Domain/discipline candidates.
  - Application areas.
  - Stakeholders and goals.

**Outputs / artifacts:**
- `ProjectContext` (conceptual model):
  - `id`, `title`, `short_description`
  - `discipline`, `subfield`, `application_area`
  - `constraints` (timeline, methods preference, etc.)
  - `initial_keywords` (plain text list)
- A short "project brief" summarizing the above.

**HITL checkpoint:**
- User reviews the generated `ProjectContext` and project brief.
- User edits fields (title, description, discipline, keywords, constraints).
- On approval, `ProjectContext` becomes the root context for downstream stages.

---

### Stage 1 – Problem framing & concept decomposition

**Goal:** Turn a vague idea into a structured problem framing and concept model.

**Inputs:**
- `ProjectContext`.
- User’s raw idea text (if not already captured).
- Optional: seed papers or links.

**Processing (conceptual):**
- Extract and structure:
  - Drivers/motivations (why the problem matters).
  - High-level problem statement.
  - Key entities (variables, populations, contexts).
  - Assumptions and constraints.
- Optionally build a simple concept model:
  - Concepts (constructs, populations, methods, outcomes).
  - Relations (e.g., influences, associations, comparisons).

**Outputs / artifacts:**
- `ProblemFraming`:
  - `problem_statement` (1–3 sentences).
  - `goals` (e.g., understand, compare, evaluate, design).
  - `scope` (in-scope vs out-of-scope aspects).
  - `stakeholders`.
- `ConceptModel`:
  - `concepts`: id, label, description, type.
  - `relations`: (source_id, target_id, relation_type, description).

**HITL checkpoint:**
- User edits problem statement, scope, and goals.
- User adds/removes concepts and relations.
- User confirms whether the problem is framed at the right level (too broad/too narrow).
- On approval, `ProblemFraming` and `ConceptModel` are used by the next stage.

---

### Stage 2 – Research question structuring

**Goal:** Translate the framed problem into explicit, structured research questions.

**Inputs:**
- `ProjectContext`.
- `ProblemFraming`.
- `ConceptModel`.
- Optional: methodological preferences (qualitative/quantitative/mixed).

**Processing (conceptual):**
- Generate candidate research questions using patterns/templates:
  - Descriptive ("What is…?")
  - Explanatory ("How/why…?")
  - Evaluative ("To what extent…?")
  - Design ("How can we design…?")
- Map each question to:
  - Linked concepts (independent/dependent constructs).
  - Population/context.
  - Possible methodological approaches (rough).

**Outputs / artifacts:**
- `ResearchQuestionSet`:
  - `questions`: each with
    - `id`, `text`, `type` (descriptive, explanatory, evaluative, design, etc.)
    - `linked_concepts` (references to `ConceptModel`)
    - `priority` (e.g., must-have, nice-to-have)
    - Optional `methodological_lens`.

**HITL checkpoint:**
- User reviews generated research questions.
- User edits wording, merges/splits questions, and sets priorities.
- User chooses which RQs are "ready for search" versus "parked for later".

---

### Stage 3 – Database-aware search strategy design

**Goal:** Turn research questions into database-specific search strategies.

**Inputs:**
- `ResearchQuestionSet` (approved/prioritized questions).
- `ConceptModel`.
- User-selected databases (e.g., PubMed, Scopus, Web of Science, arXiv, IEEE Xplore, ACM DL).

**Processing (conceptual):**
- For each high-priority research question:
  - Identify core conceptual groups (e.g., population, intervention/technology, outcome, context).
  - Propose synonyms, spelling variants, acronyms, and related terms for each concept.
- For each database:
  - Apply database-specific syntax:
    - Field tags (e.g., `TITLE-ABS-KEY`, `[tiab]`, `MeSH` fields).
    - Proximity operators and wildcards.
    - Phrase handling and parentheses.
  - Build Boolean queries:
    - OR within concept groups.
    - AND across concept groups.
    - NOT for exclusion terms.
    - Apply filters (date range, language, publication type) if specified.

**Outputs / artifacts:**
- `SearchConceptBlocks`:
  - For each conceptual block:
    - `label` (e.g., Population, Intervention, Outcome).
    - `terms_included` (synonyms/variants).
    - `terms_excluded` (off-topic terms to avoid).
- `DatabaseQueryPlan`:
  - Per database:
    - `database_name`.
    - `query_blocks` (structured representation of terms and groups).
    - `boolean_query_string` (ready-to-paste query).
    - `notes` (e.g., field usage, rationale, database-specific quirks).
- `SearchMetadata`:
  - Date, responsible person, databases targeted.

**HITL checkpoint:**
- User reviews concept blocks and query strings.
- User adds/removes terms, adjusts grouping, and flags queries as too broad/narrow.
- User tests queries directly in databases and provides feedback (e.g., hit counts, relevance).
- User approves a set of queries as "ready for pilot search".

---

### Stage 4 – Screening criteria (inclusion/exclusion) design

**Goal:** Define inclusion and exclusion criteria aligned with the research questions and search strategy.

**Inputs:**
- `ResearchQuestionSet`.
- `SearchConceptBlocks`.
- `DatabaseQueryPlan`.
- `ProjectContext` (scope, constraints).

**Processing (conceptual):**
- Propose criteria categories:
  - Population.
  - Intervention/Exposure.
  - Comparator (if relevant).
  - Outcomes.
  - Study design (e.g., RCTs, observational, qualitative, mixed methods).
  - Publication type (journal, conference, preprint, gray literature).
  - Language and time frame.
- For each category, generate draft:
  - Inclusion criteria.
  - Exclusion criteria.
- Optionally derive:
  - Title/abstract screening questions.
  - Full-text screening questions.

**Outputs / artifacts:**
- `ScreeningCriteria`:
  - `inclusion_criteria`: id, text, category.
  - `exclusion_criteria`: id, text, category.
- `ScreeningChecklist` (optional for MVP):
  - Ordered yes/no/uncertain questions for title/abstract.
  - Separate list for full-text screening.

**HITL checkpoint:**
- User reviews and edits criteria language.
- User marks criteria as mandatory vs optional.
- User adds notes/examples per criterion if useful.
- On approval, criteria are versioned (e.g., v1.0) and used downstream.

---

### Stage 5 – Strategy package & export

**Goal:** Bundle all artifacts into a reproducible, shareable strategy package.

**Inputs:**
- All previous artifacts:
  - `ProjectContext`, `ProblemFraming`, `ConceptModel`, `ResearchQuestionSet`,
    `SearchConceptBlocks`, `DatabaseQueryPlan`, `ScreeningCriteria`, etc.

**Processing (conceptual):**
- Assemble a coherent summary:
  - Narrative overview of the research strategy.
  - Structured appendices for queries and criteria.
- Prepare export formats (for MVP):
  - Markdown summary.
  - JSON/YAML files for artifacts.
- Attach metadata:
  - Version, timestamp, tool version, author.

**Outputs / artifacts:**
- `StrategyPackage`:
  - A directory/bundle containing:
    - Context, questions, search plan, screening criteria artifacts.
    - A `strategy_overview.md` (or similar) summary.
- Optional `ChangeLog` to track future revisions.

**HITL checkpoint:**
- User reviews the generated summary and package.
- User approves it as a shareable baseline strategy (e.g., for supervisors, research groups).

---

## 3. HITL patterns and states

Across all stages, the pipeline uses consistent HITL patterns:

- **Checkpoint states:**
  - `APPROVED` – user accepts the stage output.
  - `APPROVED_WITH_NOTES` – user accepts but leaves comments.
  - `REVISE_THIS_STAGE` – user wants edits/regeneration at the same stage.
  - `RESTART_FROM_STAGE_X` – user wants to go back to an earlier stage.

- **Audit logging:**
  - For each stage run, store:
    - Input artifacts.
    - Draft outputs.
    - User edits and final outputs.
    - Checkpoint state and timestamp.

- **Iterative refinement:**
  - Stages can be re-run with updated inputs.
  - Branching strategies (e.g., different scopes or RQ sets) can be supported in future iterations.

---

## 4. MVP vs future extensions (high level)

**MVP focus:**
- Implement Stage 0–5 in a simplified but end-to-end way.
- At least one database-specific query template (e.g., PubMed or a generic database).
- Simple JSON/YAML persistence and a Markdown strategy summary.
- CLI or notebook-based HITL interactions (user reviews/editing via prompts).

**Future extensions (not in MVP, but anticipated):**
- Support for multiple review types (systematic, scoping, rapid reviews).
- Rich concept mapping and visualizations.
- Multi-user collaboration (student/supervisor, research groups).
- Automated database querying (via APIs) and feedback loops.
- Integration with reference managers (Zotero, Mendeley, etc.).
- Advanced analytics for query quality and strategy patterns.

---

This document is intended as a living design reference. As the implementation evolves, we can refine stages, artifacts, and HITL mechanics, and cross-link this file with more detailed architecture and usage docs in the `docs/` folder.
