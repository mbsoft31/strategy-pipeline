# 🎯 Day 3: Stage Execution Integration - Action Plan

**Status:** Ready to Start  
**Prerequisites:** Days 1-2 Complete ✅  
**Time Estimate:** 4-6 hours

---

## 📋 Today's Goals

1. ✅ Test backend API endpoints are working
2. ✅ Test frontend can connect to backend
3. ✅ Verify project creation workflow
4. ✅ Test stage execution from UI
5. ✅ Verify approval workflow
6. ✅ Add loading states and error handling

---

## 🧪 Step-by-Step Testing Plan

### Step 1: Verify Backend is Ready (15 min)

**Terminal 1: Start Backend**
```bash
cd C:\Users\mouadh\Desktop\strategy-pipeline
python interfaces/web_app.py
```

**Expected Output:**
```
============================================================
HITL Research Strategy Pipeline - Web UI
============================================================
...
Server starting on: http://localhost:5000
...
Running on http://127.0.0.1:5000
```

**Quick Test:**
```bash
# In another terminal
curl http://localhost:5000/api/projects
# Should return: {"projects": [...]}
```

✅ **Checkpoint:** Backend responds with JSON

---

### Step 2: Verify Frontend is Ready (15 min)

**Terminal 2: Start Frontend**
```bash
cd C:\Users\mouadh\Desktop\strategy-pipeline\frontend\strategy-pipeline-ui
npm run dev
```

**Expected Output:**
```
VITE v6.x.x ready in XXX ms

➜  Local:   http://localhost:3000/
```

**Quick Test:**
- Open browser to http://localhost:3000
- Dashboard should load
- Check browser console (F12) - should have no errors

✅ **Checkpoint:** Frontend loads without errors

---

### Step 3: Test Project Creation (30 min)

**In Browser:**

1. Click "New Project" button
2. Enter research idea:
   ```
   Investigate retrieval-augmented generation techniques for reducing hallucinations in large language models used for medical question answering
   ```
3. Submit form

**Watch for:**
- Network request to `POST /api/projects`
- Status code 201
- Redirect to project detail page
- Project appears in dashboard

**If it works:**
- ✅ New project folder in `data/project_xxxxx/`
- ✅ ProjectContext.json file created
- ✅ Project shows in dashboard list

**If it fails:**
- Check browser console for errors
- Check backend terminal for error logs
- Check Network tab for request/response

✅ **Checkpoint:** Can create projects via UI

---

### Step 4: Test Project Detail View (30 min)

**After creating project:**

1. Navigate to project detail page
2. Should see:
   - Project title
   - Stage progression timeline
   - Stage 0 (Project Setup) marked as "Draft"
   - "Run Stage 1" button enabled

**Check:**
- Stage timeline displays correctly
- Current stage highlighted
- Next stage button visible
- Artifact data loaded

✅ **Checkpoint:** Project detail page works

---

### Step 5: Test Stage Execution (1 hour)

**Run Stage 1 (Problem Framing):**

1. Click "Run Stage 1" button
2. Should see:
   - Loading indicator
   - Progress message
   - Draft artifact appears

**Expected behavior:**
- Network request to `POST /api/projects/:id/stages/problem-framing/run`
- Response contains draft_artifact
- UI displays ProblemFraming data
- "Approve" button appears

**Check backend logs:**
```
127.0.0.1 - - [timestamp] "POST /api/projects/project_xxx/stages/problem-framing/run HTTP/1.1" 200 -
```

✅ **Checkpoint:** Can execute stages from UI

---

### Step 6: Test Stage Approval (30 min)

**Approve Stage:**

1. Review draft artifact
2. Optionally edit fields
3. Click "Approve" button
4. Should see:
   - Success message
   - Stage 1 marked as "Approved"
   - Stage 2 unlocked

**Expected behavior:**
- Network request to `POST /api/projects/:id/stages/problem-framing/approve`
- Artifact saved with "approved" status
- Next stage becomes available
- UI updates to show progress

✅ **Checkpoint:** Can approve stages from UI

---

### Step 7: Test Full Workflow (1 hour)

**Complete stages 0-4:**

1. Approve Stage 0 (Project Setup)
2. Run Stage 1 (Problem Framing)
3. Approve Stage 1
4. Run Stage 2 (Research Questions)
5. Approve Stage 2
6. Run Stage 3 (Search Expansion)
7. Approve Stage 3
8. Run Stage 4 (Query Plan)
9. Approve Stage 4

**For each stage, verify:**
- Stage executes successfully
- Draft artifact displays
- Approval saves correctly
- Next stage unlocks
- Data persists in files

✅ **Checkpoint:** Full workflow works end-to-end

---

### Step 8: Add Loading States (1 hour)

**Enhance UX with loading indicators:**

**File:** `frontend/strategy-pipeline-ui/src/components/StageView.tsx`

Check if loading states are shown:
- While running stage
- While approving
- During artifact loading

If missing, these should already be handled by TanStack Query's `isLoading` state.

✅ **Checkpoint:** Loading states display properly

---

### Step 9: Error Handling (1 hour)

**Test error scenarios:**

1. **Network Error:** Stop backend, try to create project
   - Should show: "Unable to connect to server"

2. **Invalid Input:** Try to create project with empty idea
   - Should show: "Research idea is required"

3. **Stage Error:** Try to run stage twice
   - Should handle gracefully

**Check browser console and network tab for each error.**

✅ **Checkpoint:** Errors handled gracefully

---

## 🐛 Common Issues & Solutions

### Issue 1: "Failed to create project"
**Solution:** Already fixed! Make sure backend is running.

### Issue 2: CORS errors
**Solution:** Already fixed with flask-cors.

### Issue 3: 404 on API calls
**Check:**
- Backend is running on port 5000
- Frontend .env.local has `VITE_API_BASE_URL=http://localhost:5000`
- Routes are correct in web_app.py

### Issue 4: Type errors in console
**Check:**
- Response format matches TypeScript types
- All required fields present
- Dates formatted as ISO strings

### Issue 5: Artifacts not loading
**Check:**
- Data directory exists
- JSON files created correctly
- File permissions OK

---

## 📊 Success Criteria for Day 3

By end of day, you should be able to:

- ✅ Create new projects via UI
- ✅ View project details
- ✅ Execute stages 0-4
- ✅ Approve each stage
- ✅ See stage progression
- ✅ View generated artifacts
- ✅ Handle errors gracefully
- ✅ See loading states

---

## 🎯 Deliverables

1. **Working demo** - Can show stakeholders
2. **Tested workflow** - All stages 0-4 work
3. **Error handling** - No crashes
4. **Loading states** - Good UX

---

## 🚀 Quick Start Commands

**Terminal 1: Backend**
```bash
cd C:\Users\mouadh\Desktop\strategy-pipeline
python interfaces/web_app.py
```

**Terminal 2: Frontend**
```bash
cd frontend/strategy-pipeline-ui
npm run dev
```

**Browser:**
```
http://localhost:3000
```

---

## ✅ Testing Checklist

Use this checklist as you test:

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Dashboard loads
- [ ] Can click "New Project"
- [ ] Can enter research idea
- [ ] Can submit project
- [ ] Redirects to project detail
- [ ] Stage timeline displays
- [ ] Can click "Run Stage"
- [ ] Loading indicator shows
- [ ] Draft artifact appears
- [ ] Can click "Approve"
- [ ] Next stage unlocks
- [ ] Can complete all 5 stages
- [ ] Data persists in files
- [ ] Errors show user-friendly messages
- [ ] Can reload page without losing state

---

## 📝 Notes & Observations

As you test, note any issues here:

**Issues Found:**
- 

**Performance Notes:**
- 

**UX Improvements Needed:**
- 

**Bugs to Fix:**
- 

---

## 🎉 Day 3 Success!

When all checkpoints pass, you'll have:
- ✅ Fully functional frontend-backend integration
- ✅ Working stage execution workflow
- ✅ Real-time artifact loading
- ✅ Professional UI/UX
- ✅ Demo-ready application!

**Then move to Day 4: Artifact Display Polish**

---

**Let's start testing! Open those two terminals and let's see it work! 🚀**

