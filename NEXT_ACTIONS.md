# ✅ NEXT: Test Stage Navigation & Execution

**Current Status:** Project creation ✅ Working  
**Next Goal:** Get at least one stage running  
**Time Estimate:** 1-2 hours

---

## 🎯 Immediate Actions (Do This Now!)

### Action 1: Navigate to a Project (5 min)

**Steps:**
1. Open browser to http://localhost:3000
2. You should see dashboard with projects
3. Click on any project in the list
4. **Expected:** Navigate to project detail page
5. **Expected:** See stage timeline/progression

**Watch for:**
- URL changes to `/projects/:projectId`
- Project title displays
- Stage information shows
- Current stage highlighted

**If it works:** ✅ Move to Action 2  
**If it fails:** Note error, check browser console

---

### Action 2: Locate Stage Execution UI (10 min)

**On project detail page, look for:**
- Stage timeline/list
- Current stage indicator
- "Run Stage" button or similar
- Stage status (not started/draft/approved)

**Possible UI patterns:**
1. **Timeline view** - Vertical list of stages with status
2. **Tab view** - Tabs for each stage
3. **Stepper** - Step-by-step progression
4. **Cards** - Card for each stage

**Find:**
- Where is Stage 1 (Problem Framing)?
- Is there a button to run it?
- Can you click on the stage?

---

### Action 3: Attempt Stage 1 Execution (20 min)

**Try to run Stage 1:**

1. Look for "Run Stage 1" or "Execute" button
2. Click it
3. **Watch browser Network tab** (F12 → Network)
4. **Expected request:**
   ```
   POST /api/projects/<project_id>/stages/problem-framing/run
   ```
5. **Expected response:**
   ```json
   {
     "stage_name": "problem-framing",
     "draft_artifact": {...},
     "prompts": [...],
     "validation_errors": []
   }
   ```

**Observe:**
- Does loading indicator show?
- Does artifact data appear?
- Are there any errors in console?
- Does backend log the request?

---

### Action 4: Review Artifact Display (15 min)

**If stage executes successfully:**

**Look for artifact data:**
- Problem statement
- PICO elements (Population, Intervention, Comparison, Outcome)
- Goals
- Scope (in/out)
- Feasibility assessment
- Risks

**Check UI quality:**
- Is data readable?
- Is layout clean?
- Can you see all fields?
- Is JSON pretty-printed?

---

### Action 5: Test Approval (20 min)

**Look for "Approve" button:**

1. Find approval UI
2. Optionally edit fields
3. Click "Approve"
4. **Expected request:**
   ```
   POST /api/projects/<project_id>/stages/problem-framing/approve
   ```
5. **Expected result:**
   - Success message
   - Stage marked as approved
   - Stage 2 unlocks
   - Can proceed to next stage

---

## 🐛 Troubleshooting Common Issues

### Issue: Can't navigate to project

**Check:**
- Is project ID valid?
- Does route exist in TanStack Router?
- Check `src/routes/projects/$projectId.tsx`

**Quick fix:**
- Manually navigate to `/projects/project_<id>`
- Check browser console for routing errors

### Issue: No "Run Stage" button

**Check:**
- Is StageView component rendering?
- Are stage routes configured?
- Check `src/routes/projects/$projectId/stages/$stageName.tsx`

**Workaround:**
- Use API test script to run stage:
  ```bash
  python test_api_endpoints.py
  ```

### Issue: Stage executes but doesn't display

**Check:**
- Network tab shows 200 response?
- Response has draft_artifact field?
- Types match between backend and frontend?

**Debug:**
- Check backend `_serialize_artifact()` function
- Verify frontend type definitions
- Log response to console

### Issue: Approval doesn't work

**Check:**
- Network request is sent?
- Request has correct format?
- Backend receives edits?

**Debug:**
- Check backend logs
- Verify endpoint exists
- Test with curl directly

---

## 📊 Expected Behavior

### Project Detail Page Should Show:

```
┌─────────────────────────────────────────┐
│  Project: <Title>                       │
│  Status: In Progress                    │
├─────────────────────────────────────────┤
│  Stage Progress:                        │
│  ✅ Stage 0: Project Setup (Approved)  │
│  🔄 Stage 1: Problem Framing (Draft)   │
│  ⚪ Stage 2: Research Questions        │
│  ⚪ Stage 3: Search Expansion          │
│  ⚪ Stage 4: Query Plan                │
│                                         │
│  [Run Stage 1] [View Details]          │
└─────────────────────────────────────────┘
```

### Stage View Should Show:

```
┌─────────────────────────────────────────┐
│  Stage 1: Problem Framing               │
├─────────────────────────────────────────┤
│  Problem Statement:                     │
│  [Editable text field]                  │
│                                         │
│  PICO Elements:                         │
│  • Population: ...                      │
│  • Intervention: ...                    │
│  • Comparison: ...                      │
│  • Outcome: ...                         │
│                                         │
│  [Approve] [Edit] [Cancel]              │
└─────────────────────────────────────────┘
```

---

## ✅ Success Checklist

**After completing these actions, you should:**

- [ ] Can navigate to project detail
- [ ] Can see stage progression
- [ ] Can identify current stage
- [ ] Can run Stage 1
- [ ] Artifact data displays
- [ ] Can approve Stage 1
- [ ] Stage 2 becomes available

**If 4+ items checked:** ✅ Great progress!  
**If 7 items checked:** 🎉 Excellent! Ready for Day 4!

---

## 📝 Document Your Findings

**As you test, note:**

**What works:**
- 

**What doesn't work:**
- 

**Errors encountered:**
- 

**Questions:**
- 

**Next steps needed:**
- 

---

## 🚀 After These Actions

**If everything works:**
- Move to `DAY3-5_ACCELERATED.md`
- Continue with remaining stages
- Start UI polish

**If issues found:**
- Document errors clearly
- Check troubleshooting guides
- Test API endpoints directly
- Debug systematically

---

## 💡 Pro Tips

1. **Keep both terminal windows visible**
   - Watch backend logs in real-time
   - See API requests as they happen

2. **Use Browser DevTools extensively**
   - Console for errors
   - Network for API calls
   - React DevTools for state

3. **Test incrementally**
   - Get one thing working
   - Then move to next
   - Don't try to fix everything at once

4. **Take screenshots**
   - Document what works
   - Record errors
   - Use for presentation

---

## 🎯 Goal for This Session

**Primary:**
- ✅ Navigate to at least one project detail page
- ✅ Identify stage execution UI
- ✅ Run at least Stage 1 successfully

**Stretch:**
- ✅ Approve Stage 1
- ✅ Run Stage 2
- ✅ Complete full workflow through Stage 4

**Time:** 1-2 hours

---

**Ready? Let's navigate to a project and see what we have! 🚀**

**Current browsers should be open:**
- Backend logs in Terminal 1
- Frontend in Terminal 2  
- Browser at http://localhost:3000

**Let's do this! 💪**

