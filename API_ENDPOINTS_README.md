# JSON API Endpoints - Implementation Complete! ✅

## Overview

The backend now has complete JSON API endpoints for frontend integration. The React frontend can now connect to the Flask backend to create projects, run stages, and manage artifacts.

---

## Quick Start

### 1. Install Dependencies

```bash
# Install flask-cors for CORS support
pip install flask-cors==4.0.0

# Or install all requirements
pip install -r requirements.txt
```

### 2. Start Backend Server

```bash
python interfaces/web_app.py
```

Server runs on: **http://localhost:5000**

### 3. Test API Endpoints

```bash
# Run the test script
python test_api_endpoints.py
```

---

## API Endpoints Implemented

### ✅ Project Management

#### **GET /api/projects**
List all projects with metadata

**Response:**
```json
{
  "projects": [
    {
      "id": "project_abc123",
      "title": "LLM Hallucination Study",
      "status": "draft",
      "created_at": "2025-11-22T10:30:00Z"
    }
  ]
}
```

---

#### **POST /api/projects**
Create new project from raw idea

**Request:**
```json
{
  "raw_idea": "Investigate techniques for reducing LLM hallucinations..."
}
```

**Response:** (201 Created)
```json
{
  "project_id": "project_xyz789",
  "title": "LLM Hallucination Study",
  "stage_result": {
    "stage_name": "project-setup",
    "draft_artifact": { ...ProjectContext data... },
    "prompts": ["Review the generated context..."],
    "validation_errors": []
  }
}
```

---

#### **GET /api/projects/:id**
Get project details with all artifact statuses

**Response:**
```json
{
  "id": "project_xyz789",
  "title": "LLM Hallucination Study",
  "description": "Short description...",
  "status": "draft",
  "created_at": "2025-11-22T10:30:00Z",
  "updated_at": null,
  "current_stage": 0,
  "total_stages": 7,
  "artifacts": {
    "ProjectContext": "draft",
    "ProblemFraming": "approved"
  }
}
```

---

### ✅ Artifact Management

#### **GET /api/projects/:id/artifacts/:type**
Get specific artifact as JSON

**Supported types:**
- `ProjectContext`
- `ProblemFraming`
- `ConceptModel`
- `ResearchQuestionSet`
- `SearchConceptBlocks`
- `DatabaseQueryPlan`

**Response:**
```json
{
  "id": "project_xyz789",
  "title": "LLM Hallucination Study",
  "raw_idea": "Investigate techniques...",
  "background_summary": "...",
  "research_domain": "Computer Science",
  "expected_outcomes": ["Reduce hallucinations by 30%"],
  "status": "draft",
  "created_at": "2025-11-22T10:30:00Z"
}
```

---

### ✅ Stage Execution

#### **POST /api/projects/:id/stages/:name/run**
Execute a pipeline stage

**Supported stages:**
- `project-setup`
- `problem-framing`
- `research-questions`
- `search-concept-expansion`
- `database-query-plan`
- `screening-criteria`
- `strategy-export`

**Request:**
```json
{}  // Optional stage-specific inputs
```

**Response:**
```json
{
  "stage_name": "problem-framing",
  "draft_artifact": { ...ProblemFraming data... },
  "prompts": ["Review the problem statement..."],
  "validation_errors": [],
  "metadata": {
    "model_name": "gpt-4",
    "mode": "llm",
    "generated_at": "2025-11-22T10:35:00Z"
  },
  "extra_artifacts": {
    "concept_model": { ...ConceptModel data... }
  }
}
```

---

#### **POST /api/projects/:id/stages/:name/approve**
Approve stage with optional edits

**Request:**
```json
{
  "edits": {
    "title": "Updated Title",
    "goals": ["New goal 1", "New goal 2"]
  },
  "user_notes": "Approved after review"
}
```

**Response:**
```json
{
  "success": true,
  "artifact": { ...approved artifact data... }
}
```

---

## CORS Configuration

CORS is enabled for frontend development on:
- `http://localhost:3000` (Create React App default)
- `http://localhost:5173` (Vite default)

All `/api/*` routes support cross-origin requests from these origins.

---

## Error Handling

All endpoints return proper HTTP status codes:

- **200 OK** - Successful GET/POST
- **201 Created** - Project created
- **400 Bad Request** - Invalid input
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

Error response format:
```json
{
  "error": "Descriptive error message"
}
```

---

## Testing the API

### Using curl

```bash
# List projects
curl http://localhost:5000/api/projects

# Create project
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"raw_idea": "Your research idea here..."}'

# Get project
curl http://localhost:5000/api/projects/project_abc123

# Get artifact
curl http://localhost:5000/api/projects/project_abc123/artifacts/ProjectContext

# Run stage
curl -X POST http://localhost:5000/api/projects/project_abc123/stages/problem-framing/run \
  -H "Content-Type: application/json" \
  -d '{}'

# Approve stage
curl -X POST http://localhost:5000/api/projects/project_abc123/stages/problem-framing/approve \
  -H "Content-Type: application/json" \
  -d '{"edits": {}, "user_notes": "Looks good"}'
```

### Using the Test Script

```bash
python test_api_endpoints.py
```

This script:
1. Lists existing projects
2. Creates a new project
3. Gets project details
4. Gets ProjectContext artifact
5. Runs problem-framing stage
6. Gets ProblemFraming artifact
7. Approves project-setup stage
8. Approves problem-framing stage
9. Verifies project status

---

## Frontend Integration

### Update API Client

The frontend API client (`frontend/strategy-pipeline-ui/src/lib/api/projects.ts`) should now work with real endpoints:

```typescript
// Example usage
const projects = await projectsApi.list();
const newProject = await projectsApi.create("My research idea");
const project = await projectsApi.get(newProject.project_id);
const artifact = await projectsApi.getArtifact(project.id, "ProjectContext");
await projectsApi.runStage(project.id, "problem-framing");
await projectsApi.approveStage(project.id, "problem-framing", {}, "Approved");
```

### Environment Configuration

Ensure `frontend/strategy-pipeline-ui/.env.local` has:
```
VITE_API_BASE_URL=http://localhost:5000
```

---

## Next Steps

### Day 2: Connect Frontend (4-6 hours)

1. **Update frontend API client**
   - Remove mock/fallback logic
   - Use real JSON endpoints

2. **Test project creation flow**
   - Create project via UI
   - Verify in data directory
   - Load project detail page

3. **Test artifact loading**
   - Display ProjectContext
   - Show stage progression
   - Handle errors

### Day 3: Stage Execution (4-6 hours)

1. **Connect run/approve buttons**
2. **Add loading states**
3. **Handle errors gracefully**
4. **Test full workflow**

---

## Implementation Details

### Artifact Serialization

The `_serialize_artifact()` helper handles:
- Pydantic `model_dump()` (primary)
- Dataclass `asdict()` (fallback)
- Datetime to ISO format conversion
- Enum to value conversion

### Stage Name Mapping

Frontend → Backend:
- `project-setup` → `project-setup`
- `problem-framing` → `problem-framing`
- `research-questions` → `research-questions`
- `search-concept-expansion` → `search-concept-expansion`
- `database-query-plan` → `database-query-plan`

### Current Stage Determination

Logic:
1. If ProjectContext approved → stage 1
2. If ProblemFraming approved → stage 2
3. If ResearchQuestionSet approved → stage 3
4. If SearchConceptBlocks approved → stage 4
5. If DatabaseQueryPlan approved → stage 5
6. Draft status → stay at current stage

---

## Troubleshooting

### CORS Errors

**Problem:** Browser shows CORS policy error  
**Solution:** 
- Ensure flask-cors is installed
- Check frontend origin matches CORS config
- Restart Flask server

### 404 Not Found

**Problem:** Endpoint returns 404  
**Solution:**
- Check endpoint URL spelling
- Verify project_id exists in data directory
- Check artifact type name matches exactly

### 500 Internal Server Error

**Problem:** Server error on API call  
**Solution:**
- Check Flask console for traceback
- Verify all required artifacts exist
- Check stage dependencies met

### Connection Refused

**Problem:** Can't connect to localhost:5000  
**Solution:**
- Start Flask server: `python interfaces/web_app.py`
- Check port 5000 not in use
- Try: `http://127.0.0.1:5000/api/projects`

---

## Files Modified

✅ `interfaces/web_app.py` - Added JSON API endpoints  
✅ `requirements.txt` - Added flask-cors dependency  
✅ `test_api_endpoints.py` - Created API test script  

---

## Success Criteria

- [x] GET /api/projects returns project list
- [x] POST /api/projects creates new project
- [x] GET /api/projects/:id returns project details
- [x] GET /api/projects/:id/artifacts/:type returns artifact
- [x] POST /api/projects/:id/stages/:name/run executes stage
- [x] POST /api/projects/:id/stages/:name/approve approves stage
- [x] CORS headers present for frontend
- [x] Error handling with proper status codes
- [x] JSON serialization working
- [x] Test script verifies all endpoints

---

## 🎉 Status: COMPLETE

The JSON API layer is fully implemented and ready for frontend integration!

**Next:** Start the frontend dev server and connect it to these endpoints.

```bash
# Terminal 1: Backend
python interfaces/web_app.py

# Terminal 2: Frontend  
cd frontend/strategy-pipeline-ui
npm run dev

# Terminal 3: Test
python test_api_endpoints.py
```

Happy coding! 🚀

