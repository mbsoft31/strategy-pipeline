# 🚀 Moving to Stage 1: Problem Framing

**Project:** project_031edc5f  
**Current Stage:** 0 (Project Setup - DRAFT)  
**Next Stage:** 1 (Problem Framing)

---

## ✅ Step-by-Step Guide

### Option 1: Via Web UI (Recommended) 🌐

**1. Start Both Servers**

**Terminal 1 - Backend:**
```bash
cd C:\Users\mouadh\Desktop\strategy-pipeline
python interfaces/web_app.py
```
Wait for: `Server starting on: http://localhost:5000`

**Terminal 2 - Frontend:**
```bash
cd C:\Users\mouadh\Desktop\strategy-pipeline\frontend\strategy-pipeline-ui
npm run dev
```
Wait for: `Local: http://localhost:3000`

**2. Navigate in Browser:**
```
http://localhost:3000/projects/project_031edc5f
```

You'll see:
- ✅ Project title
- ✅ StageTimeline with 5 stage cards
- ✅ Progress bar showing "1 of 5 complete"

**3. Click on Stage 1 Card:**
- Look for "Stage 1: Problem Framing"
- Click the "Continue" or "Run Stage" button
- OR click the whole card

**4. You'll navigate to:**
```
http://localhost:3000/projects/project_031edc5f/stages/problem-framing
```

**5. You'll see a blue DEBUG box showing:**
```
DEBUG: StageView Loaded
Project: project_031edc5f
Stage: problem-framing
Loading: Yes/No
Error: Yes/No
Artifact: Yes/No
```

**6. Click "Run Stage" button**
- Loading spinner appears
- Backend generates ProblemFraming artifact
- After ~5-10 seconds, artifact displays

**7. Review the generated content:**
- Problem statement
- PICO elements
- Goals
- Scope boundaries

**8. Click "Approve & Continue"**
- Toast notification appears
- Navigate back to project detail
- Stage 1 now has green checkmark
- Stage 2 unlocks

---

### Option 2: Via API (Alternative) 🔧

**If backend is running, test directly:**

**Run Stage 1:**
```bash
curl -X POST http://localhost:5000/api/projects/project_031edc5f/stages/problem-framing/run -H "Content-Type: application/json" -d "{}"
```

**Expected response:**
```json
{
  "stage_name": "problem-framing",
  "draft_artifact": {
    "id": "...",
    "problem_statement": "...",
    "pico_elements": {...},
    "goals": [...],
    ...
  },
  "prompts": [...],
  "validation_errors": []
}
```

**Verify artifact created:**
```bash
ls C:\Users\mouadh\Desktop\strategy-pipeline\data\project_031edc5f\
```

Should now show: `ProblemFraming.json`

**View the artifact:**
```bash
cat C:\Users\mouadh\Desktop\strategy-pipeline\data\project_031edc5f\ProblemFraming.json
```

**Approve the stage:**
```bash
curl -X POST http://localhost:5000/api/projects/project_031edc5f/stages/problem-framing/approve -H "Content-Type: application/json" -d '{"edits": {}, "user_notes": "Approved"}'
```

---

### Option 3: Direct Python Script 🐍

**Run this script:**

```python
# run_stage1.py
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.controller import PipelineController
from src.services import FilePersistenceService, SimpleModelService

# Initialize
data_dir = project_root / 'data'
controller = PipelineController(
    SimpleModelService(),
    FilePersistenceService(str(data_dir))
)

# Run Stage 1
project_id = 'project_031edc5f'
print(f"Running Stage 1 for {project_id}...")

result = controller.run_stage(project_id, 'problem-framing')

print(f"\n✅ Stage executed!")
print(f"Stage: {result.stage_name}")
print(f"Problem statement: {result.draft_artifact.problem_statement[:200]}...")
print(f"Goals: {len(result.draft_artifact.goals)} defined")
print(f"Validation errors: {result.validation_errors}")

# Approve stage
print(f"\nApproving stage...")
controller.approve_stage(
    project_id,
    'problem-framing',
    edits={},
    user_notes="Auto-approved"
)

print("✅ Stage 1 approved!")
print(f"\nCheck: data/{project_id}/ProblemFraming.json")
```

**Run it:**
```bash
cd C:\Users\mouadh\Desktop\strategy-pipeline
python run_stage1.py
```

---

## 🎯 What You'll Get

### ProblemFraming Artifact Contains:

1. **Problem Statement**
   - Clear articulation of research problem
   - Based on your research idea

2. **PICO Elements**
   - Population: Target group
   - Intervention: What's being studied
   - Comparison: What it's compared to
   - Outcome: Expected results

3. **Research Goals**
   - List of 3-5 specific goals
   - Aligned with problem statement

4. **Scope**
   - What's included
   - What's excluded
   - Boundaries defined

5. **Feasibility Assessment**
   - Practical considerations
   - Resource requirements

---

## 🐛 Troubleshooting

### Issue: Can't see Stage 1 button

**Check:**
- Is backend running? (`curl http://localhost:5000/api/projects`)
- Is frontend running? (Open http://localhost:3000)
- Does project detail page load?

**Solution:**
- Restart both servers
- Hard refresh browser (Ctrl+Shift+R)

### Issue: "Run Stage" button does nothing

**Check:**
- Browser console for errors (F12)
- Network tab for API call
- Backend logs for Python errors

**Solution:**
- Check console.log output
- Verify project ID is correct
- Test API directly with curl

### Issue: Stage runs but nothing displays

**Check:**
- Debug box should show: `Artifact: Yes`
- Look for `ProblemFraming.json` in data directory

**Solution:**
- Check artifact file exists
- Verify it has valid JSON
- Try refreshing page

---

## ✅ Success Indicators

**You'll know it worked when:**

1. ✅ ProblemFraming.json file created in `data/project_031edc5f/`
2. ✅ File contains problem statement, PICO, goals
3. ✅ Web UI shows ArtifactViewer with data
4. ✅ Can approve and move to Stage 2
5. ✅ Toast notification appears
6. ✅ Progress bar shows 2/5 complete

---

## 📍 URLs to Use

**Project Detail:**
```
http://localhost:3000/projects/project_031edc5f
```

**Stage 1 Direct:**
```
http://localhost:3000/projects/project_031edc5f/stages/problem-framing
```

**Stage 2 (after approval):**
```
http://localhost:3000/projects/project_031edc5f/stages/research-questions
```

---

## 🎉 Quick Start (Easiest Way)

**Just do this:**

1. **Terminal 1:** `python interfaces/web_app.py`
2. **Terminal 2:** `cd frontend/strategy-pipeline-ui && npm run dev`
3. **Browser:** Open http://localhost:3000/projects/project_031edc5f
4. **Click:** Stage 1 card or "Continue" button
5. **Click:** "Run Stage" button (big blue button)
6. **Wait:** 5-10 seconds for generation
7. **Review:** Generated problem framing
8. **Click:** "Approve & Continue" button
9. **Done:** Stage 1 complete, move to Stage 2!

---

## 📊 Expected Timeline

- **Start servers:** 10 seconds
- **Navigate to page:** 5 seconds
- **Run Stage 1:** 10 seconds (AI generation)
- **Review content:** 1-2 minutes
- **Approve:** 5 seconds
- **Total:** ~3 minutes

---

**Ready? Start the servers and navigate to the project!** 🚀

**Current file location:**
```
C:\Users\mouadh\Desktop\strategy-pipeline\data\project_031edc5f\ProjectContext.json ✅
```

**Next file will be:**
```
C:\Users\mouadh\Desktop\strategy-pipeline\data\project_031edc5f\ProblemFraming.json
```

**Let's move forward!** 🎯

