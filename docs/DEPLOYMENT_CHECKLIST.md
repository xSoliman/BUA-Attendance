# ✅ Deployment Checklist

Use this checklist to ensure smooth deployment of your QR Attendance System.

---

## Pre-Deployment

### Code Preparation
- [ ] All code is tested locally
- [ ] Backend runs without errors
- [ ] Frontend connects to backend successfully
- [ ] Attendance recording works
- [ ] Camera access works on mobile

### Git Setup
- [ ] Git repository initialized (`git init`)
- [ ] `.gitignore` file exists
- [ ] `.env` file is in `.gitignore`
- [ ] `.env` file is NOT committed
- [ ] All changes are committed
- [ ] GitHub repository created
- [ ] Code pushed to GitHub

### Service Account
- [ ] Google Service Account created
- [ ] Service Account JSON key downloaded
- [ ] JSON key saved securely (not in git)
- [ ] Service Account email noted down
- [ ] Google Sheets API enabled

### Google Sheet
- [ ] Test spreadsheet created
- [ ] Sheet has correct format (ID, Name, Email, Week columns)
- [ ] Service Account added as Editor to sheet
- [ ] Spreadsheet ID copied

---

## Deployment (Render.com)

### Backend Deployment
- [ ] Logged into Render.com
- [ ] New Web Service created
- [ ] GitHub repository connected
- [ ] Root directory set to `backend`
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Environment variable `GOOGLE_SERVICE_ACCOUNT_JSON` added
- [ ] Service deployed successfully
- [ ] Backend URL copied
- [ ] Health check passes (`/health` endpoint)

### Frontend Deployment
- [ ] New Static Site created on Render
- [ ] Same GitHub repository connected
- [ ] Root directory set to `frontend`
- [ ] Publish directory set to `.`
- [ ] Site deployed successfully
- [ ] Frontend URL copied

### Configuration
- [ ] `frontend/app.js` updated with backend URL
- [ ] Backend environment variable `FRONTEND_ORIGIN` added
- [ ] Changes committed and pushed
- [ ] Auto-deployment triggered
- [ ] Both services redeployed successfully

---

## Testing

### Backend Tests
- [ ] Backend URL accessible
- [ ] `/` endpoint returns API info
- [ ] `/health` endpoint returns healthy status
- [ ] `/api/service-account-email` returns correct email
- [ ] No errors in Render logs

### Frontend Tests
- [ ] Frontend URL accessible
- [ ] Page loads without errors
- [ ] Service Account email displays on config page
- [ ] Can enter Spreadsheet ID
- [ ] Validation works (with test spreadsheet)
- [ ] Can navigate to session page

### Integration Tests
- [ ] Can select course sheet
- [ ] Can select attendance column
- [ ] Can start scanner
- [ ] Camera access prompt appears
- [ ] Camera feed displays
- [ ] QR code scanning works
- [ ] Manual entry works
- [ ] Attendance records to sheet
- [ ] Toast notifications appear
- [ ] Cooldown prevents duplicates
- [ ] "Student Not Found" works correctly

### Mobile Tests
- [ ] Frontend accessible on mobile
- [ ] HTTPS works (required for camera)
- [ ] Camera permission prompt appears
- [ ] Camera feed displays correctly
- [ ] QR scanning works on mobile
- [ ] Touch targets are large enough
- [ ] Manual entry keyboard works
- [ ] Notifications are visible

---

## Post-Deployment

### Documentation
- [ ] Frontend URL shared with TAs
- [ ] Instructions provided for camera access
- [ ] Spreadsheet ID shared (if needed)
- [ ] Service Account email shared
- [ ] Quick start guide provided

### Monitoring Setup
- [ ] UptimeRobot monitor created (optional)
- [ ] Ping interval set to 5 minutes
- [ ] Email alerts configured
- [ ] Render dashboard bookmarked

### Security
- [ ] `.env` file not in GitHub
- [ ] Service Account JSON secure
- [ ] Only necessary people have access
- [ ] CORS properly configured
- [ ] HTTPS enforced

### Backup
- [ ] Service Account JSON backed up securely
- [ ] Spreadsheet ID documented
- [ ] Deployment URLs documented
- [ ] Environment variables documented

---

## Optional Enhancements

### Performance
- [ ] UptimeRobot configured to prevent cold starts
- [ ] CDN configured (if using custom domain)
- [ ] Caching headers optimized

### Custom Domain
- [ ] Domain purchased (optional)
- [ ] DNS configured
- [ ] SSL certificate issued
- [ ] Domain connected to Render

### Analytics
- [ ] Usage tracking added (optional)
- [ ] Error monitoring configured
- [ ] Performance monitoring enabled

---

## Troubleshooting Checklist

If something doesn't work:

### Backend Issues
- [ ] Check Render logs for errors
- [ ] Verify environment variables are set
- [ ] Test `/health` endpoint
- [ ] Check Service Account JSON format
- [ ] Verify Google Sheets API is enabled

### Frontend Issues
- [ ] Check browser console for errors
- [ ] Verify API_BASE_URL is correct
- [ ] Test backend URL directly
- [ ] Check CORS configuration
- [ ] Clear browser cache

### Camera Issues
- [ ] Verify HTTPS is enabled
- [ ] Check browser permissions
- [ ] Try different browser (Chrome recommended)
- [ ] Test on different device
- [ ] Check camera hardware

### Attendance Recording Issues
- [ ] Verify Service Account has Editor access
- [ ] Check Spreadsheet ID is correct
- [ ] Verify sheet name matches
- [ ] Check column names are correct
- [ ] Test with known Student ID

---

## Success Criteria

Your deployment is successful when:

✅ Backend is accessible and healthy  
✅ Frontend loads without errors  
✅ Configuration page works  
✅ Session initialization works  
✅ Scanner page loads  
✅ Camera access works  
✅ QR scanning records attendance  
✅ Manual entry works  
✅ Toast notifications appear  
✅ Cooldown prevents duplicates  
✅ Works on mobile devices  
✅ HTTPS is enabled  
✅ No errors in logs  

---

## Maintenance Schedule

### Daily
- [ ] Check for errors in Render logs
- [ ] Monitor uptime status

### Weekly
- [ ] Review usage statistics
- [ ] Check Google Sheets API quota
- [ ] Test critical functionality

### Monthly
- [ ] Update dependencies if needed
- [ ] Review security settings
- [ ] Backup configuration

---

## Emergency Contacts

**Hosting Platform Support:**
- Render: https://render.com/docs/support
- Railway: https://railway.app/help
- Vercel: https://vercel.com/support

**Google Cloud Support:**
- Console: https://console.cloud.google.com
- Support: https://cloud.google.com/support

---

## Rollback Plan

If deployment fails:

1. **Check logs** in hosting platform
2. **Revert changes** in GitHub
3. **Redeploy** previous working version
4. **Test locally** to identify issue
5. **Fix and redeploy**

---

## Completion

Date deployed: _______________  
Backend URL: _______________  
Frontend URL: _______________  
Deployed by: _______________  

**Congratulations! Your QR Attendance System is live! 🎉**
