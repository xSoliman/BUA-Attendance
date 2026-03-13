# Free Deployment Guide

This guide will help you deploy the QR Attendance System for free using popular hosting platforms.

## Recommended Free Hosting Options

### Option 1: Render.com (Recommended - Easiest)
- **Backend**: Free tier with 750 hours/month
- **Frontend**: Free static site hosting
- **Setup Time**: ~10 minutes
- **Pros**: Easy setup, automatic HTTPS, good performance
- **Cons**: Spins down after 15 min of inactivity (cold start ~30s)

### Option 2: Railway.app
- **Backend**: $5 free credit/month (enough for small usage)
- **Frontend**: Free static hosting
- **Setup Time**: ~10 minutes
- **Pros**: No cold starts, better performance
- **Cons**: Limited free credit

### Option 3: Vercel (Frontend) + Render (Backend)
- **Backend**: Render free tier
- **Frontend**: Vercel unlimited free hosting
- **Setup Time**: ~15 minutes
- **Pros**: Best frontend performance, unlimited bandwidth
- **Cons**: Two separate platforms

---

## Option 1: Deploy on Render.com (Recommended)

### Step 1: Prepare Your Repository

1. **Initialize Git** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit"
```

2. **Create a GitHub repository** and push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/qr-attendance-system.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Backend on Render

1. Go to [render.com](https://render.com) and sign up (free)

2. Click **"New +"** → **"Web Service"**

3. Connect your GitHub repository

4. Configure the service:
   - **Name**: `qr-attendance-backend`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

5. **Add Environment Variables**:
   Click "Advanced" → "Add Environment Variable":
   - Key: `GOOGLE_SERVICE_ACCOUNT_JSON`
   - Value: (paste your entire JSON from .env file)

6. Click **"Create Web Service"**

7. Wait for deployment (~2-3 minutes)

8. **Copy your backend URL**: `https://qr-attendance-backend.onrender.com`

### Step 3: Deploy Frontend on Render

1. Click **"New +"** → **"Static Site"**

2. Connect the same GitHub repository

3. Configure:
   - **Name**: `qr-attendance-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: (leave empty)
   - **Publish Directory**: `.`

4. Click **"Create Static Site"**

5. **Copy your frontend URL**: `https://qr-attendance-frontend.onrender.com`

### Step 4: Update CORS Settings

1. Go back to your backend service on Render

2. Add another environment variable:
   - Key: `FRONTEND_ORIGIN`
   - Value: `https://qr-attendance-frontend.onrender.com`

3. The service will automatically redeploy

### Step 5: Update Frontend API URL

You need to update the frontend to point to your deployed backend:

1. Edit `frontend/app.js` line 4:
```javascript
const API_BASE_URL = 'https://qr-attendance-backend.onrender.com/api';
```

2. Commit and push:
```bash
git add frontend/app.js
git commit -m "Update API URL for production"
git push
```

3. Render will automatically redeploy your frontend

### Step 6: Test Your Deployment

1. Visit your frontend URL: `https://qr-attendance-frontend.onrender.com`
2. Configure your spreadsheet
3. Start scanning!

---

## Option 2: Deploy on Railway.app

### Step 1: Prepare Repository (same as Option 1)

### Step 2: Deploy on Railway

1. Go to [railway.app](https://railway.app) and sign up

2. Click **"New Project"** → **"Deploy from GitHub repo"**

3. Select your repository

4. Railway will detect both backend and frontend

5. **Configure Backend**:
   - Click on the backend service
   - Go to "Variables" tab
   - Add: `GOOGLE_SERVICE_ACCOUNT_JSON` with your JSON
   - Go to "Settings" tab
   - Set "Start Command": `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Generate domain (click "Generate Domain")

6. **Configure Frontend**:
   - Click on the frontend service
   - Go to "Settings" tab
   - Set "Start Command": `cd frontend && python -m http.server $PORT`
   - Generate domain

7. Update `frontend/app.js` with your backend URL

8. Push changes to trigger redeployment

---

## Option 3: Vercel (Frontend) + Render (Backend)

### Backend: Follow Render steps above

### Frontend on Vercel:

1. Go to [vercel.com](https://vercel.com) and sign up

2. Click **"Add New..."** → **"Project"**

3. Import your GitHub repository

4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: (leave empty)
   - **Output Directory**: `.`

5. Click **"Deploy"**

6. Update `frontend/app.js` with your Render backend URL

7. Redeploy

---

## Important Notes

### Cold Starts (Render Free Tier)
- Free tier spins down after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- Solution: Use a service like [UptimeRobot](https://uptimerobot.com) to ping your backend every 5 minutes

### HTTPS and Camera Access
- All free hosting platforms provide HTTPS automatically
- Camera access requires HTTPS, so local HTTP won't work on phones
- Your deployed app will work perfectly on mobile devices

### Environment Variables Security
- Never commit `.env` file to GitHub
- Add `.env` to `.gitignore`
- Set environment variables in hosting platform dashboard

### Custom Domain (Optional)
- Render: Free custom domain support
- Vercel: Free custom domain support
- Railway: Free custom domain support

---

## Post-Deployment Checklist

- [ ] Backend is accessible at your URL
- [ ] Frontend is accessible at your URL
- [ ] Service account email is displayed on config page
- [ ] Spreadsheet validation works
- [ ] Can select course and week
- [ ] Camera access works on mobile
- [ ] Attendance recording works
- [ ] Toast notifications appear
- [ ] Cooldown prevents duplicates

---

## Troubleshooting

### Backend not starting
- Check logs in hosting platform dashboard
- Verify `GOOGLE_SERVICE_ACCOUNT_JSON` is set correctly
- Ensure `requirements.txt` includes all dependencies

### Frontend can't connect to backend
- Check CORS settings (FRONTEND_ORIGIN environment variable)
- Verify API_BASE_URL in `frontend/app.js` is correct
- Check browser console for errors

### Camera not working
- Ensure you're using HTTPS (not HTTP)
- Check browser permissions
- Try different browser (Chrome recommended)

---

## Cost Estimate

### Render Free Tier
- Backend: Free (750 hours/month)
- Frontend: Free (unlimited)
- **Total: $0/month**

### Railway
- Backend + Frontend: $5 credit/month
- Typical usage: ~$2-3/month
- **Total: Free for first month, then ~$2-3/month**

### Vercel + Render
- Backend: Free (Render)
- Frontend: Free (Vercel)
- **Total: $0/month**

---

## Recommended Setup for Production

For best performance and reliability:

1. **Use Vercel for Frontend** (best performance, no cold starts)
2. **Use Render for Backend** (free tier is sufficient)
3. **Set up UptimeRobot** to prevent cold starts
4. **Use custom domain** for professional look

---

## Need Help?

- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs

