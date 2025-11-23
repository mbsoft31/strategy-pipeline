# 🔧 Troubleshooting: "Failed to create project" Error

**Date:** November 22, 2025  
**Issue:** Frontend shows "Failed to create project. Please try again."

---

## 🎯 Quick Fix Checklist

### 1. ✅ Is the Backend Running?

**Check:**
```bash
curl http://localhost:5000/api/projects
```

**Expected:** JSON response with `{"projects": [...]}`

**If error:** Backend not running. Start it:
```bash
cd C:\Users\mouadh\Desktop\strategy-pipeline
python interfaces/web_app.py
```

---

### 2. ✅ Is the Frontend Connected?

**Check browser console** (F12 → Console tab)

**Look for:**
- ❌ `Network Error` → Backend not running
- ❌ `CORS Error` → CORS not configured (should be fixed)
- ❌ `404 Not Found` → Wrong endpoint URL
- ❌ `400 Bad Request` → Invalid data sent

**Check Network tab** (F12 → Network tab)
- Look for POST request to `/api/projects`
- Check request payload
- Check response

---

### 3. ✅ Common Issues & Solutions

#### Issue A: Backend Not Running
**Symptom:** `Failed to fetch` or `Network Error`

**Solution:**
```bash
# Terminal 1 - Start Backend
cd C:\Users\mouadh\Desktop\strategy-pipeline
python interfaces/web_app.py

# Should see:
# Server starting on: http://localhost:5000
```

#### Issue B: CORS Error
**Symptom:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:** Already fixed in code, but verify:
```python
# In interfaces/web_app.py, should have:
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:5173"]}})
```

#### Issue C: Port Already in Use
**Symptom:** `Address already in use`

**Solution:**
```bash
# Windows - Find and kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or use different port in web_app.py:
app.run(debug=True, port=5001)
# Then update frontend .env.local:
VITE_API_BASE_URL=http://localhost:5001
```

#### Issue D: Empty/Invalid Research Idea
**Symptom:** `raw_idea is required` or `must be at least 20 characters`

**Solution:** Enter longer research idea (minimum 20 characters)

#### Issue E: Frontend Build Issues
**Symptom:** Blank page or console errors

**Solution:**
```bash
cd frontend/strategy-pipeline-ui
npm install  # Install dependencies
npm run dev  # Start dev server
```

---

## 🧪 Step-by-Step Diagnosis

### Step 1: Run Diagnostic
```bash
cd C:\Users\mouadh\Desktop\strategy-pipeline
python diagnose_backend.py
```

**Expected:** All checks pass ✅

### Step 2: Test Backend API Directly
```bash
# Test list projects
curl http://localhost:5000/api/projects

# Test create project
curl -X POST http://localhost:5000/api/projects ^
  -H "Content-Type: application/json" ^
  -d "{\"raw_idea\": \"Research AI hallucination reduction techniques in medical QA systems\"}"
```

**Expected:** JSON response with project_id

### Step 3: Check Frontend Console

**Open browser to:** http://localhost:3000

**Open DevTools:** F12 or Right-click → Inspect

**Console tab:** Look for errors

**Network tab:** 
- Filter by "Fetch/XHR"
- Look for POST to `/api/projects`
- Check status code (should be 201)
- Check response

### Step 4: Verify Environment

**Frontend .env.local:**
```bash
cat frontend/strategy-pipeline-ui/.env.local
# Should show: VITE_API_BASE_URL=http://localhost:5000
```

**Backend check:**
```bash
python -c "import flask_cors; print('CORS OK')"
# Should print: CORS OK
```

---

## 🔍 Detailed Debugging

### Check Backend Logs

When you start the backend:
```bash
python interfaces/web_app.py
```

**Watch for:**
- ✅ `Server starting on: http://localhost:5000`
- ✅ `Running on http://127.0.0.1:5000`

**When you create project, should see:**
- `127.0.0.1 - - [timestamp] "POST /api/projects HTTP/1.1" 201 -`

**If error:**
- Look for Python traceback
- Check error message
- Note which line fails

### Check Frontend Request

**Browser DevTools → Network tab:**

1. **Request:**
   - URL: `http://localhost:5000/api/projects`
   - Method: `POST`
   - Content-Type: `application/json`
   - Payload: `{"raw_idea": "..."}`

2. **Response:**
   - Status: `201 Created`
   - Body: `{"project_id": "...", "title": "..."}`

**If 400 Error:**
- Check request payload format
- Verify raw_idea field present
- Check idea length (min 20 chars)

**If 500 Error:**
- Check backend console for traceback
- Look at error message
- Check data directory permissions

---

## 🚀 Complete Startup Guide

### Terminal 1: Backend
```bash
cd C:\Users\mouadh\Desktop\strategy-pipeline

# Install dependencies (first time only)
pip install flask-cors==4.0.0

# Start backend
python interfaces/web_app.py

# Keep this terminal open
# Should see: Server starting on: http://localhost:5000
```

### Terminal 2: Frontend
```bash
cd C:\Users\mouadh\Desktop\strategy-pipeline\frontend\strategy-pipeline-ui

# Install dependencies (first time only)
npm install

# Start frontend
npm run dev

# Keep this terminal open
# Should see: Local: http://localhost:3000
```

### Browser
```
Open: http://localhost:3000
```

---

## 📋 Verification Checklist

Before creating a project, verify:

- [ ] Backend terminal shows: "Server starting on: http://localhost:5000"
- [ ] Frontend terminal shows: "Local: http://localhost:3000"
- [ ] Browser opens to http://localhost:3000
- [ ] Dashboard loads (no errors in console)
- [ ] "New Project" button visible
- [ ] No CORS errors in console
- [ ] Network tab shows API accessible

Then try creating project:

- [ ] Click "New Project"
- [ ] Enter research idea (min 20 characters)
- [ ] Click "Create" or "Submit"
- [ ] Watch Network tab for POST request
- [ ] Check status code (should be 201)
- [ ] Check response has project_id
- [ ] Page should redirect to project detail

---

## 🛠️ Manual API Test

If frontend fails, test backend directly:

**PowerShell:**
```powershell
# Create project via API
$headers = @{
    "Content-Type" = "application/json"
}
$body = @{
    raw_idea = "Investigate retrieval-augmented generation for reducing LLM hallucinations in medical question answering"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/projects" -Method Post -Headers $headers -Body $body
```

**Expected output:**
```json
{
  "project_id": "project_abc123",
  "title": "...",
  "stage_result": {...}
}
```

**If this works:** Problem is in frontend
**If this fails:** Problem is in backend

---

## 📞 Still Having Issues?

### Collect Debug Info

1. **Backend logs:**
   - Copy any error messages from Python
   - Note which endpoint fails

2. **Frontend console:**
   - Screenshot of errors
   - Copy network request/response

3. **System info:**
   - Python version: `python --version`
   - Node version: `node --version`
   - OS: Windows (confirmed)

### Common Solutions

**Reset everything:**
```bash
# Stop all servers (Ctrl+C in both terminals)

# Backend
cd C:\Users\mouadh\Desktop\strategy-pipeline
python diagnose_backend.py  # Should pass

# Frontend
cd frontend/strategy-pipeline-ui
npm install
npm run build  # Should succeed with 0 errors

# Start fresh
# Terminal 1: python interfaces/web_app.py
# Terminal 2: npm run dev
```

**Check data directory:**
```bash
cd C:\Users\mouadh\Desktop\strategy-pipeline
ls data/  # Should show project folders
```

**Verify API client:**
```bash
cd frontend/strategy-pipeline-ui
cat src/lib/api/projects.ts | Select-String "create.*async"
# Should show clean implementation without FormData
```

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Backend shows request: `POST /api/projects 201`
2. ✅ Frontend redirects to new project page
3. ✅ Project appears in dashboard
4. ✅ New folder created in `data/project_<id>/`
5. ✅ Browser console has no errors
6. ✅ Network tab shows 201 status

---

## 📚 Additional Resources

- **API Documentation:** `API_ENDPOINTS_README.md`
- **Integration Guide:** `FRONTEND_INTEGRATION_SUMMARY.md`
- **Test Script:** `python test_api_endpoints.py`
- **Diagnostic:** `python diagnose_backend.py`

---

**Most Common Fix:** Just restart the backend server! 🔄

