# Web UI Architecture - Visual Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                               │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Landing Page (/)                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │  │
│  │  │ Project Card │  │ Project Card │  │  New Project │     │  │
│  │  │   Draft ⏳   │  │ Approved ✓   │  │    Button    │     │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              ↓ Click "New Project"                 │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  New Project Form (/project/new)                           │  │
│  │  ┌───────────────────────────────────────────────────────┐ │  │
│  │  │ [Large textarea for research idea...]                 │ │  │
│  │  │  Character count: 0/2000                              │ │  │
│  │  └───────────────────────────────────────────────────────┘ │  │
│  │  [Create Project & Continue]  ← HTMX POST                 │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              ↓ Submit                              │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Project Detail (/project/abc123)                          │  │
│  │  ┌─────────────────────────────────────────────────────┐   │  │
│  │  │  PIPELINE PROGRESS                                   │   │  │
│  │  │  ┌──┐────┌──┐────┌──┐────┌──┐────┌──┐              │   │  │
│  │  │  │✓ │────│⏳│────│○ │────│○ │────│○ │              │   │  │
│  │  │  └──┘    └──┘    └──┘    └──┘    └──┘              │   │  │
│  │  │   0       1       2       3       4                 │   │  │
│  │  │  Setup   Frame  Quest.  Search  Screen              │   │  │
│  │  └─────────────────────────────────────────────────────┘   │  │
│  │  [Start Stage 1] [View Details]                            │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              ↓ Click "Start Stage 1"               │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Stage 1: Problem Framing                                  │  │
│  │  ┌───────────────────────────────────────────────────────┐ │  │
│  │  │ AI Checklist:                                         │ │  │
│  │  │ • Review problem statement                            │ │  │
│  │  │ • Edit goals to align with objectives                 │ │  │
│  │  │ • Adjust scope boundaries                             │ │  │
│  │  └───────────────────────────────────────────────────────┘ │  │
│  │  ┌───────────────────────────────────────────────────────┐ │  │
│  │  │ Problem Statement: [Editable text...]                 │ │  │
│  │  │ Goals:                                                 │ │  │
│  │  │   • Goal 1 [Edit] [Remove]                            │ │  │
│  │  │   • Goal 2 [Edit] [Remove]                            │ │  │
│  │  │   [Add Goal]                                          │ │  │
│  │  └───────────────────────────────────────────────────────┘ │  │
│  │  [Approve & Continue] ← HTMX POST                          │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              ↓ Approve                             │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  ┌─────────────────────────────────────────────────────┐   │  │
│  │  │  ✓ Stage Approved!                                   │   │  │
│  │  │  Redirecting to project...                           │   │  │
│  │  └─────────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                              ↕ HTMX (no page reload)
┌────────────────────────────────────────────────────────────────────┐
│                      FLASK WEB SERVER                               │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Routes (web_app.py)                                         │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │ │
│  │  │   GET /    │  │ POST /new  │  │ GET /proj  │             │ │
│  │  │  Landing   │→ │  Create    │→ │  Detail    │             │ │
│  │  └────────────┘  └────────────┘  └────────────┘             │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │ │
│  │  │ GET /stage │  │POST approve│  │  JSON API  │             │ │
│  │  │   Edit     │→ │  Artifact  │  │   /api/    │             │ │
│  │  └────────────┘  └────────────┘  └────────────┘             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              ↓                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  PipelineController                                          │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │ │
│  │  │start_project│ │ run_stage  │  │  approve   │             │ │
│  │  └────────────┘  └────────────┘  └────────────┘             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              ↓                                     │
│  ┌──────────────────┐         ┌──────────────────┐               │
│  │  ModelService    │         │ PersistenceService│               │
│  │  ┌────────────┐  │         │  ┌────────────┐  │               │
│  │  │SimpleModel │  │         │  │ JSON files │  │               │
│  │  │  Service   │  │         │  │  ./data/   │  │               │
│  │  └────────────┘  │         │  └────────────┘  │               │
│  └──────────────────┘         └──────────────────┘               │
└────────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│                      FILE SYSTEM                                    │
│  ./data/                                                           │
│    ├── project_abc123/                                            │
│    │   ├── ProjectContext.json                                    │
│    │   ├── ProblemFraming.json                                    │
│    │   └── ConceptModel.json                                      │
│    └── project_xyz456/                                            │
│        └── ProjectContext.json                                    │
└────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
1. User enters idea
   ↓
2. Browser → HTMX POST → Flask route
   ↓
3. Flask → PipelineController.start_project()
   ↓
4. Controller → ProjectSetupStage.execute()
   ↓
5. Stage → SimpleModelService.suggest_project_context()
   ↓
6. ModelService → Extract keywords, generate title
   ↓
7. Stage → PersistenceService.save_artifact()
   ↓
8. Persistence → Write JSON to ./data/project_id/
   ↓
9. Stage → Return StageResult
   ↓
10. Flask → Render template with artifact
    ↓
11. Browser ← HTML (no reload, HTMX swap)
    ↓
12. User sees AI-generated context
    ↓
13. User edits & approves
    ↓
14. Cycle repeats for Stage 1, 2, 3...
```

## Component Interactions

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Browser   │ HTMX │    Flask    │ Call │ Controller  │
│             │─────→│             │─────→│             │
│ (Tailwind)  │←─────│  (Jinja2)   │←─────│  (Python)   │
│ (Alpine.js) │ HTML │  Templates  │ Data │   Stages    │
└─────────────┘      └─────────────┘      └─────────────┘
                                                  │
                                                  ↓
                                    ┌─────────────────────────┐
                                    │                         │
                                    ↓                         ↓
                          ┌─────────────┐         ┌─────────────┐
                          │ModelService │         │ Persistence │
                          │             │         │   Service   │
                          │ (AI/LLM)    │         │  (JSON)     │
                          └─────────────┘         └─────────────┘
```

## Technology Stack Layers

```
┌───────────────────────────────────────────────────────────┐
│ Layer 4: Presentation (Browser)                           │
│ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ │
│ │ Tailwind  │ │   HTMX    │ │ Alpine.js │ │   HTML5   │ │
│ │   CSS     │ │  (9KB)    │ │   (3KB)   │ │ Semantic  │ │
│ └───────────┘ └───────────┘ └───────────┘ └───────────┘ │
└───────────────────────────────────────────────────────────┘
                          ↕ HTTP/HTTPS
┌───────────────────────────────────────────────────────────┐
│ Layer 3: Web Framework (Flask)                            │
│ ┌───────────┐ ┌───────────┐ ┌───────────┐               │
│ │  Routes   │ │  Jinja2   │ │ Session   │               │
│ │ /project  │ │ Templates │ │  Mgmt     │               │
│ └───────────┘ └───────────┘ └───────────┘               │
└───────────────────────────────────────────────────────────┘
                          ↕ Function Calls
┌───────────────────────────────────────────────────────────┐
│ Layer 2: Business Logic (Controller)                      │
│ ┌───────────┐ ┌───────────┐ ┌───────────┐               │
│ │ Pipeline  │ │   Stage   │ │ Artifact  │               │
│ │Controller │ │ Registry  │ │ Approval  │               │
│ └───────────┘ └───────────┘ └───────────┘               │
└───────────────────────────────────────────────────────────┘
                          ↕ Service Calls
┌───────────────────────────────────────────────────────────┐
│ Layer 1: Services (Model & Persistence)                   │
│ ┌────────────────────┐ ┌──────────────────────┐          │
│ │  SimpleModelService│ │ FilePersistenceService│          │
│ │  (AI/extraction)   │ │  (JSON read/write)   │          │
│ └────────────────────┘ └──────────────────────┘          │
└───────────────────────────────────────────────────────────┘
                          ↕ File I/O
┌───────────────────────────────────────────────────────────┐
│ Layer 0: Data Storage (File System)                       │
│ ./data/project_id/*.json                                  │
└───────────────────────────────────────────────────────────┘
```

## UX Flow States

```
State 1: LANDING
┌─────────────────┐
│  See Projects   │
│  + New Project  │
└────────┬────────┘
         │
         ↓ Click "New"
         
State 2: CREATING
┌─────────────────┐
│  Enter Idea     │
│  [textarea]     │
│  [Create]       │
└────────┬────────┘
         │
         ↓ Submit
         
State 3: LOADING
┌─────────────────┐
│  ↻ Creating...  │
│  Please wait    │
└────────┬────────┘
         │
         ↓ Complete
         
State 4: REVIEWING
┌─────────────────┐
│  Stage 0        │
│  ┌───────────┐  │
│  │ AI Draft  │  │
│  │ [Edit]    │  │
│  └───────────┘  │
│  [Approve]      │
└────────┬────────┘
         │
         ↓ Approve
         
State 5: PROGRESSING
┌─────────────────┐
│  ✓ Stage 0 Done │
│  → Stage 1 Next │
│  Timeline View  │
└────────┬────────┘
         │
         ↓ Repeat for each stage
```

This visual architecture shows how the web UI creates an optimal user experience through clear separation of concerns and progressive disclosure!

