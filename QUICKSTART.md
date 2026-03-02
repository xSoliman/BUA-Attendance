# Quick Start Guide for TAs

This guide will get you up and running with the QR Attendance System in 5 minutes.

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Google Sheet with student data prepared
- [ ] Service Account created and JSON key downloaded
- [ ] Service Account email added as Editor to your Google Sheet

## 5-Minute Setup

### Step 1: Configure Backend (2 minutes)

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env and paste your Service Account JSON
nano .env  # or use any text editor
```

In the `.env` file, paste your entire Service Account JSON:
```env
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
```

### Step 2: Start the Server (1 minute)

```bash
# Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Keep this terminal open!

### Step 3: Start Frontend (1 minute)

Open a new terminal:

```bash
# Serve frontend
cd frontend
python -m http.server 3000
```

### Step 4: Configure Your Sheet (1 minute)

1. Open `http://localhost:3000` on your phone or computer
2. Get your Spreadsheet ID from the Google Sheet URL:
   ```
   https://docs.google.com/spreadsheets/d/[COPY_THIS_PART]/edit
   ```
3. Paste it in the configuration page
4. Click "Save Configuration"

## First Attendance Session

1. **Select Course**: Choose your course sheet (e.g., "CS101")
2. **Select Week**: Choose the attendance column (e.g., "Week 1")
3. **Start Scanner**: Click the button and allow camera access
4. **Scan Students**: Point camera at QR codes
5. **Done!**: Green notification = attendance recorded

## Common Issues

### "Cannot access spreadsheet"
→ Make sure you shared the sheet with the service account email (shown on config page)

### Camera not working
→ Use Chrome browser and allow camera permissions

### "Student Not Found"
→ Check that Student IDs in QR codes match IDs in your sheet exactly

## Need Help?

See the full [README.md](README.md) for detailed instructions and troubleshooting.

## Sheet Format Reminder

Your Google Sheet should look like this:

| ID       | Name          | Email           | Week 1 | Week 2 | Week 3 |
|----------|---------------|-----------------|--------|--------|--------|
| 20210001 | Ahmed Mohamed | ahmed@email.com |        |        |        |
| 20210002 | Sara Ali      | sara@email.com  |        |        |        |

- ID column must be in columns A, B, or C
- Header must be "ID" or "رقم الجلوس"
- Attendance columns start from column D

## Generating QR Codes

```bash
cd qr_generator
pip install -r requirements.txt
python generate_qr.py students.csv
```

QR codes will be in the `output/` folder. Print and distribute to students!

---

**Pro Tip**: Bookmark `http://localhost:3000` on your phone for quick access during lab sessions.
