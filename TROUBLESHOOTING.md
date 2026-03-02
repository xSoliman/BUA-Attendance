# Troubleshooting Guide

Comprehensive solutions for common issues with the QR Attendance System.

## Table of Contents

- [Setup Issues](#setup-issues)
- [Google Sheets Issues](#google-sheets-issues)
- [Camera and Scanning Issues](#camera-and-scanning-issues)
- [Backend Issues](#backend-issues)
- [Frontend Issues](#frontend-issues)
- [QR Code Generator Issues](#qr-code-generator-issues)

## Setup Issues

### Python Dependencies Won't Install

**Symptoms**: `pip install` fails with errors

**Solutions**:

1. **Update pip**:
   ```bash
   pip install --upgrade pip
   ```

2. **Use virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Check Python version**:
   ```bash
   python --version  # Should be 3.8 or higher
   ```

### Service Account JSON Invalid

**Symptoms**: "Invalid credentials" or "Authentication failed"

**Solutions**:

1. **Verify JSON format**: Ensure the entire JSON is on one line in `.env`:
   ```env
   GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
   ```

2. **Check for extra quotes**: Don't add extra quotes around the JSON

3. **Validate JSON**: Use a JSON validator to check the file

4. **Re-download key**: If corrupted, create a new key from Google Cloud Console

## Google Sheets Issues

### "Cannot access spreadsheet" Error

**Symptoms**: Validation fails when entering Spreadsheet ID

**Solutions**:

1. **Check sharing permissions**:
   - Open your Google Sheet
   - Click "Share"
   - Verify the service account email is listed as an Editor
   - Service account email format: `name@project-id.iam.gserviceaccount.com`

2. **Verify Spreadsheet ID**:
   - URL format: `https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit`
   - Copy only the ID part (between `/d/` and `/edit`)
   - Should be 44 characters long

3. **Check API is enabled**:
   - Go to Google Cloud Console
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google Sheets API"
   - Ensure it's enabled

4. **Test with a simple sheet**:
   - Create a new test sheet
   - Share it with the service account
   - Try accessing it to isolate the issue

### "Student Not Found" for Valid Students

**Symptoms**: QR code scans successfully but shows "Student Not Found"

**Solutions**:

1. **Check ID column header**:
   - Must be exactly "ID" or "رقم الجلوس" (case-insensitive)
   - No extra spaces or special characters
   - Must be in columns A, B, or C

2. **Verify Student ID format**:
   - IDs in sheet must match QR code exactly
   - Check for leading/trailing spaces
   - Check for different number formats (text vs number)

3. **Check for hidden characters**:
   ```
   In Google Sheets:
   - Select the ID column
   - Format → Number → Plain text
   ```

4. **Test with manual entry**:
   - Type the Student ID manually
   - If it works, the QR code might have extra characters

### Rate Limit Errors

**Symptoms**: "Rate limit exceeded" or "Quota exceeded"

**Solutions**:

1. **Wait and retry**: Google Sheets API has quotas
   - 100 requests per 100 seconds per user
   - System automatically retries after 2 seconds

2. **Reduce scan frequency**: If scanning very rapidly, slow down slightly

3. **Check quota usage**:
   - Google Cloud Console → "APIs & Services" → "Dashboard"
   - View quota usage for Google Sheets API

4. **Request quota increase**: For high-volume usage, request increase from Google

### Wrong Column Being Updated

**Symptoms**: Attendance marked in wrong week/column

**Solutions**:

1. **Verify column selection**: Check the session info displayed in scanner

2. **Check column headers**: Ensure attendance columns start from column D

3. **Restart session**: Click "Change Session" and reselect the correct column

4. **Check for merged cells**: Unmerge any merged cells in the header row

## Camera and Scanning Issues

### Camera Won't Start

**Symptoms**: Black screen or "Camera access denied"

**Solutions**:

1. **Grant permissions**:
   - **Chrome**: Click the camera icon in address bar → Allow
   - **Safari**: Settings → Safari → Camera → Allow
   - **Firefox**: Click the camera icon in address bar → Allow

2. **Use HTTPS or localhost**:
   - Browsers require secure context for camera
   - `http://localhost` works
   - For remote access, use HTTPS

3. **Check camera availability**:
   - Close other apps using the camera
   - Try a different browser
   - Restart the browser

4. **Test camera**:
   - Visit a camera test website to verify camera works
   - Check system camera permissions

### QR Code Won't Scan

**Symptoms**: Camera works but QR code not detected

**Solutions**:

1. **Improve lighting**: Ensure good lighting on the QR code

2. **Adjust distance**: Hold QR code 10-30cm from camera

3. **Check QR code quality**:
   - Ensure it's not blurry or damaged
   - Print at adequate size (minimum 5cm x 5cm)
   - Avoid glossy paper that reflects light

4. **Clean camera lens**: Wipe phone camera lens

5. **Try manual entry**: Type the Student ID as a workaround

### Scanner Freezes or Lags

**Symptoms**: Scanner becomes unresponsive

**Solutions**:

1. **Refresh the page**: Reload the scanner page

2. **Clear browser cache**:
   - Chrome: Settings → Privacy → Clear browsing data
   - Select "Cached images and files"

3. **Close other tabs**: Free up browser resources

4. **Restart browser**: Complete browser restart

5. **Check device performance**: Close other apps on your phone

## Backend Issues

### Backend Won't Start

**Symptoms**: `uvicorn` command fails or exits immediately

**Solutions**:

1. **Check for port conflicts**:
   ```bash
   # Check if port 8000 is in use
   lsof -i :8000  # On Mac/Linux
   netstat -ano | findstr :8000  # On Windows
   ```

2. **Use different port**:
   ```bash
   uvicorn main:app --port 8001
   ```

3. **Check for syntax errors**:
   ```bash
   python -m py_compile backend/main.py
   ```

4. **Verify environment variables**:
   ```bash
   # Check .env file exists and is readable
   cat backend/.env
   ```

5. **Check Python path**:
   ```bash
   # Ensure backend modules can be imported
   cd backend
   python -c "import sheets_auth"
   ```

### "Module not found" Errors

**Symptoms**: Import errors when starting backend

**Solutions**:

1. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Check Python path**:
   ```bash
   # Run from project root, not backend directory
   cd /path/to/qr-attendance-system
   uvicorn backend.main:app
   ```

3. **Use absolute imports**: Ensure imports use `backend.` prefix

### API Returns 500 Errors

**Symptoms**: Backend starts but API calls fail

**Solutions**:

1. **Check logs**: Look at terminal where uvicorn is running

2. **Test endpoints**:
   ```bash
   # Test health endpoint
   curl http://localhost:8000/health
   
   # Test service account email
   curl http://localhost:8000/api/service-account-email
   ```

3. **Verify credentials**: Ensure service account JSON is valid

4. **Check Google Sheets API**: Verify API is enabled in Google Cloud

## Frontend Issues

### Frontend Won't Load

**Symptoms**: Blank page or "Cannot connect"

**Solutions**:

1. **Check server is running**:
   ```bash
   # Should see "Serving HTTP on 0.0.0.0 port 3000"
   ```

2. **Verify URL**: Use `http://localhost:3000` not `http://127.0.0.1:3000`

3. **Check browser console**: Press F12 and look for errors

4. **Clear browser cache**: Hard refresh with Ctrl+Shift+R (Cmd+Shift+R on Mac)

### "Cannot connect to backend" Error

**Symptoms**: Frontend loads but API calls fail

**Solutions**:

1. **Verify backend is running**: Check `http://localhost:8000/health`

2. **Check CORS configuration**:
   - Ensure frontend URL is in `backend/main.py` origins list
   - Default includes `http://localhost:3000`

3. **Check API URL**: Verify frontend is calling correct backend URL

4. **Test with curl**:
   ```bash
   curl http://localhost:8000/api/service-account-email
   ```

### Configuration Not Saving

**Symptoms**: Spreadsheet ID not persisting between sessions

**Solutions**:

1. **Check localStorage**: Browser may have localStorage disabled
   - Open browser console (F12)
   - Type: `localStorage.getItem('qr-attendance-config')`

2. **Enable cookies and site data**: Check browser privacy settings

3. **Try different browser**: Some privacy modes block localStorage

4. **Clear and retry**:
   ```javascript
   // In browser console
   localStorage.clear()
   // Then reconfigure
   ```

### Toast Notifications Not Showing

**Symptoms**: No visual feedback after scanning

**Solutions**:

1. **Check browser console**: Look for JavaScript errors

2. **Verify CSS loaded**: Check that `styles.css` is loading

3. **Test manually**:
   ```javascript
   // In browser console
   showToast('Test message', 'success')
   ```

## QR Code Generator Issues

### "CSV file not found" Error

**Symptoms**: Script can't find the CSV file

**Solutions**:

1. **Use full path**:
   ```bash
   python generate_qr.py /full/path/to/students.csv
   ```

2. **Check current directory**:
   ```bash
   ls students.csv  # Should show the file
   ```

3. **Verify file name**: Check for typos or extra extensions

### "Missing required columns" Error

**Symptoms**: CSV validation fails

**Solutions**:

1. **Check CSV headers**: First row must be exactly:
   ```csv
   Student_ID,Name
   ```

2. **No extra spaces**: Headers should not have leading/trailing spaces

3. **Check encoding**: Save CSV as UTF-8

4. **Verify format**:
   ```csv
   Student_ID,Name
   20210001,Ahmed Mohamed
   20210002,Sara Ali
   ```

### Generated QR Codes Won't Scan

**Symptoms**: QR codes generated but won't scan in app

**Solutions**:

1. **Check QR code content**:
   - Use a QR code reader app to verify content
   - Should contain only the Student ID

2. **Increase print size**: Print larger (minimum 5cm x 5cm)

3. **Check print quality**: Use high-quality printer settings

4. **Test before printing all**: Generate and test one QR code first

### Font Errors in QR Generator

**Symptoms**: "Font not found" warnings

**Solutions**:

1. **Install fonts** (Linux):
   ```bash
   sudo apt-get install fonts-dejavu
   ```

2. **Use default font**: Script falls back to default if custom fonts unavailable

3. **Specify font path**: Edit `generate_qr.py` to use available font

## General Debugging Tips

### Enable Debug Mode

**Backend**:
```bash
# Add to .env
DEBUG=True

# Run with reload
uvicorn main:app --reload --log-level debug
```

**Frontend**:
```javascript
// In browser console
localStorage.setItem('debug', 'true')
```

### Check Logs

**Backend logs**: Look at terminal where uvicorn is running

**Frontend logs**: Open browser console (F12) → Console tab

**Google Sheets API logs**: Google Cloud Console → Logging

### Test Individual Components

1. **Test backend only**:
   ```bash
   curl http://localhost:8000/api/service-account-email
   ```

2. **Test Google Sheets access**:
   ```python
   from backend.sheets_auth import get_client
   client = get_client()
   print("Success!")
   ```

3. **Test QR generation**:
   ```python
   from qr_generator.generate_qr import generate_qr_code
   img = generate_qr_code("20210001")
   img.save("test.png")
   ```

## Still Having Issues?

1. **Check the README**: Review setup instructions carefully
2. **Verify all prerequisites**: Ensure all requirements are met
3. **Test with minimal setup**: Use a simple test sheet with few students
4. **Check browser compatibility**: Use Chrome for best compatibility
5. **Review error messages**: Read error messages carefully for clues

## Getting Help

When reporting issues, include:

- Operating system and version
- Python version (`python --version`)
- Browser and version
- Exact error message
- Steps to reproduce
- What you've already tried

---

**Remember**: Most issues are related to Google Sheets permissions or Service Account configuration. Double-check these first!
