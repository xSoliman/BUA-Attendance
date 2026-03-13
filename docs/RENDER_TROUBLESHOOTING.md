# 🔧 Render Deployment Troubleshooting

## Issue: Frontend Can't Connect to Backend

### Quick Fix Checklist

#### 1. ✅ Fix API URL (DONE)
The API_BASE_URL in `frontend/app.js` has been updated to:
```javascript
const API_BASE_URL = 'https://bua-attendance.onrender.com/api';
```

**Next Step**: Commit and push this change:
```bash
git add frontend/app.js
git commit -m "Fix API URL - add /api path"
git push
```

#### 2. ⚠️ Check CORS Configuration

Your backend needs to allow requests from your frontend URL.

**Go to Render Dashboard** → **Backend Service** → **Environment**

Add or update this environment variable:
- **Key**: `FRONTEND_ORIGIN`
- **Value**: `https://YOUR-FRONTEND-URL.onrender.com`

Example:
```
FRONTEND_ORIGIN=https://bua-attendance-frontend.onrender.com
```

**Important**: Replace with your ACTUAL frontend URL from Render!

#### 3. 🔍 Verify Backend is Running

Test your backend directly:

**Test 1: Health Check**
```bash
curl https://bua-attendance.onrender.com/health
```
Expected: `{"status":"healthy"}`

**Test 2: Service Account Email**
```bash
curl https://bua-attendance.onrender.com/api/service-account-email
```
Expected: `{"email":"your-service-account@..."}`

**Test 3: Root Endpoint**
```bash
curl https://bua-attendance.onrender.com/
```
Expected: API info with version

#### 4. 🌐 Check Browser Console

Open your frontend in browser:
1. Press F12 to open Developer Tools
2. Go to "Console" tab
3. Look for errors

**Common Errors:**

**Error: "CORS policy"**
```
Access to fetch at 'https://bua-attendance.onrender.com/api/...' 
from origin 'https://your-frontend.onrender.com' has been blocked by CORS policy
```
**Solution**: Add `FRONTEND_ORIGIN` environment variable to backend (see step 2)

**Error: "Failed to fetch"**
```
TypeError: Failed to fetch
```
**Solution**: Check if backend URL is correct and backend is running

**Error: "404 Not Found"**
```
GET https://bua-attendance.onrender.com/api/service-account-email 404
```
**Solution**: Verify API_BASE_URL includes `/api` path

#### 5. 📋 Complete Configuration Checklist

**Backend Environment Variables** (Render Dashboard → Backend → Environment):
- [ ] `GOOGLE_SERVICE_ACCOUNT_JSON` - Your service account JSON
- [ ] `FRONTEND_ORIGIN` - Your frontend URL (e.g., `https://bua-attendance-frontend.onrender.com`)

**Frontend Configuration** (in `frontend/app.js`):
- [ ] `API_BASE_URL` - Your backend URL with `/api` (e.g., `https://bua-attendance.onrender.com/api`)

**Git Status**:
- [ ] Changes committed
- [ ] Changes pushed to GitHub
- [ ] Render auto-deployed (check dashboard)

---

## Step-by-Step Fix

### Step 1: Update Frontend URL
```bash
# Already done! The API_BASE_URL has been fixed.
# Just commit and push:
git add frontend/app.js
git commit -m "Fix API URL"
git push
```

### Step 2: Add CORS Configuration

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click on your **backend service** (e.g., "bua-attendance")
3. Go to **Environment** tab
4. Click **Add Environment Variable**
5. Add:
   - Key: `FRONTEND_ORIGIN`
   - Value: Your frontend URL (find it in your frontend service)
6. Click **Save Changes**
7. Backend will automatically redeploy (~2 minutes)

### Step 3: Wait for Deployments

**Check Backend Deployment**:
1. Go to backend service in Render
2. Check "Events" tab
3. Wait for "Deploy succeeded" message
4. Check logs for any errors

**Check Frontend Deployment**:
1. Go to frontend service in Render
2. Check "Events" tab
3. Wait for "Deploy succeeded" message

### Step 4: Test Connection

**Test Backend**:
```bash
# Replace with your actual backend URL
curl https://bua-attendance.onrender.com/api/service-account-email
```

**Test Frontend**:
1. Open your frontend URL in browser
2. Open Developer Tools (F12)
3. Go to Console tab
4. Refresh page
5. Check for errors

**Test Full Flow**:
1. Visit frontend URL
2. Should see service account email on config page
3. Enter a test Spreadsheet ID
4. Click "Save Configuration"
5. Should validate successfully

---

## Common Issues & Solutions

### Issue 1: "CORS Error"

**Symptom**: Browser console shows CORS policy error

**Solution**:
1. Add `FRONTEND_ORIGIN` to backend environment variables
2. Make sure the URL matches EXACTLY (including https://)
3. No trailing slash in the URL
4. Wait for backend to redeploy

**Verify CORS is working**:
```bash
# Replace URLs with your actual URLs
curl -H "Origin: https://your-frontend.onrender.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://bua-attendance.onrender.com/api/service-account-email -v
```

Look for `Access-Control-Allow-Origin` in response headers.

### Issue 2: "404 Not Found"

**Symptom**: API calls return 404

**Possible Causes**:
1. Missing `/api` in API_BASE_URL
2. Backend not deployed correctly
3. Wrong backend URL

**Solution**:
1. Verify `API_BASE_URL` in `frontend/app.js` includes `/api`
2. Test backend endpoints directly with curl
3. Check backend logs in Render dashboard

### Issue 3: "500 Internal Server Error"

**Symptom**: Backend returns 500 error

**Possible Causes**:
1. `GOOGLE_SERVICE_ACCOUNT_JSON` not set or invalid
2. Backend code error
3. Missing dependencies

**Solution**:
1. Check backend logs in Render dashboard
2. Verify `GOOGLE_SERVICE_ACCOUNT_JSON` is set correctly
3. Make sure it's valid JSON (no line breaks in the middle)
4. Check for Python errors in logs

### Issue 4: Backend Takes 30+ Seconds to Respond

**Symptom**: First request after idle takes very long

**Cause**: Render free tier "cold start" - backend spins down after 15 minutes of inactivity

**Solutions**:
1. **Use UptimeRobot** (Recommended - Free):
   - Go to [uptimerobot.com](https://uptimerobot.com)
   - Sign up (free)
   - Add monitor: `https://bua-attendance.onrender.com/health`
   - Interval: 5 minutes
   - Keeps backend warm

2. **Upgrade to Paid Tier** ($7/month):
   - No cold starts
   - Better performance
   - Go to Render dashboard → Upgrade

### Issue 5: Service Account Email Not Showing

**Symptom**: Config page shows "Error loading email"

**Possible Causes**:
1. Backend not accessible
2. CORS blocking request
3. `GOOGLE_SERVICE_ACCOUNT_JSON` not set

**Solution**:
1. Test backend directly: `curl https://bua-attendance.onrender.com/api/service-account-email`
2. Check browser console for errors
3. Verify environment variable is set in Render dashboard

---

## Verification Commands

Run these commands to verify everything is working:

```bash
# 1. Test backend health
curl https://bua-attendance.onrender.com/health

# 2. Test service account endpoint
curl https://bua-attendance.onrender.com/api/service-account-email

# 3. Test CORS (replace with your frontend URL)
curl -H "Origin: https://your-frontend.onrender.com" \
     https://bua-attendance.onrender.com/api/service-account-email -v

# 4. Check if frontend is accessible
curl -I https://your-frontend.onrender.com
```

---

## Debug Checklist

Go through this checklist:

**Backend**:
- [ ] Backend URL is correct: `https://bua-attendance.onrender.com`
- [ ] Health endpoint works: `/health` returns `{"status":"healthy"}`
- [ ] API endpoint works: `/api/service-account-email` returns email
- [ ] Environment variable `GOOGLE_SERVICE_ACCOUNT_JSON` is set
- [ ] Environment variable `FRONTEND_ORIGIN` is set to frontend URL
- [ ] Backend logs show no errors
- [ ] Backend deployment succeeded

**Frontend**:
- [ ] Frontend URL is accessible
- [ ] `API_BASE_URL` in `app.js` is correct (includes `/api`)
- [ ] `API_BASE_URL` matches backend URL
- [ ] Changes are committed and pushed
- [ ] Frontend deployment succeeded
- [ ] Browser console shows no CORS errors

**Connection**:
- [ ] Backend allows frontend origin (CORS)
- [ ] Frontend can reach backend
- [ ] Service account email displays on config page
- [ ] No 404 errors in browser console
- [ ] No CORS errors in browser console

---

## Still Not Working?

### Get Your URLs

**Find Backend URL**:
1. Go to Render Dashboard
2. Click on backend service
3. Copy URL at top (e.g., `https://bua-attendance.onrender.com`)

**Find Frontend URL**:
1. Go to Render Dashboard
2. Click on frontend service
3. Copy URL at top (e.g., `https://bua-attendance-frontend.onrender.com`)

### Check Configuration

**Backend Environment Variables**:
```bash
# Should have these two:
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
FRONTEND_ORIGIN=https://your-frontend.onrender.com
```

**Frontend app.js**:
```javascript
// Should be:
const API_BASE_URL = 'https://bua-attendance.onrender.com/api';
// NOT:
const API_BASE_URL = 'https://bua-attendance.onrender.com';  // ❌ Missing /api
```

### Contact Support

If still not working after all checks:

1. **Check Render Status**: https://status.render.com
2. **Render Support**: https://render.com/docs/support
3. **Share Error Details**:
   - Backend logs from Render dashboard
   - Browser console errors
   - Curl command outputs

---

## Quick Fix Summary

```bash
# 1. Fix frontend API URL (already done)
git add frontend/app.js
git commit -m "Fix API URL"
git push

# 2. Add FRONTEND_ORIGIN to backend in Render dashboard
# Key: FRONTEND_ORIGIN
# Value: https://your-frontend.onrender.com

# 3. Wait for deployments to complete

# 4. Test
curl https://bua-attendance.onrender.com/api/service-account-email

# 5. Open frontend in browser and check console
```

---

**Need more help? Check the browser console (F12) and backend logs in Render dashboard for specific error messages!**
