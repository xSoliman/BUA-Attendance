# 🚀 Deploy Now - Quick Start

## Fastest Way to Deploy (5 minutes)

### Option 1: One-Click Deploy to Render ⚡

1. **Push to GitHub** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/qr-attendance.git
git push -u origin main
```

2. **Click this button** (after pushing to GitHub):

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

3. **Connect your GitHub repo** and configure:
   - Add `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable
   - Wait 2-3 minutes for deployment
   - Done! 🎉

### Option 2: Manual Deploy to Render (10 minutes)

#### Backend:
1. Go to [render.com](https://render.com) → Sign up
2. New → Web Service → Connect GitHub repo
3. Settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variable**: 
     - Key: `GOOGLE_SERVICE_ACCOUNT_JSON`
     - Value: (paste your JSON from backend/.env)

4. Create Web Service → Copy URL

#### Frontend:
1. Render → New → Static Site → Same repo
2. Settings:
   - **Root Directory**: `frontend`
   - **Publish Directory**: `.`
3. Create Static Site → Copy URL

#### Update Configuration:
1. Edit `frontend/app.js` line 4:
```javascript
const API_BASE_URL = 'https://YOUR-BACKEND-URL.onrender.com/api';
```

2. Add to backend environment variables:
   - Key: `FRONTEND_ORIGIN`
   - Value: `https://YOUR-FRONTEND-URL.onrender.com`

3. Push changes:
```bash
git add frontend/app.js
git commit -m "Update API URL"
git push
```

### Option 3: Deploy to Railway (Alternative)

1. Go to [railway.app](https://railway.app) → Sign up
2. New Project → Deploy from GitHub
3. Select your repo
4. Configure backend:
   - Add `GOOGLE_SERVICE_ACCOUNT_JSON` variable
   - Generate domain
5. Update `frontend/app.js` with backend URL
6. Push changes

---

## After Deployment

### Test Your App:
1. Visit your frontend URL
2. Enter your Spreadsheet ID
3. Select course and week
4. Start scanning!

### Share with TAs:
Send them:
- Frontend URL
- Instructions to allow camera access
- Spreadsheet ID (if needed)

### Keep It Awake (Render Free Tier):
Use [UptimeRobot](https://uptimerobot.com) to ping your backend every 5 minutes to prevent cold starts.

---

## Troubleshooting

**Backend not starting?**
- Check logs in Render dashboard
- Verify `GOOGLE_SERVICE_ACCOUNT_JSON` is set

**Frontend can't connect?**
- Check `API_BASE_URL` in `frontend/app.js`
- Verify CORS settings (FRONTEND_ORIGIN)

**Camera not working?**
- Ensure using HTTPS (all free hosts provide this)
- Allow camera permissions in browser

---

## Cost: $0/month 💰

All recommended platforms offer free tiers sufficient for this project!

---

## Need Help?

Check `FREE_DEPLOYMENT_GUIDE.md` for detailed instructions.
