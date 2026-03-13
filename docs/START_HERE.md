# 🚀 Start Here - Free Hosting Guide

Welcome! This guide will help you deploy your QR Attendance System for free.

---

## 📚 Documentation Overview

I've created several guides to help you:

### Quick Start (Choose One):
1. **DEPLOY_NOW.md** - Fastest way to deploy (5-10 minutes)
2. **FREE_DEPLOYMENT_GUIDE.md** - Detailed step-by-step guide
3. **DEPLOYMENT_SUMMARY.md** - Compare all hosting options

### Helper Files:
- **DEPLOYMENT_CHECKLIST.md** - Complete checklist for deployment
- **deploy.sh** - Automated deployment helper script
- **render.yaml** - Render.com configuration
- **vercel.json** - Vercel configuration

---

## ⚡ Quickest Path to Deployment

### 1. Prepare Your Code (2 minutes)
```bash
# Run the deployment helper
./deploy.sh

# Or manually:
git init
git add .
git commit -m "Ready for deployment"
```

### 2. Push to GitHub (2 minutes)
```bash
# Create repo at: https://github.com/new
git remote add origin https://github.com/YOUR_USERNAME/qr-attendance.git
git branch -M main
git push -u origin main
```

### 3. Deploy to Render (5 minutes)

**Backend:**
1. Go to [render.com](https://render.com) → Sign up
2. New → Web Service → Connect your repo
3. Settings:
   - Root: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variable:
   - Key: `GOOGLE_SERVICE_ACCOUNT_JSON`
   - Value: (paste from backend/.env)
5. Deploy → Copy URL

**Frontend:**
1. Render → New → Static Site → Same repo
2. Settings:
   - Root: `frontend`
   - Publish: `.`
3. Deploy → Copy URL

### 4. Connect Them (2 minutes)
1. Edit `frontend/app.js` line 4:
```javascript
const API_BASE_URL = 'https://YOUR-BACKEND.onrender.com/api';
```

2. Add to backend env vars:
   - `FRONTEND_ORIGIN` = `https://YOUR-FRONTEND.onrender.com`

3. Push:
```bash
git add frontend/app.js
git commit -m "Update API URL"
git push
```

### 5. Test! (1 minute)
Visit your frontend URL and test the complete flow.

**Total Time: ~10 minutes**  
**Total Cost: $0/month**

---

## 🎯 Recommended Hosting

### Best Overall: Render.com
- ✅ Completely free
- ✅ Easiest setup
- ✅ Automatic HTTPS
- ✅ Auto-deploy from GitHub
- ⚠️ Cold starts (30s after 15 min idle)

**Solution for cold starts**: Use [UptimeRobot](https://uptimerobot.com) (free) to ping every 5 minutes

### Best Performance: Railway.app
- ✅ No cold starts
- ✅ Better performance
- ✅ $5 free credit/month
- ⚠️ ~$2-3/month after free credit

### Best Frontend: Vercel + Render
- ✅ Vercel: Unlimited free frontend
- ✅ Render: Free backend
- ✅ Best performance
- ⚠️ Two platforms to manage

---

## 📋 Pre-Deployment Checklist

Before you start:
- [ ] System works locally (test at http://localhost:3000)
- [ ] Service Account JSON ready
- [ ] Google Sheet prepared with correct format
- [ ] Service Account added as Editor to sheet
- [ ] Git installed
- [ ] GitHub account created

---

## 🔧 What's Included

### Backend (Python/FastAPI):
- Google Sheets integration
- Attendance recording API
- Service Account authentication
- CORS configuration
- Error handling

### Frontend (HTML/JS):
- Configuration page
- Session initialization
- QR code scanner
- Manual entry
- Toast notifications
- Cooldown management

### Deployment Files:
- `.gitignore` - Protects sensitive files
- `render.yaml` - Render configuration
- `vercel.json` - Vercel configuration
- `deploy.sh` - Helper script

---

## 📖 Detailed Guides

### For Step-by-Step Instructions:
Read **FREE_DEPLOYMENT_GUIDE.md**

### For Quick Deployment:
Read **DEPLOY_NOW.md**

### To Compare Options:
Read **DEPLOYMENT_SUMMARY.md**

### For Complete Checklist:
Read **DEPLOYMENT_CHECKLIST.md**

---

## 🆘 Need Help?

### Common Issues:

**"Backend not starting"**
→ Check Render logs, verify environment variables

**"Frontend can't connect to backend"**
→ Check API_BASE_URL in frontend/app.js, verify CORS

**"Camera not working"**
→ Ensure HTTPS is enabled, allow camera permissions

**"Student Not Found"**
→ Verify Service Account has Editor access to sheet

### Documentation:
- `README.md` - Project overview
- `QUICKSTART.md` - Local setup guide
- `TROUBLESHOOTING.md` - Common issues
- `ARCHITECTURE_INTEGRATION.md` - System architecture

---

## 💰 Cost

All recommended options are **FREE**:
- Render: $0/month (free tier)
- Railway: Free for first month, then ~$2-3/month
- Vercel: $0/month (unlimited)

---

## 🎉 After Deployment

### Share with TAs:
1. Frontend URL
2. Instructions for camera access
3. Spreadsheet ID (if needed)

### Monitor:
- Check Render dashboard for logs
- Set up UptimeRobot to prevent cold starts
- Monitor Google Sheets API usage

### Maintain:
- Update dependencies periodically
- Keep Service Account secure
- Backup configuration

---

## 🚀 Ready to Deploy?

### Option 1: Use Helper Script
```bash
./deploy.sh
```

### Option 2: Follow Quick Guide
```bash
cat DEPLOY_NOW.md
```

### Option 3: Read Detailed Guide
```bash
cat FREE_DEPLOYMENT_GUIDE.md
```

---

## ✨ Success!

Once deployed, your QR Attendance System will be:
- ✅ Accessible from anywhere
- ✅ Secure with HTTPS
- ✅ Working on mobile devices
- ✅ Free to host
- ✅ Auto-deploying from GitHub

**Good luck with your deployment! 🎊**

---

## Quick Links

- [Render.com](https://render.com) - Recommended hosting
- [Railway.app](https://railway.app) - Alternative hosting
- [Vercel.com](https://vercel.com) - Frontend hosting
- [UptimeRobot](https://uptimerobot.com) - Prevent cold starts
- [GitHub](https://github.com) - Code hosting

---

**Questions?** Check the documentation files or hosting platform support.
