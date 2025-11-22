# API Specification for Strategy Pipeline

**Version:** 1.0  
**Base URL:** `http://localhost:5000/api` (development)  
**Format:** JSON  
**Authentication:** None (MVP single-user mode)

---

## 📋 Table of Contents

1. [Projects](#projects)
2. [Stages](#stages)
3. [Artifacts](#artifacts)
4. [Error Handling](#error-handling)

---

## 🗂 Projects

### List All Projects

**GET** `/api/projects`

**Response 200:**
```json
{
  "projects": [
    {
      "id": "project_abc123",
      "title": "Retrieval Augmentation Study",
      "current_stage": 4,
      "total_stages": 7,
      "status": "in_progress",
      "created_at": "2025-11-20T14:00:00Z",
      "updated_at": "2025-11-22T10:30:00Z"
    }
  ]
}
```

---

### Create New Project

**POST** `/api/projects`

**Request Body:**
```json
{
  "raw_idea": "Investigate techniques for reducing LLM hallucinations",
  "title": "LLM Hallucination Mitigation" // optional
}
```

**Response 201:**
```json
{
  "project_id": "project_xyz789",
  "title": "LLM Hallucination Mitigation",
  "stage_result": {
    "stage_name": "project-setup",
    "draft_artifact": { /* ProjectContext object */ },
    "metadata": { /* generation metadata */ },
    "prompts": ["Review the generated context..."],
    "validation_errors": []
  }
}
```

**Response 400 (Validation Error):**
```json
{
  "error": "Research idea must be at least 20 characters",
  "code": "VALIDATION_ERROR"
}
```

---

### Get Project Details

**GET** `/api/projects/:projectId`

**Response 200:**
```json
{
  "project": {
    "id": "project_abc123",
    "title": "Retrieval Augmentation Study",
    "current_stage": 4,
    "total_stages": 7,
    "status": "in_progress",
    "created_at": "2025-11-20T14:00:00Z",
    "updated_at": "2025-11-22T10:30:00Z",
    "artifacts": {
      "ProjectContext": "APPROVED",
      "ProblemFraming": "APPROVED",
      "ResearchQuestionSet": "APPROVED",
      "SearchConceptBlocks": "APPROVED",
      "DatabaseQueryPlan": "DRAFT"
    }
  }
}
```

**Response 404:**
```json
{
  "error": "Project not found",
  "code": "NOT_FOUND"
}
```

---

## 🎯 Stages

### Execute Stage

**POST** `/api/projects/:projectId/stages/:stageName`

**Stage Names:**
- `project-setup`
- `problem-framing`
- `research-questions`
- `search-concept-expansion`
- `database-query-plan`
- `screening-criteria`
- `strategy-export`

**Request Body (Optional Inputs):**
```json
{
  "inputs": {
    "target_databases": ["pubmed", "scopus"], // for database-query-plan
    "estimate_hits": false,
    "refine_with_queries": true // for screening-criteria
  }
}
```

**Response 200:**
```json
{
  "stage_name": "problem-framing",
  "draft_artifact": {
    "project_id": "project_abc123",
    "problem_statement": "...",
    "goals": ["Goal 1", "Goal 2"],
    "scope_in": [...],
    "scope_out": [...],
    "stakeholders": [...],
    "research_gap": "...",
    "status": "DRAFT",
    "created_at": "2025-11-22T12:00:00Z",
    "updated_at": "2025-11-22T12:00:00Z"
  },
  "metadata": {
    "model_name": "gpt-4o-mini",
    "mode": "llm",
    "generated_at": "2025-11-22T12:00:00Z"
  },
  "prompts": [
    "Review the problem statement for clarity",
    "Ensure goals are specific and measurable"
  ],
  "validation_errors": []
}
```

**Response 400 (Preconditions Not Met):**
```json
{
  "error": "Cannot execute stage: ProjectContext not approved",
  "code": "PRECONDITION_FAILED",
  "required_artifacts": ["ProjectContext"]
}
```

**Response 400 (Validation Error):**
```json
{
  "stage_name": "database-query-plan",
  "draft_artifact": null,
  "validation_errors": [
    "SearchConceptBlocks is empty - no concept blocks defined.",
    "Please review Stage 3 output and ensure at least one concept block exists."
  ]
}
```

---

### Get Available Stages

**GET** `/api/projects/:projectId/available-stages`

**Response 200:**
```json
{
  "available_stages": ["database-query-plan"]
}
```

---

## 📦 Artifacts

### Get Artifact

**GET** `/api/projects/:projectId/artifacts/:artifactType`

**Artifact Types:**
- `ProjectContext`
- `ProblemFraming`
- `ConceptModel`
- `ResearchQuestionSet`
- `SearchConceptBlocks`
- `DatabaseQueryPlan`
- `ScreeningCriteria`
- `StrategyExportBundle`

**Response 200:**
```json
{
  "artifact": {
    "project_id": "project_abc123",
    "problem_statement": "Investigate retrieval augmentation techniques...",
    "goals": ["Reduce hallucinations by 30%", "Maintain latency <500ms"],
    "scope_in": ["Retrieval-augmented generation", "Fact-checking"],
    "scope_out": ["Fine-tuning approaches"],
    "stakeholders": ["Researchers", "ML Engineers"],
    "research_gap": "Current approaches lack systematic evaluation...",
    "status": "APPROVED",
    "created_at": "2025-11-21T10:00:00Z",
    "updated_at": "2025-11-21T11:30:00Z",
    "model_metadata": {
      "model_name": "gpt-4o-mini",
      "mode": "llm",
      "generated_at": "2025-11-21T10:00:00Z"
    },
    "user_notes": "Added temporal constraint to scope"
  }
}
```

**Response 404:**
```json
{
  "error": "Artifact not found",
  "code": "NOT_FOUND"
}
```

---

### Update/Approve Artifact

**PUT** `/api/projects/:projectId/artifacts/:artifactType`

**Request Body:**
```json
{
  "edits": {
    "problem_statement": "Updated problem statement...",
    "goals": ["New goal 1", "New goal 2"],
    "scope_in": [...]
  },
  "approval_status": "APPROVED", // or "APPROVED_WITH_NOTES", "REQUIRES_REVISION"
  "user_notes": "Refined goals based on stakeholder feedback"
}
```

**Response 200:**
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

**Response 400 (Validation Error):**
```json
{
  "error": "Invalid field: 'goals' cannot be empty",
  "code": "VALIDATION_ERROR"
}
```

---

## ❌ Error Handling

### Error Response Format

All error responses follow this structure:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "specific_field",
    "constraint": "validation rule that failed"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Stage executed successfully |
| 201 | Created | Project created |
| 400 | Bad Request | Validation error, missing required field |
| 404 | Not Found | Project or artifact not found |
| 500 | Server Error | Unexpected backend error |
| 503 | Service Unavailable | LLM provider timeout |

### Common Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `NOT_FOUND` | Resource not found |
| `PRECONDITION_FAILED` | Prerequisites not met (e.g., prior stage not approved) |
| `LLM_ERROR` | LLM provider error |
| `TIMEOUT` | Request timeout |
| `INTERNAL_ERROR` | Unexpected server error |

---

## 🔒 Authentication (Future)

MVP does not require authentication. Future versions will use:

**Headers:**
```
Authorization: Bearer <token>
```

**Login Endpoint (Planned):**
```
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "..."
}
```

---

## 📊 Rate Limiting (Future)

MVP has no rate limiting. Future versions:
- 100 requests per minute per IP
- 429 status code when exceeded
- `Retry-After` header with wait time in seconds

---

## 🔄 Polling vs WebSockets (Future)

**Current (MVP):** Client polls for stage execution status every 2-5 seconds.

**Future Enhancement:** Server-Sent Events (SSE) or WebSockets for real-time updates:
```
GET /api/projects/:projectId/stream
```

---

## 📝 Example Frontend Fetch Calls

### Create Project

```javascript
const createProject = async (rawIdea, title) => {
  const response = await fetch('/api/projects', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_idea: rawIdea, title })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error);
  }
  
  return response.json();
};
```

### Execute Stage

```javascript
const executeStage = async (projectId, stageName, inputs = {}) => {
  const response = await fetch(`/api/projects/${projectId}/stages/${stageName}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ inputs })
  });
  
  return response.json();
};
```

### Approve Artifact

```javascript
const approveArtifact = async (projectId, artifactType, edits, userNotes) => {
  const response = await fetch(`/api/projects/${projectId}/artifacts/${artifactType}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      edits,
      approval_status: 'APPROVED',
      user_notes: userNotes
    })
  });
  
  return response.json();
};
```

---

**Note:** This API specification is based on the current backend implementation. Refer to backend source code (`src/controller.py`, `interfaces/web_app.py`) for authoritative implementation details.

