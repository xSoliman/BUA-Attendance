# 🗺️ Deployment Flowchart

Visual guide to deploying your QR Attendance System.

---

## Quick Decision Tree

```
Do you have a GitHub account?
│
├─ NO → Create one at github.com
│
└─ YES → Do you have code on GitHub?
    │
    ├─ NO → Run: ./deploy.sh (follow prompts)
    │
    └─ YES → Choose hosting platform
        │
        ├─ Want easiest? → Render.com
        ├─ Want best performance? → Railway.app
        └─ Want best frontend? → Vercel + Render
```

---

## Deployment Flow - Render.com

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Prepare Repository                                  │
├─────────────────────────────────────────────────────────────┤
│ • git init                                                   │
│ • git add .                                                  │
│ • git commit -m "Ready for deployment"                      │
│ • Create GitHub repo                                         │
│ • git push                                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Deploy Backend                                      │
├─────────────────────────────────────────────────────────────┤
│ • Go to render.com                                           │
│ • New → Web Service                                          │
│ • Connect GitHub repo                                        │
│ • Root: backend                                              │
│ • Build: pip install -r requirements.txt                    │
│ • Start: uvicorn main:app --host 0.0.0.0 --port $PORT      │
│ • Add env var: GOOGLE_SERVICE_ACCOUNT_JSON                  │
│ • Deploy                                                     │
│ • Copy URL: https://xxx-backend.onrender.com                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Deploy Frontend                                     │
├─────────────────────────────────────────────────────────────┤
│ • Render → New → Static Site                                │
│ • Same GitHub repo                                           │
│ • Root: frontend                                             │
│ • Publish: .                                                 │
│ • Deploy                                                     │
│ • Copy URL: https://xxx-frontend.onrender.com               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Connect Services                                    │
├─────────────────────────────────────────────────────────────┤
│ • Edit frontend/app.js:                                      │
│   const API_BASE_URL = 'https://xxx-backend.onrender.com/api'│
│ • Add backend env var:                                       │
│   FRONTEND_ORIGIN = 'https://xxx-frontend.onrender.com'     │
│ • git commit & push                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Test & Launch                                       │
├─────────────────────────────────────────────────────────────┤
│ • Visit frontend URL                                         │
│ • Test configuration                                         │
│ • Test session setup                                         │
│ • Test QR scanning                                           │
│ • Share with TAs                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ✅ DEPLOYED!
```

---

## Testing Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Backend Tests                                                │
├─────────────────────────────────────────────────────────────┤
│ ✓ https://backend-url.onrender.com/                         │
│   → Should return API info                                   │
│                                                              │
│ ✓ https://backend-url.onrender.com/health                   │
│   → Should return {"status": "healthy"}                      │
│                                                              │
│ ✓ https://backend-url.onrender.com/api/service-account-email│
│   → Should return service account email                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Frontend Tests                                               │
├─────────────────────────────────────────────────────────────┤
│ ✓ https://frontend-url.onrender.com                         │
│   → Should load config page                                  │
│                                                              │
│ ✓ Service account email displays                            │
│   → Should show email from backend                           │
│                                                              │
│ ✓ Enter test Spreadsheet ID                                 │
│   → Should validate successfully                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Integration Tests                                            │
├─────────────────────────────────────────────────────────────┤
│ ✓ Select course sheet                                        │
│ ✓ Select attendance column                                   │
│ ✓ Start scanner                                              │
│ ✓ Allow camera access                                        │
│ ✓ Scan QR code                                               │
│ ✓ Verify attendance recorded                                 │
│ ✓ Test manual entry                                          │
│ ✓ Verify cooldown works                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ✅ ALL TESTS PASS!
```

---

## Troubleshooting Flow

```
Problem: Backend not starting
│
├─ Check Render logs
│  │
│  ├─ "Module not found" → Check requirements.txt
│  ├─ "Port already in use" → Render handles this automatically
│  └─ "Environment variable not set" → Add GOOGLE_SERVICE_ACCOUNT_JSON
│
└─ Still not working?
   └─ Check FREE_DEPLOYMENT_GUIDE.md

─────────────────────────────────────────────────────────────

Problem: Frontend can't connect to backend
│
├─ Check browser console
│  │
│  ├─ "CORS error" → Add FRONTEND_ORIGIN to backend env vars
│  ├─ "Network error" → Check API_BASE_URL in frontend/app.js
│  └─ "404 Not Found" → Verify backend URL is correct
│
└─ Still not working?
   └─ Check TROUBLESHOOTING.md

─────────────────────────────────────────────────────────────

Problem: Camera not working
│
├─ Check browser permissions
│  │
│  ├─ "Permission denied" → Allow camera in browser settings
│  ├─ "Not secure context" → Ensure using HTTPS (not HTTP)
│  └─ "No camera found" → Check device camera
│
└─ Still not working?
   └─ Try different browser (Chrome recommended)

─────────────────────────────────────────────────────────────

Problem: Attendance not recording
│
├─ Check Google Sheet
│  │
│  ├─ Service Account not added → Add as Editor
│  ├─ Wrong Spreadsheet ID → Verify ID from URL
│  ├─ Wrong sheet name → Check exact name
│  └─ Wrong column name → Check exact name
│
└─ Check backend logs for errors
```

---

## Cold Start Prevention Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Problem: Backend takes 30s to respond after idle            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Solution: Keep Backend Warm                                  │
├─────────────────────────────────────────────────────────────┤
│ Option 1: UptimeRobot (Recommended)                         │
│ • Go to uptimerobot.com                                      │
│ • Sign up (free)                                             │
│ • Add monitor                                                │
│ • URL: https://backend-url.onrender.com/health              │
│ • Interval: 5 minutes                                        │
│ • Done! Backend stays warm                                   │
│                                                              │
│ Option 2: Upgrade to Paid                                    │
│ • Render paid tier: $7/month                                 │
│ • No cold starts                                             │
│ • Better performance                                         │
│                                                              │
│ Option 3: Use Railway Instead                                │
│ • No cold starts on free tier                                │
│ • $5 credit/month                                            │
│ • ~$2-3/month after credit                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Maintenance Flow

```
Weekly:
┌─────────────────────────────────────────────────────────────┐
│ • Check Render dashboard for errors                         │
│ • Review usage statistics                                    │
│ • Test critical functionality                                │
└─────────────────────────────────────────────────────────────┘

Monthly:
┌─────────────────────────────────────────────────────────────┐
│ • Update dependencies (if needed)                            │
│ • Review security settings                                   │
│ • Backup configuration                                       │
│ • Check Google Sheets API quota                             │
└─────────────────────────────────────────────────────────────┘

As Needed:
┌─────────────────────────────────────────────────────────────┐
│ • Add new features                                           │
│ • Fix bugs                                                   │
│ • Update documentation                                       │
│ • Scale if needed                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Success Checklist

```
✅ Backend deployed and accessible
✅ Frontend deployed and accessible
✅ Services connected (CORS configured)
✅ Environment variables set
✅ HTTPS enabled (automatic)
✅ Configuration page works
✅ Session initialization works
✅ Scanner page loads
✅ Camera access works
✅ QR scanning records attendance
✅ Manual entry works
✅ Toast notifications appear
✅ Cooldown prevents duplicates
✅ Works on mobile devices
✅ No errors in logs
✅ TAs have access
✅ Documentation shared
```

---

## Quick Reference

### Render Commands
```bash
# View logs
render logs <service-name>

# Restart service
render restart <service-name>

# Deploy manually
render deploy <service-name>
```

### Git Commands
```bash
# Commit changes
git add .
git commit -m "Update"
git push

# Check status
git status

# View history
git log --oneline
```

### Testing URLs
```bash
# Test backend
curl https://backend-url.onrender.com/health

# Test service account
curl https://backend-url.onrender.com/api/service-account-email
```

---

## Time Estimates

| Task | Time |
|------|------|
| Prepare repository | 2 min |
| Push to GitHub | 2 min |
| Deploy backend | 3 min |
| Deploy frontend | 2 min |
| Connect services | 2 min |
| Test deployment | 2 min |
| **Total** | **~15 min** |

---

## Cost Breakdown

| Platform | Backend | Frontend | Total |
|----------|---------|----------|-------|
| Render | Free | Free | $0/mo |
| Railway | $2-3 | Free | $2-3/mo |
| Vercel + Render | Free | Free | $0/mo |

---

**Ready to deploy? Start with START_HERE.md or DEPLOY_NOW.md!**
