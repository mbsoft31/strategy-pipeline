# Strategy Pipeline - Frontend Integration Strategic Plan

**Date:** November 22, 2025  
**Current Status:** 71% Complete (5/7 stages implemented)  
**Recent Achievement:** ✅ Frontend UI scaffolding complete & deployed

---

## 📊 Current State Analysis

### ✅ What's Working

#### Backend Pipeline (71% Complete)
- **Stage 0-4:** Fully implemented and tested
  - ✅ Project Setup (LLM-powered context generation)
  - ✅ Problem Framing (with OpenAlex validation)
  - ✅ Research Questions (PICO-based, 5 RQ types)
  - ✅ Search Expansion (synonym generation + fallback)
  - ✅ Database Query Plan (multi-DB, complexity analysis)

#### Anti-Hallucination Engine (100% Complete)
- ✅ 7 database dialects (PubMed, Scopus, arXiv, OpenAlex, WoS, Semantic Scholar, Crossref)
- ✅ Syntax validation preventing hallucinated operators
- ✅ Deterministic query generation
- ✅ Excluded term handling with NOT operators

#### Infrastructure (100% Complete)
- ✅ LLM provider abstraction (OpenAI, OpenRouter)
- ✅ File persistence service
- ✅ Configuration management
- ✅ Comprehensive test suite (11 test files)
- ✅ 11 sample projects in data directory

#### Frontend (95% Complete - NEW!)
- ✅ React 19.2 + TypeScript scaffolding
- ✅ TanStack Router for routing
- ✅ TanStack Query for data fetching
- ✅ shadcn/ui component library
- ✅ Complete type definitions (100% spec compliance)
- ✅ API client with backend compatibility layer
- ✅ Production build working (0 errors)

#### Documentation (Excellent)
- ✅ 35+ documentation files
- ✅ Architecture guides
- ✅ Implementation status
- ✅ Frontend specifications (7 detailed docs)

### ⏳ What's Missing

#### Backend Pipeline (29%)
- ⚠️ **Stage 5:** Screening Criteria (scaffolded but not implemented)
- ⚠️ **Stage 6:** Strategy Export (scaffolded but not implemented)

#### Frontend Integration (10%)
- ⚠️ Backend JSON API endpoints (currently HTML-based)
- ⚠️ Project listing endpoint
- ⚠️ Stage execution JSON responses
- ⚠️ Real-time artifact loading
- ⚠️ Stage-specific artifact editors

#### Quality & Polish
- ⚠️ End-to-end integration testing
- ⚠️ Performance optimization
- ⚠️ Error handling polish
- ⚠️ User onboarding flow

---

## 🎯 Strategic Options - Choose Your Path

### Option A: Complete the Pipeline (Backend-First)
**Goal:** Finish stages 5-6, achieve 100% pipeline completion

**Pros:**
- Complete core product functionality
- Deliver on original vision
- Strong foundation for all users

**Cons:**
- No user interface yet
- Harder to demo to stakeholders
- Delayed user feedback

**Time:** 1-2 weeks

---

### Option B: Frontend Integration (User-First) ⭐ RECOMMENDED
**Goal:** Connect frontend to backend, create working demo

**Pros:**
- Immediate user-facing value
- Can demo to stakeholders NOW
- Get user feedback early
- Frontend is already built!
- Stages 0-4 are enough for MVP

**Cons:**
- Stages 5-6 remain incomplete
- Need to add JSON API endpoints

**Time:** 3-5 days

---

### Option C: Hybrid Approach (Balanced)
**Goal:** Basic frontend integration + Stage 5 completion

**Pros:**
- User interface for working stages
- Extend pipeline by 1 stage
- Balanced progress

**Cons:**
- Split focus
- Takes longer than either alone

**Time:** 1-2 weeks

---

## 🚀 RECOMMENDED PATH: Option B (Frontend Integration)

### Why This Makes Sense

1. **Frontend is DONE** - You just completed the scaffolding!
2. **Stages 0-4 are VALUABLE** - Users can create projects through query generation
3. **Demo-able in Days** - Show working product to stakeholders
4. **User Feedback Loop** - Learn what users actually need
5. **Momentum** - Build on frontend success immediately

### What This Unlocks

✅ Working web application  
✅ Visual project creation  
✅ Stage progression interface  
✅ Query generation UI  
✅ Professional demo material  
✅ User testing capability  

---

## 📋 Detailed Action Plan: Frontend Integration (3-5 Days)

### Day 1: Backend JSON API Layer

#### Tasks
1. **Create API endpoints** (`interfaces/api.py` or extend `web_app.py`)
   ```python
   @app.route('/api/projects', methods=['GET'])
   def list_projects():
       projects = controller.list_projects()
       return jsonify({'projects': [...]})
   
   @app.route('/api/projects/<project_id>', methods=['GET'])
   def get_project(project_id):
       # Load all artifacts and return project status
   
   @app.route('/api/projects/<project_id>/artifacts/<artifact_type>')
   def get_artifact(project_id, artifact_type):
       # Return JSON artifact
   ```

2. **Add CORS support** for development
   ```python
   from flask_cors import CORS
   CORS(app)
   ```

3. **Test endpoints with Postman/curl**

**Deliverable:** Working JSON API for frontend consumption

---

### Day 2: Connect Frontend to Real Backend

#### Tasks
1. **Update `frontend/strategy-pipeline-ui/src/lib/api/projects.ts`**
   - Remove mock/fallback logic
   - Use real JSON endpoints
   
2. **Test project creation flow**
   - Create project via frontend
   - Verify it appears in data directory
   - Load project detail page

3. **Test artifact loading**
   - Load ProjectContext from data directory
   - Display in ProjectDetail component
   - Verify stage status detection

**Deliverable:** Frontend can create and view projects

---

### Day 3: Stage Execution Integration

#### Tasks
1. **Add stage execution endpoint**
   ```python
   @app.route('/api/projects/<project_id>/stages/<stage_name>/run', methods=['POST'])
   def run_stage(project_id, stage_name):
       result = controller.run_stage(project_id, stage_name)
       return jsonify(result.to_dict())
   ```

2. **Add approval endpoint**
   ```python
   @app.route('/api/projects/<project_id>/stages/<stage_name>/approve', methods=['POST'])
   def approve_stage(project_id, stage_name):
       edits = request.json.get('edits', {})
       # Apply edits and approve
   ```

3. **Update frontend StageView component**
   - Connect run/approve buttons to API
   - Show loading states
   - Handle errors gracefully

**Deliverable:** Full stage execution workflow working

---

### Day 4: Artifact Display & Basic Editing

#### Tasks
1. **Implement read-only artifact viewers**
   - ProjectContext display
   - ProblemFraming display
   - Research Questions display
   - Query display with syntax highlighting

2. **Add basic editing capability**
   - Text field editing
   - List item editing
   - Save draft functionality

3. **Polish the UI**
   - Loading states
   - Error messages
   - Success notifications

**Deliverable:** Users can view and edit artifacts

---

### Day 5: Testing & Polish

#### Tasks
1. **End-to-end testing**
   - Create new project
   - Run all stages 0-4
   - Approve each stage
   - Verify artifacts saved correctly

2. **Error handling**
   - Network errors
   - Invalid inputs
   - Missing artifacts

3. **Documentation**
   - Update README with demo instructions
   - Create user guide
   - Record demo video (optional)

**Deliverable:** Production-ready demo application

---

## 📈 Success Metrics

### After 5 Days
- [ ] Frontend connects to backend
- [ ] Can create projects via UI
- [ ] Can run stages 0-4 via UI
- [ ] Can view generated queries
- [ ] Zero critical bugs
- [ ] Demo-ready application

### User Experience
- [ ] < 2 seconds page load
- [ ] < 5 seconds stage execution (excluding LLM)
- [ ] Clear error messages
- [ ] Intuitive navigation
- [ ] Mobile-responsive (basic)

---

## 🎯 Alternative Quick Wins (If You Choose Different Path)

### Quick Win 1: Complete Stage 5 (2-3 hours)
**File:** `src/stages/screening_criteria.py`

**What to implement:**
```python
def _generate_screening_criteria(self, framing, concepts, queries):
    # Inclusion criteria based on PICO elements
    # Exclusion criteria from scope_out
    # Study type filters
    # Language filters
    # Date range filters
```

**Impact:** 86% pipeline completion (6/7 stages)

---

### Quick Win 2: Add Export Functionality (3-4 hours)
**File:** `src/stages/strategy_export.py`

**What to implement:**
```python
def _generate_markdown_summary(self, artifacts):
    # Title + metadata
    # Problem statement
    # Research questions
    # Search queries for each database
    # Screening criteria
    # References
```

**Impact:** 100% pipeline completion!

---

### Quick Win 3: Better Demo Script (1 hour)
**File:** `examples/demos/complete_workflow.py`

**Create:** End-to-end demo showing:
- Project creation
- Stage progression
- Query generation
- Export output

**Impact:** Better stakeholder presentations

---

## 🔄 Long-term Roadmap (Post-Integration)

### Phase 1: MVP Enhancement (2-4 weeks)
1. Complete stages 5-6
2. Advanced artifact editors
3. Query syntax highlighting
4. Validation feedback UI
5. Export bundle download

### Phase 2: Intelligence Layer (4-6 weeks)
1. Autonomous research agent integration
2. Paper search & synthesis
3. Literature review generation
4. Citation management

### Phase 3: Collaboration Features (6-8 weeks)
1. Multi-user support
2. Team workspaces
3. Version control for artifacts
4. Comments & annotations

### Phase 4: Enterprise Features (8-12 weeks)
1. API authentication
2. Usage analytics
3. Custom database integration
4. White-label deployment

---

## 💡 Strong Recommendation

### Go with Option B: Frontend Integration

**Why:**
1. You just finished frontend scaffolding - ride that momentum!
2. Stages 0-4 are already VERY valuable
3. Demo-able product in under a week
4. User feedback will guide stages 5-6 design
5. Easier to fundraise/publish with working demo

### Next Action (Right Now):

1. **Read** `frontend/specs/API_SPECIFICATION.md` - understand expected endpoints
2. **Create** `interfaces/api.py` - start with project listing endpoint
3. **Test** with curl/Postman before connecting frontend
4. **Update** frontend API client once backend ready
5. **Test** end-to-end with real project

### Timeline:
- **Day 1:** JSON API endpoints
- **Day 2:** Frontend connection
- **Day 3:** Stage execution
- **Day 4:** Artifact display
- **Day 5:** Testing & demo

**By Nov 27 (5 days):** You'll have a working, demo-able web application!

---

## 📞 Need Help Deciding?

### Questions to Ask Yourself:

1. **Do you need to demo this soon?** → Go frontend integration
2. **Do you need 100% feature completion?** → Finish stages 5-6 first
3. **Do you want user feedback?** → Frontend integration wins
4. **Is this for a paper/publication?** → Complete pipeline first
5. **Is this for a startup/product?** → Frontend integration critical

### My Prediction:

You'll get more value from a **working demo** than from **complete but invisible** backend stages.

Users don't care if stages 5-6 are missing if they can:
- ✅ Create projects through a beautiful UI
- ✅ Generate research questions automatically
- ✅ Get multi-database Boolean queries
- ✅ See the anti-hallucination engine in action

You can add stages 5-6 later based on actual user needs!

---

## ✅ Decision Matrix

| Factor | Frontend Integration | Complete Pipeline |
|--------|---------------------|-------------------|
| **Time to demo** | 5 days | 2+ weeks |
| **User feedback** | Immediate | Delayed |
| **Stakeholder wow** | High | Medium |
| **Technical completion** | 71% | 100% |
| **Risk** | Low | Medium |
| **Learning** | User needs | Technical completeness |

**Winner:** 🏆 **Frontend Integration** (5 out of 6 factors)

---

## 🎬 Conclusion

You're at an exciting inflection point! The frontend is done, the backend stages 0-4 work beautifully, and you have 11 sample projects proving the system works.

**My advice:** Strike while the iron is hot. Connect that beautiful React UI to your solid backend, get a working demo, and show it to users. Their feedback will be invaluable for designing stages 5-6.

You've already proven the technical viability. Now prove the user value!

**Next commit message:**
```
feat(api): Add JSON API endpoints for frontend integration

- Add /api/projects listing endpoint
- Add /api/projects/:id detail endpoint  
- Add /api/projects/:id/artifacts/:type
- Enable CORS for development
- Return JSON responses for all endpoints

Connects React UI to backend pipeline (Stages 0-4)
```

Ready to build something users can actually use? Let's go! 🚀

---

## 🚀 Implementation Details

### Backend API Endpoints (Detailed Spec)

#### 1. List Projects
```python
@app.route('/api/projects', methods=['GET'])
def list_projects():
    """Return all projects with metadata."""
    project_ids = controller.list_projects()
    projects = []
    
    for pid in project_ids:
        ctx = controller.get_artifact(pid, "ProjectContext", ProjectContext)
        if ctx:
            projects.append({
                'id': pid,
                'title': ctx.title,
                'status': ctx.status.value,
                'created_at': ctx.created_at.isoformat(),
                'updated_at': ctx.updated_at.isoformat() if ctx.updated_at else None,
                'current_stage': _determine_current_stage(pid),
            })
    
    return jsonify({'projects': projects})
```

#### 2. Get Project Details
```python
@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Return project with all artifact statuses."""
    if not controller.persistence_service.project_exists(project_id):
        return jsonify({'error': 'Project not found'}), 404
    
    artifacts = {}
    for artifact_type in ['ProjectContext', 'ProblemFraming', 'ConceptModel', 
                          'ResearchQuestionSet', 'SearchConceptBlocks', 'DatabaseQueryPlan']:
        art = controller.get_artifact(project_id, artifact_type)
        if art:
            artifacts[artifact_type] = art.status.value
    
    return jsonify({
        'id': project_id,
        'artifacts': artifacts,
        'current_stage': _determine_current_stage(project_id),
        'total_stages': 7,
    })
```

#### 3. Get Artifact
```python
@app.route('/api/projects/<project_id>/artifacts/<artifact_type>', methods=['GET'])
def get_artifact(project_id, artifact_type):
    """Return specific artifact as JSON."""
    artifact = controller.get_artifact(project_id, artifact_type)
    if not artifact:
        return jsonify({'error': 'Artifact not found'}), 404
    
    return jsonify(artifact.model_dump())
```

#### 4. Create Project
```python
@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create new project from raw idea."""
    data = request.get_json()
    raw_idea = data.get('raw_idea', '').strip()
    
    if not raw_idea:
        return jsonify({'error': 'raw_idea is required'}), 400
    
    result = controller.start_project(raw_idea=raw_idea)
    
    return jsonify({
        'project_id': result.draft_artifact.id,
        'title': result.draft_artifact.title,
        'stage_result': {
            'stage_name': result.stage_name,
            'draft_artifact': result.draft_artifact.model_dump(),
            'prompts': result.prompts,
            'validation_errors': result.validation_errors,
        }
    }), 201
```

#### 5. Run Stage
```python
@app.route('/api/projects/<project_id>/stages/<stage_name>/run', methods=['POST'])
def run_stage(project_id, stage_name):
    """Execute a pipeline stage."""
    data = request.get_json() or {}
    
    try:
        result = controller.run_stage(project_id, stage_name, **data)
        
        return jsonify({
            'stage_name': result.stage_name,
            'draft_artifact': result.draft_artifact.model_dump() if result.draft_artifact else None,
            'prompts': result.prompts,
            'validation_errors': result.validation_errors,
            'metadata': result.metadata.model_dump() if result.metadata else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### 6. Approve Stage
```python
@app.route('/api/projects/<project_id>/stages/<stage_name>/approve', methods=['POST'])
def approve_stage(project_id, stage_name):
    """Approve stage with optional edits."""
    data = request.get_json() or {}
    edits = data.get('edits', {})
    user_notes = data.get('user_notes')
    
    try:
        result = controller.approve_stage(
            project_id, 
            stage_name, 
            edits=edits,
            user_notes=user_notes
        )
        
        return jsonify({
            'success': True,
            'artifact': result.model_dump() if result else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Frontend API Client Updates

#### Update `projects.ts`
```typescript
export const projectsApi = {
  list: async (): Promise<Project[]> => {
    const response = await apiClient.get<{ projects: Project[] }>('/api/projects');
    return response.projects;
  },

  get: async (projectId: string): Promise<Project> => {
    return await apiClient.get<Project>(`/api/projects/${projectId}`);
  },

  create: async (rawIdea: string, title?: string): Promise<{ project_id: string }> => {
    return await apiClient.post<{ project_id: string }>('/api/projects', {
      raw_idea: rawIdea,
      title,
    });
  },

  getArtifact: async <T = unknown>(
    projectId: string,
    artifactType: string
  ): Promise<T> => {
    return await apiClient.get<T>(`/api/projects/${projectId}/artifacts/${artifactType}`);
  },

  runStage: async (
    projectId: string,
    stageName: string,
    inputs?: Record<string, unknown>
  ): Promise<StageResult> => {
    return await apiClient.post<StageResult>(
      `/api/projects/${projectId}/stages/${stageName}/run`,
      inputs
    );
  },

  approveStage: async (
    projectId: string,
    stageName: string,
    edits?: Record<string, unknown>,
    userNotes?: string
  ): Promise<void> => {
    await apiClient.post(
      `/api/projects/${projectId}/stages/${stageName}/approve`,
      { edits, user_notes: userNotes }
    );
  },
};
```

---

## 📝 Testing Checklist

### Backend API Tests
- [ ] `GET /api/projects` returns list
- [ ] `GET /api/projects/:id` returns project
- [ ] `GET /api/projects/:id/artifacts/:type` returns artifact
- [ ] `POST /api/projects` creates project
- [ ] `POST /api/projects/:id/stages/:name/run` executes stage
- [ ] `POST /api/projects/:id/stages/:name/approve` approves stage
- [ ] CORS headers present
- [ ] Error responses have proper status codes
- [ ] JSON responses properly formatted

### Frontend Integration Tests
- [ ] Project list loads and displays
- [ ] Create new project form works
- [ ] Project detail page loads
- [ ] Stage timeline shows correct status
- [ ] Run stage button triggers execution
- [ ] Approve button saves artifact
- [ ] Loading states show during API calls
- [ ] Error messages display on failure
- [ ] Navigation works between pages

### End-to-End Tests
- [ ] Create project → See in list
- [ ] Run Stage 0 → Artifact saved
- [ ] Approve Stage 0 → Stage 1 unlocked
- [ ] Run Stage 1 → ProblemFraming created
- [ ] Continue through Stage 4
- [ ] All artifacts persist correctly
- [ ] Can reload page and state preserved

---

## 🎯 Success Criteria

**You're done when:**

1. ✅ User can open browser to `localhost:3000`
2. ✅ User can click "New Project" and enter idea
3. ✅ User sees project appear in dashboard
4. ✅ User can click project and see stage timeline
5. ✅ User can click "Run Stage" and see progress
6. ✅ User can see generated artifact (questions, queries)
7. ✅ User can click "Approve" and unlock next stage
8. ✅ User can complete stages 0-4 without errors
9. ✅ All data persists in `data/` directory
10. ✅ Application handles errors gracefully

**Bonus points:**
- ✅ Mobile responsive
- ✅ Keyboard shortcuts work
- ✅ Dark mode (if implemented)
- ✅ Demo video recorded
- ✅ User guide written

---

## 🚨 Common Pitfalls to Avoid

1. **CORS Issues**
   - Solution: Add `flask-cors` package, configure properly
   - Test with browser dev tools network tab

2. **Data Format Mismatches**
   - Solution: Use Pydantic `.model_dump()` for serialization
   - Validate against TypeScript types

3. **Route Conflicts**
   - Solution: Ensure `/api/*` routes don't conflict with HTML routes
   - Use different Flask Blueprint if needed

4. **Error Handling**
   - Solution: Wrap all API calls in try-catch
   - Return proper HTTP status codes (400, 404, 500)

5. **State Management**
   - Solution: Use TanStack Query cache invalidation
   - Refetch after mutations

6. **Performance**
   - Solution: Add loading skeletons
   - Implement pagination for project list
   - Cache artifacts in frontend

---

## 📚 Additional Resources

### Documentation to Reference
- `frontend/specs/API_SPECIFICATION.md` - Expected API structure
- `frontend/specs/DATA_MODELS.md` - Artifact JSON schemas
- `docs/architecture-overview.md` - System architecture
- `docs/pipeline-design.md` - Stage progression logic

### Code to Study
- `interfaces/web_app.py` - Existing HTML routes
- `src/controller.py` - Pipeline orchestration
- `frontend/strategy-pipeline-ui/src/lib/api/` - API client layer
- `frontend/strategy-pipeline-ui/src/components/` - UI components

### Tools to Use
- Postman/Insomnia - API testing
- Browser DevTools - Network debugging
- React DevTools - Component inspection
- TanStack Query DevTools - Cache debugging

---

**Questions? Ready to implement? Let's build this!**

