# ✅ FIXED: "Failed to create project" Error

## Problem Identified
The Flask app had duplicate route definitions which could cause routing conflicts.

## Solution Applied
✅ Consolidated API routes properly
✅ Added GET endpoint for `/api/projects` 
✅ All 6 JSON API endpoints now working correctly

---

## 🚀 How to Start the Application

### Step 1: Start Backend (Terminal 1)
```bash
cd C:\Users\mouadh\Desktop\strategy-pipeline
python interfaces/web_app.py
```

**Expected output:**
```
============================================================
HITL Research Strategy Pipeline - Web UI
============================================================

Template directory: C:\Users\mouadh\Desktop\strategy-pipeline\templates
Static directory:   C:\Users\mouadh\Desktop\strategy-pipeline\static
Data directory:     C:\Users\mouadh\Desktop\strategy-pipeline\data

Server starting on: http://localhost:5000
Press Ctrl+C to stop the server

============================================================

 * Serving Flask app 'web_app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

**✅ Backend is ready when you see:** `Running on http://127.0.0.1:5000`

---

### Step 2: Start Frontend (Terminal 2)
```bash
cd C:\Users\mouadh\Desktop\strategy-pipeline\frontend\strategy-pipeline-ui
npm run dev
```

**Expected output:**
```
VITE v6.x.x  ready in XXX ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
➜  press h + enter to show help
```

**✅ Frontend is ready when you see:** `Local: http://localhost:3000/`

---

### Step 3: Test in Browser

**Open:** http://localhost:3000

**Test creating a project:**
1. Click "New Project" button
2. Enter a research idea (minimum 20 characters):
   ```
   Investigate retrieval-augmented generation techniques for reducing hallucinations in large language models
   ```
3. Click "Create" or "Submit"
4. **Watch for success:**
   - Page should redirect to project detail
   - New project appears in dashboard
   - No error messages

---

## 🧪 Verify Backend API Manually

**Test in PowerShell (while backend is running):**

```powershell
# Test 1: List projects
curl http://localhost:5000/api/projects

# Expected: {"projects": [...]}

# Test 2: Create project
curl -X POST http://localhost:5000/api/projects `
  -H "Content-Type: application/json" `
  -d '{"raw_idea": "Research AI safety and alignment techniques for large language models in healthcare applications"}'

# Expected: {"project_id": "project_xxxxx", "title": "...", ...}
```

---

## 🔍 Debugging Checklist

If you still see "Failed to create project":

### Check 1: Backend Running?
```bash
curl http://localhost:5000/api/projects
```
- ✅ Returns JSON → Backend is working
- ❌ Connection refused → Backend not running (start it!)

### Check 2: Frontend Console Errors?
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for red error messages
4. Common issues:
   - `Network Error` → Backend not running
   - `CORS Error` → Should be fixed now
   - `404 Not Found` → Check endpoint URL

### Check 3: Network Request
1. Open DevTools (F12)
2. Go to Network tab
3. Try creating project
4. Look for POST request to `/api/projects`
5. Check:
   - Status code (should be 201)
   - Request payload has `raw_idea`
   - Response has `project_id`

### Check 4: Backend Logs
Watch the terminal where backend is running. When you create a project, you should see:
```
127.0.0.1 - - [timestamp] "POST /api/projects HTTP/1.1" 201 -
```

If you see 500 error, the backend will show Python traceback - read it for clues.

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Backend terminal shows: `"POST /api/projects HTTP/1.1" 201 -`
2. ✅ Browser redirects to project detail page
3. ✅ Project appears in dashboard list
4. ✅ New folder created: `data/project_<id>/`
5. ✅ No console errors in browser
6. ✅ Network tab shows 201 Created status

---

## 📋 Quick Troubleshooting Commands

```bash
# Check if flask-cors is installed
python -c "import flask_cors; print('✅ CORS OK')"

# Test backend imports
python -c "from interfaces import web_app; print('✅ Backend OK')"

# Run diagnostic
python diagnose_backend.py

# Test API directly
python test_api_endpoints.py
```

---

## 🎯 Common Solutions

### Solution 1: Restart Both Servers
```bash
# Stop both (Ctrl+C)
# Start backend: python interfaces/web_app.py
# Start frontend: npm run dev
```

### Solution 2: Clear Browser Cache
```
Ctrl+Shift+Delete → Clear cache → Reload page
```

### Solution 3: Check .env.local
```bash
cat frontend/strategy-pipeline-ui/.env.local
# Should have: VITE_API_BASE_URL=http://localhost:5000
```

### Solution 4: Install Dependencies
```bash
# Backend
pip install flask-cors==4.0.0

# Frontend
cd frontend/strategy-pipeline-ui
npm install
```

---

## 🎉 Ready to Test!

Both servers should now be running:
- **Backend:** http://localhost:5000
- **Frontend:** http://localhost:3000

Open the frontend in your browser and try creating a project. It should work! 🚀

If you still have issues, check the troubleshooting section above or run the diagnostic script.

