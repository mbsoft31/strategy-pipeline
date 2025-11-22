# 02 - Stage Execution & Approval Feature Specification

**Feature:** Pipeline Stage Progression UI  
**Priority:** P0 (MVP)  
**Estimated Complexity:** High

---

## 🎯 Purpose

Enable users to execute pipeline stages sequentially, review AI-generated drafts, edit artifacts, and approve them to unlock the next stage. This is the **core workflow** of the application.

---

## 📐 User Interface Requirements

### 1. Project Detail Page Layout

**URL:** `/projects/:projectId`

```
+------------------------------------------------------------------+
| ← Back to Projects        Retrieval Augmentation Study           |
+------------------------------------------------------------------+
| [Stage Timeline: ●━━━━━○━○━○━○━○]                                |
|  0   1   2   3   4   5   6                                       |
| Setup Framing RQs Search Query Criteria Export                   |
+------------------------------------------------------------------+
| Current Stage: Problem Framing (Stage 1)                         |
+------------------------------------------------------------------+
|                                                                  |
| [Left Sidebar]              [Main Content Area]                  |
| • Project Context ✅         [Stage 1 Draft Artifact Display]   |
| • Problem Framing ⏳                                             |
| • Research Questions         Problem Statement:                  |
| • Search Expansion           [Editable Textarea...]             |
| • Query Plan                                                     |
| • Screening Criteria         Goals:                              |
| • Strategy Export            [Editable List...]                  |
|                                                                  |
|                             [Cancel] [Save Draft] [Approve ✓]   |
+------------------------------------------------------------------+
```

**Key Components:**

#### **A. Stage Timeline (Stepper)**
- Visual progress indicator showing all 7 stages
- **Completed stages:** Filled circle (●) with green/blue color
- **Current stage:** Highlighted circle (◉) with pulse animation
- **Locked stages:** Hollow circle (○) with gray color
- **Connecting lines:** Solid for completed, dashed for future
- **Labels:** Stage names below circles (abbreviate on mobile)

#### **B. Left Sidebar (Stage Navigation)**
- List of all stages with status icons:
  - ✅ Approved
  - ⏳ In Progress (draft available)
  - 🔒 Locked (awaiting prior approval)
  - ⚠️ Requires Revision (validation errors)
- Click stage → View that stage's artifact (if accessible)
- Highlight current active stage

#### **C. Main Content Area**
- **Stage Title:** "Stage X: [Name]"
- **Description:** Brief explanation of what this stage does
- **Status Badge:** "Draft", "Approved", "Requires Revision"
- **Artifact Editor:** (See detailed specs below)
- **Action Buttons:** Cancel, Save Draft, Approve

---

### 2. Stage Execution Flow

**Initial State (No Draft):**
```
+------------------------------------------------------------------+
| Stage 1: Problem Framing                              [🔒 Locked] |
+------------------------------------------------------------------+
| Transform your project context into a structured problem         |
| statement with goals, scope, and research gaps.                  |
|                                                                  |
| Prerequisites:                                                   |
| ✅ Project Context (Stage 0) approved                            |
|                                                                  |
|                        [▶ Run Stage 1]                           |
+------------------------------------------------------------------+
```

**Loading State:**
```
+------------------------------------------------------------------+
| Stage 1: Problem Framing                          [⏳ Processing] |
+------------------------------------------------------------------+
| Generating structured problem framing...                         |
|                                                                  |
| [■■■■■■■■■□□□□□□] 60% - Drafting goals                          |
|                                                                  |
| This may take 5-10 seconds.                                      |
+------------------------------------------------------------------+
```

**Draft Ready State:**
```
+------------------------------------------------------------------+
| Stage 1: Problem Framing                              [📝 Draft]  |
+------------------------------------------------------------------+
| Review and edit the generated artifact. Click "Approve" to save  |
| and unlock the next stage.                                       |
|                                                                  |
| [Artifact Editor - See Section 3 below]                          |
|                                                                  |
| AI Suggestions:                                                  |
| • Consider adding stakeholder: "Research participants"           |
| • Refine scope_out to exclude case studies                       |
|                                                                  |
|                  [Cancel] [Save Draft] [Approve ✓]              |
+------------------------------------------------------------------+
```

**Approved State:**
```
+------------------------------------------------------------------+
| Stage 1: Problem Framing                          [✅ Approved]   |
+------------------------------------------------------------------+
| Last approved: 2 hours ago by User                               |
|                                                                  |
| [Read-Only Artifact Display]                                     |
|                                                                  |
| Problem Statement:                                               |
| Investigate retrieval augmentation techniques...                 |
|                                                                  |
| Goals:                                                           |
| • Reduce factual hallucinations by 30%                           |
| • Maintain response latency under 500ms                          |
|                                                                  |
|                         [Edit] [Re-run Stage]                    |
+------------------------------------------------------------------+
```

---

### 3. Artifact Editor (Per Stage)

Each stage has a **custom editor** tailored to its artifact structure. Below are specs for each:

#### **Stage 0: Project Context**

**Fields:**
- **Title** (Text Input) - Editable, max 200 chars
- **Short Description** (Textarea) - Max 500 chars
- **Discipline** (Select/Autocomplete) - E.g., "Computer Science", "Medicine"
- **Subfield** (Text Input) - E.g., "Natural Language Processing"
- **Application Area** (Text Input) - E.g., "Healthcare AI"
- **Initial Keywords** (Tag Input) - Add/remove tags
- **Constraints** (Key-Value Pairs) - E.g., "budget: $10k", "timeline: 3 months"

**Layout:**
```
Title: [_______________________________________]

Description:
[______________________________________________]
[______________________________________________]
[______________________________________________]

Discipline: [Computer Science ▼]
Subfield:   [Natural Language Processing____]
Application: [Healthcare AI__________________]

Keywords: [machine learning] [x] [LLM] [x] [+ Add]

Constraints:
  budget: [$10,000_____] [Remove]
  timeline: [3 months___] [Remove]
  [+ Add Constraint]
```

---

#### **Stage 1: Problem Framing**

**Fields:**
- **Problem Statement** (Rich Textarea) - Markdown supported
- **Goals** (List Editor) - Add/remove/reorder bullets
- **Scope In** (List Editor)
- **Scope Out** (List Editor)
- **Stakeholders** (Tag Input)
- **Research Gap** (Textarea) - Optional

**Layout:**
```
Problem Statement:
[______________________________________________]
[______________________________________________]
(Supports **bold**, *italic*, `code`)

Goals:
  1. [Reduce hallucinations by 30%___] [↑↓] [×]
  2. [Maintain latency under 500ms____] [↑↓] [×]
  [+ Add Goal]

Scope - Include:
  • [Retrieval-augmented generation___] [×]
  • [Fact-checking mechanisms_________] [×]
  [+ Add]

Scope - Exclude:
  • [Fine-tuning approaches___________] [×]
  [+ Add]

Stakeholders:
  [Researchers] [×] [ML Engineers] [×] [+ Add]

Research Gap (Optional):
[Existing work focuses on post-hoc verification...]
```

---

#### **Stage 2: Research Questions**

**Fields:**
- **Questions List** - Each question has:
  - Text (Textarea)
  - Type (Select: descriptive, explanatory, evaluative, design)
  - Priority (Select: must_have, nice_to_have)
  - Linked Concepts (Multi-select from ConceptModel)
  - Methodological Lens (Text Input, optional)

**Layout (Per Question):**
```
┌─ Question 1 ─────────────────────────────── [×Remove]
│
│ Question Text:
│ [What retrieval strategies are most effective...___]
│
│ Type: [Evaluative ▼]  Priority: [Must Have ▼]
│
│ Linked Concepts: [Retrieval] [×] [LLM] [×] [+ Add]
│
│ Methodological Lens: [Comparative analysis___]
│
└──────────────────────────────────────────────

[+ Add Research Question]
```

---

#### **Stage 3: Search Concept Expansion**

**Fields:**
- **Concept Blocks** - Each block has:
  - Label (e.g., "Large Language Models")
  - Description (optional)
  - Terms Included (Tag Input with suggestions)
  - Terms Excluded (Tag Input)

**Layout (Per Block):**
```
┌─ Concept Block: Large Language Models ─────── [×Remove]
│
│ Label: [Large Language Models_________________]
│
│ Description (Optional):
│ [Core AI models for text generation...]
│
│ Included Terms:
│   [Large Language Model] [×] [LLM] [×] [GPT] [×]
│   [Transformer] [×] [+ Add Term]
│
│ Excluded Terms:
│   [Small language model] [×] [+ Add Term]
│
└──────────────────────────────────────────────────

[+ Add Concept Block]
```

**AI Suggestions (Shown in sidebar):**
- "Add synonym: 'generative AI'"
- "Consider excluding: 'rule-based systems'"

---

#### **Stage 4: Database Query Plan**

**Fields:**
- **Queries List** - Each query has:
  - Database Name (Read-only)
  - Boolean Query String (Code Editor with syntax highlighting)
  - Complexity Analysis (Read-only display)
  - Notes (Textarea, optional)

**Layout (Per Query):**
```
┌─ PubMed Query ──────────────────────────────────────────
│
│ Boolean Query:
│ ┌─────────────────────────────────────────────────┐
│ │ ("large language model"[tiab] OR "LLM"[tiab])   │
│ │ AND ("hallucination"[tiab] OR "factual error"[tiab])│
│ │ NOT ("fine tuning"[tiab])                       │
│ └─────────────────────────────────────────────────┘
│
│ Complexity Analysis:
│   Level: Balanced | Expected Results: 100-1,000
│   Guidance: Well-balanced query for systematic review
│
│ Notes (Optional):
│ [Consider adding MeSH terms for broader coverage...]
│
│ [Copy Query] [Preview in Database] [Test Syntax]
│
└────────────────────────────────────────────────────────
```

**Syntax Highlighting:**
- Operators (AND, OR, NOT): Bold, blue
- Field tags ([tiab], [mesh]): Gray, italic
- Terms in quotes: Green
- Parentheses: Yellow

---

#### **Stage 5: Screening Criteria**

**Fields:**
- **Inclusion Criteria** (List Editor)
- **Exclusion Criteria** (List Editor)

**Layout:**
```
Inclusion Criteria:
  1. [Studies addressing retrieval augmentation___] [×]
  2. [Published in peer-reviewed journals________] [×]
  [+ Add Criterion]

Exclusion Criteria:
  1. [Non-English publications___________________] [×]
  2. [Case studies with n<10____________________] [×]
  [+ Add Criterion]

[Validate Against Query Plan] (Shows overlap report)
```

---

#### **Stage 6: Strategy Export**

**Fields:**
- **Export Format Selection** (Checkboxes):
  - ☑ Markdown Summary
  - ☐ PDF Bundle
  - ☐ JSON Artifacts
  - ☐ Citation List
- **Notes** (Textarea, optional)

**Preview:**
```
Exported Files:
  ✓ STRATEGY_SUMMARY.md (12 KB)
  ✓ ProjectContext.json (2 KB)
  ✓ DatabaseQueryPlan.json (8 KB)
  ...

[Download Bundle.zip] [View Summary Preview]
```

---

### 4. Action Buttons

**Button States:**

| Button | Behavior | Enabled When |
|--------|----------|--------------|
| **Run Stage** | Execute current stage | Prerequisites met, no draft exists |
| **Cancel** | Discard changes, revert to last saved draft | Editing |
| **Save Draft** | Save current edits without approving | Form valid |
| **Approve** | Lock artifact and unlock next stage | Form valid |
| **Edit** | Switch from read-only to edit mode | Artifact approved |
| **Re-run Stage** | Discard current artifact and regenerate | Artifact exists |

**Confirmation Dialogs:**
- **Approve:** "Are you sure? This will lock the artifact and move to the next stage."
- **Re-run:** "This will discard the current draft. Continue?"
- **Cancel (with unsaved changes):** "You have unsaved changes. Discard them?"

---

## 🔌 API Integration

### Execute Stage

**Endpoint:** `POST /api/projects/:projectId/stages/:stageName`

**Request Body:**
```json
{
  "inputs": {
    "target_databases": ["pubmed", "scopus"], // Stage 4 example
    "estimate_hits": false
  }
}
```

**Response:**
```json
{
  "stage_name": "database-query-plan",
  "draft_artifact": {
    "project_id": "project_123",
    "queries": [
      {
        "database_name": "pubmed",
        "boolean_query_string": "...",
        "complexity_analysis": {...}
      }
    ],
    "status": "DRAFT"
  },
  "metadata": {
    "model_name": "gpt-4o-mini",
    "generated_at": "2025-11-22T12:00:00Z"
  },
  "prompts": ["Review each database query...", ...],
  "validation_errors": []
}
```

**Frontend Actions:**
- Show loading state during execution
- On success: Display draft in editor
- On error (validation_errors): Show errors inline with fields

---

### Approve Artifact

**Endpoint:** `PUT /api/projects/:projectId/artifacts/:artifactType`

**Request Body:**
```json
{
  "edits": {
    "goals": ["Reduce hallucinations by 40%", ...],
    "scope_in": [...]
  },
  "approval_status": "APPROVED",
  "user_notes": "Added temporal constraint"
}
```

**Response:**
```json
{
  "success": true,
  "artifact": {
    "status": "APPROVED",
    "updated_at": "2025-11-22T12:05:00Z"
  },
  "next_available_stages": ["research-questions"]
}
```

**Frontend Actions:**
- Disable "Approve" button while processing
- On success: Update stage status, unlock next stage, show success toast
- On error: Display error message

---

### Fetch Artifact

**Endpoint:** `GET /api/projects/:projectId/artifacts/:artifactType`

**Response:**
```json
{
  "artifact": {
    "project_id": "project_123",
    "problem_statement": "...",
    "goals": [...],
    "status": "APPROVED",
    "updated_at": "2025-11-22T10:00:00Z"
  }
}
```

---

## 🎨 Design Specifications

### Stage Status Colors

| Status | Color | Icon |
|--------|-------|------|
| Draft | Yellow (`bg-yellow-100`, `text-yellow-800`) | 📝 |
| Approved | Green (`bg-green-100`, `text-green-800`) | ✅ |
| Requires Revision | Red (`bg-red-100`, `text-red-800`) | ⚠️ |
| Locked | Gray (`bg-gray-100`, `text-gray-600`) | 🔒 |
| Processing | Blue (`bg-blue-100`, `text-blue-800`) | ⏳ |

### Loading States

- **Skeleton Loaders:** Show gray placeholder boxes during fetch
- **Progress Bars:** For stage execution (if backend provides progress updates)
- **Spinners:** For button actions (Save Draft, Approve)

### Error States

```
+--------------------------------------------------+
| ⚠️ Error                                         |
+--------------------------------------------------+
| Unable to execute stage: Missing prerequisite    |
| artifact "ProjectContext".                       |
|                                                  |
| [Retry] [Go to Stage 0]                          |
+--------------------------------------------------+
```

### Validation Feedback

- **Inline Errors:** Red text below invalid fields
- **Field Highlighting:** Red border on invalid inputs
- **Summary Box:** List all errors at top of form

---

## ♿ Accessibility Requirements

- **Keyboard Navigation:** Tab through all fields, Enter to submit
- **Screen Reader:** Announce stage status changes ("Stage 1 approved")
- **ARIA Labels:** Descriptive labels for all inputs
- **Focus Management:** Move focus to error summary on validation fail
- **Live Regions:** Announce loading state changes

---

## 🧪 Testing Scenarios

### Unit Tests
- [ ] Stage stepper renders correctly
- [ ] Artifact editor validates input
- [ ] Approve button disabled when form invalid

### Integration Tests
- [ ] Execute stage API call succeeds
- [ ] Approve artifact updates status and unlocks next stage
- [ ] Error handling displays validation errors

### E2E Tests
- [ ] User can complete full pipeline (Stages 0-6)
- [ ] Edits are saved correctly
- [ ] Stage progression logic works

---

## 📝 Implementation Checklist

- [ ] Create `ProjectDetailPage` component
- [ ] Create `StageStepper` component
- [ ] Create `StageNavigation` (sidebar) component
- [ ] Create artifact editor components for each stage
- [ ] Implement `useStageExecution` hook
- [ ] Implement `useArtifactApproval` mutation
- [ ] Add form validation logic
- [ ] Implement optimistic UI updates
- [ ] Add loading/error states
- [ ] Test keyboard navigation
- [ ] Accessibility audit

---

**Next:** Read `03_ARTIFACT_VIEWER.md` for artifact history and diff viewing.

