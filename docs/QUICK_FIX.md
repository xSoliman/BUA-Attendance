# ⚡ Quick Fix - Frontend Can't See Backend

## The Problem
Your frontend can't connect to your backend on Render.

## The Solution (3 Steps)

### Step 1: Fix API URL ✅ (DONE)
I've already fixed the API URL in `frontend/app.js` to include `/api`:
```javascript
const API_BASE_URL = 'https://bua-attendance.onrender.com/api';
```

**Now commit and push**:
```bash
git add frontend/app.js
git commit -m "Fix API URL - add /api path"
git push
```

### Step 2: Add CORS Configuration ⚠️ (YOU NEED TO DO THIS)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click on your **backend service** (the one named like "bua-attendance")
3. Click **Environment** tab on the left
4. Click **Add Environment Variable** button
5. Add this variable:
   - **Key**: `FRONTEND_ORIGIN`
   - **Value**: Your frontend URL (e.g., `https://bua-attendance-frontend.onrender.com`)
6. Click **Save Changes**
7. Wait for backend to redeploy (~2 minutes)

**Important**: Use your ACTUAL frontend URL from Render!

### Step 3: Wait & Test

**Wait for deployments**:
- Frontend will redeploy automatically after you push (Step 1)
- Backend will redeploy after you add environment variable (Step 2)
- Check "Events" tab in each service to see deployment status

**Test it**:
1. Open your frontend URL in browser
2. You should see the service account email on the config page
3. If not, press F12 and check Console tab for errors

---

## Quick Test Commands

Replace URLs with your actual Render URLs:

```bash
# Test backend
curl https://bua-attendance.onrender.com/api/service-account-email

# Should return something like:
# {"email":"bua-ta-attendance@optical-loop-458800-q0.iam.gserviceaccount.com"}
```

---

## Common Mistakes

❌ **Wrong**: `FRONTEND_ORIGIN=https://bua-attendance-frontend.onrender.com/`  
✅ **Correct**: `FRONTEND_ORIGIN=https://bua-attendance-frontend.onrender.com`  
(No trailing slash!)

❌ **Wrong**: `API_BASE_URL = 'https://bua-attendance.onrender.com'`  
✅ **Correct**: `API_BASE_URL = 'https://bua-attendance.onrender.com/api'`  
(Must include /api!)

---

## Still Not Working?

### Run the diagnostic script:
```bash
./test-render-connection.sh
```

### Or check manually:

**1. Check Backend Logs**:
- Go to Render Dashboard → Backend Service → Logs
- Look for errors

**2. Check Browser Console**:
- Open frontend in browser
- Press F12
- Go to Console tab
- Look for red errors

**3. Read detailed guide**:
```bash
cat RENDER_TROUBLESHOOTING.md
```

---

## What Should Happen

After completing all steps:

1. ✅ Frontend loads without errors
2. ✅ Service account email displays on config page
3. ✅ No CORS errors in browser console
4. ✅ Can validate spreadsheet
5. ✅ Can select course and week
6. ✅ Scanner works

---

## Need More Help?

- **Detailed Guide**: `RENDER_TROUBLESHOOTING.md`
- **Test Script**: `./test-render-connection.sh`
- **Render Support**: https://render.com/docs/support

---

**TL;DR**:
1. Push the fixed `frontend/app.js` (already done)
2. Add `FRONTEND_ORIGIN` environment variable to backend in Render
3. Wait for deployments
4. Test!
