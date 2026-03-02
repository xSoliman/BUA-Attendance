# QR Attendance System

A mobile-first web application for Teaching Assistants to record student attendance by scanning QR codes. The system integrates with Google Sheets as a database backend, providing a simple and familiar interface for managing student records.

## Features

- **QR Code Scanning**: Fast camera-based scanning optimized for mobile devices
- **Google Sheets Integration**: Use your existing spreadsheets as the database
- **Mobile-Optimized UI**: Responsive design for smartphone usage in lab environments
- **Real-time Feedback**: Instant visual notifications for attendance recording
- **Duplicate Prevention**: 30-second cooldown to prevent accidental double-scans
- **Manual Entry**: Fallback option when QR codes are damaged or unreadable
- **Multi-Session Support**: Easily switch between courses and weeks
- **Offline-Ready**: Asynchronous operations maintain UI responsiveness

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [1. Google Cloud Service Account Setup](#1-google-cloud-service-account-setup)
  - [2. Backend Configuration](#2-backend-configuration)
  - [3. Running the Application](#3-running-the-application)
- [Usage Guide for TAs](#usage-guide-for-tas)
  - [First-Time Configuration](#first-time-configuration)
  - [Starting an Attendance Session](#starting-an-attendance-session)
  - [Scanning QR Codes](#scanning-qr-codes)
  - [Changing Sessions](#changing-sessions)
- [QR Code Generator](#qr-code-generator)
- [Google Sheets Format](#google-sheets-format)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account
- Google Sheets with student data
- Modern web browser with camera access (Chrome, Safari, or Firefox)

## Setup Instructions

### 1. Google Cloud Service Account Setup

The application uses a Google Service Account to access Google Sheets. Follow these steps to create one:

#### Step 1.1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., "QR Attendance System")
4. Click "Create"

#### Step 1.2: Enable Google Sheets API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"

#### Step 1.3: Create Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Enter a name (e.g., "attendance-system")
4. Click "Create and Continue"
5. Skip the optional steps and click "Done"

#### Step 1.4: Generate Service Account Key

1. In the Credentials page, find your service account under "Service Accounts"
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" → "Create new key"
5. Select "JSON" format
6. Click "Create" - a JSON file will be downloaded

**Important**: Keep this JSON file secure! It contains credentials to access your Google Sheets.

#### Step 1.5: Share Google Sheet with Service Account

1. Open the JSON key file you downloaded
2. Copy the `client_email` value (looks like: `attendance-system@project-id.iam.gserviceaccount.com`)
3. Open your Google Sheet
4. Click "Share" button
5. Paste the service account email
6. Give it "Editor" permissions
7. Click "Send"

### 2. Backend Configuration

#### Step 2.1: Install Dependencies

```bash
# Navigate to the backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt
```

#### Step 2.2: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your configuration:

**Option A: Inline JSON credentials (recommended)**
```env
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"your-project-id",...}
```
Paste the entire contents of your downloaded JSON key file as the value.

**Option B: Path to JSON file**
```env
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service-account-key.json
```

3. Configure server settings (optional):
```env
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=http://localhost:3000
```

### 3. Running the Application

#### Step 3.1: Start the Backend Server

```bash
# From the backend directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

You can verify it's running by visiting `http://localhost:8000/health`

#### Step 3.2: Serve the Frontend

The frontend is a static web application. You can serve it using any web server:

**Option A: Using Python's built-in server**
```bash
# From the frontend directory
cd frontend
python -m http.server 3000
```

**Option B: Using Node.js http-server**
```bash
# Install http-server globally (one time)
npm install -g http-server

# From the frontend directory
cd frontend
http-server -p 3000
```

The application will be available at `http://localhost:3000`

## Usage Guide for TAs

### First-Time Configuration

1. **Open the Application**: Navigate to `http://localhost:3000` on your mobile device or computer

2. **Enter Spreadsheet ID**:
   - Open your Google Sheet in a browser
   - Copy the Spreadsheet ID from the URL:
     ```
     https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit
     ```
   - Paste it into the configuration page

3. **Verify Access**:
   - The system will validate that the Service Account has access
   - If you see an error, make sure you've shared the sheet with the service account email (shown on the configuration page)

4. **Save Configuration**:
   - Click "Save Configuration"
   - The Spreadsheet ID will be stored in your browser for future use

### Starting an Attendance Session

1. **Select Course Sheet**:
   - Choose the course from the dropdown (e.g., "CS101", "MATH201")
   - The system will load all sheet tabs from your spreadsheet

2. **Select Attendance Column**:
   - Choose the week/session column (e.g., "Week 1", "Week 2")
   - Only columns from column D onwards are shown (columns A-C are for student info)

3. **Start Scanner**:
   - Click "Start Scanner" button
   - Grant camera permissions when prompted

### Scanning QR Codes

1. **Position QR Code**:
   - Hold the student's QR code in front of your camera
   - The scanner will automatically detect and process it

2. **Visual Feedback**:
   - **Green notification**: "Attendance Recorded" - Success!
   - **Red notification**: "Student Not Found" - Student ID not in the sheet
   - **Yellow notification**: "Already Scanned" - Student scanned within last 30 seconds

3. **Manual Entry** (if QR code is damaged):
   - Type the Student ID in the text field
   - Click "Submit" or press Enter
   - Works exactly like scanning

4. **Continuous Scanning**:
   - The scanner stays active after each scan
   - No need to reset or click anything
   - Just scan the next student

### Changing Sessions

1. **Switch Course or Week**:
   - Click "Change Session" button in the scanner
   - Select new course and/or week
   - Click "Start Scanner" again

2. **Reconfigure Spreadsheet**:
   - Click the settings icon
   - Enter a new Spreadsheet ID
   - Your previous configuration will be replaced

## QR Code Generator

Generate QR codes for your students from a CSV file.

### Preparing the CSV File

Create a CSV file with the following format:

```csv
Student_ID,Name
20210001,Ahmed Mohamed
20210002,Sara Ali
20210003,Omar Hassan
```

**Requirements**:
- Must have headers: `Student_ID` and `Name`
- Student_ID should match the IDs in your Google Sheet
- Save as UTF-8 encoding (especially important for Arabic names)

### Generating QR Codes

1. **Install Dependencies**:
```bash
cd qr_generator
pip install -r requirements.txt
```

2. **Run the Generator**:
```bash
python generate_qr.py students.csv
```

3. **Output**:
   - QR code images will be saved in the `output/` directory
   - Each file is named `{Student_ID}.png`
   - Each image includes:
     - QR code containing the Student_ID
     - Footer with student name and ID for easy identification

### Printing QR Codes

- Print the generated images on card stock
- Recommended size: 5cm x 5cm or larger
- Students can laminate them for durability
- Test scanning before distributing to students

## Google Sheets Format

Your Google Sheet must follow this structure:

### Required Columns (A-C)

| Column | Header Options | Description |
|--------|---------------|-------------|
| A, B, or C | `ID` or `رقم الجلوس` | Student ID (must match QR codes) |
| Any | `Name` | Student name (optional but recommended) |
| Any | `Email` | Student email (optional) |

### Attendance Columns (D onwards)

| Week 1 | Week 2 | Week 3 | ... |
|--------|--------|--------|-----|
|        |        |        |     |
|        |        |        |     |

### Example Sheet

```
| ID       | Name          | Email              | Week 1 | Week 2 | Week 3 |
|----------|---------------|--------------------|--------|--------|--------|
| 20210001 | Ahmed Mohamed | ahmed@university   |        |        |        |
| 20210002 | Sara Ali      | sara@university    |        |        |        |
| 20210003 | Omar Hassan   | omar@university    |        |        |        |
```

### Important Notes

- The Student ID column **must** be in columns A, B, or C
- The header must be exactly `ID` or `رقم الجلوس` (case-insensitive)
- Attendance columns start from column D
- The system writes "P" for present (you can customize this in the code)
- Empty cells mean absent

## Troubleshooting

### Camera Not Working

**Problem**: Camera doesn't start or shows error

**Solutions**:
- Ensure you're using HTTPS or localhost (browsers require secure context for camera)
- Check browser permissions: Settings → Site Settings → Camera
- Try a different browser (Chrome recommended for mobile)
- Restart the browser
- Check if another app is using the camera

### Spreadsheet Access Denied

**Problem**: "Cannot access spreadsheet" error

**Solutions**:
- Verify the Service Account email is added as an Editor to your Google Sheet
- Check that the Spreadsheet ID is correct
- Ensure Google Sheets API is enabled in your Google Cloud project
- Verify the service account JSON credentials are correctly configured in `.env`

### Student Not Found

**Problem**: QR code scans but shows "Student Not Found"

**Solutions**:
- Verify the Student ID in the QR code matches exactly with the ID in the sheet
- Check that the ID column header is named `ID` or `رقم الجلوس`
- Ensure the ID column is in columns A, B, or C
- Check for extra spaces or formatting in the Student IDs

### Already Scanned Warning

**Problem**: Getting "Already Scanned" for different students

**Solutions**:
- This is normal if you scan the same student within 30 seconds
- Wait 30 seconds and try again
- If it persists, click "Change Session" and start a new session

### Backend Connection Error

**Problem**: Frontend can't connect to backend

**Solutions**:
- Verify the backend server is running (`http://localhost:8000/health`)
- Check that the API URL in frontend code matches your backend URL
- Ensure CORS is properly configured in `backend/main.py`
- Check firewall settings if accessing from another device

## Development

### Project Structure

```
qr-attendance-system/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── sheets_auth.py          # Google Sheets authentication
│   ├── sheets_service.py       # Google Sheets operations
│   ├── attendance_service.py   # Business logic
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment configuration
├── frontend/
│   ├── index.html             # Entry point
│   ├── config.html            # Configuration page
│   ├── session.html           # Session initialization
│   ├── scanner.html           # QR scanner interface
│   ├── app.js                 # Application logic
│   └── styles.css             # Styling
├── qr_generator/
│   ├── generate_qr.py         # QR code generation script
│   └── requirements.txt       # Python dependencies
└── tests/
    ├── unit/                  # Unit tests
    ├── integration/           # Integration tests
    └── conftest.py            # Test configuration
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-mock hypothesis

# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/unit/test_sheets_service.py
```

### API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Technology Stack

- **Backend**: FastAPI (Python) - Fast, modern web framework
- **Frontend**: Vanilla JavaScript - No build step required
- **QR Scanning**: html5-qrcode library
- **Database**: Google Sheets API via gspread
- **Testing**: pytest, Hypothesis (property-based testing)

## License

This project is intended for educational use in university settings.

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the API documentation at `/docs`
3. Check the browser console for error messages
4. Verify all setup steps were completed correctly

---

**Note**: This system is designed for simplicity and ease of use. For production deployment with many concurrent users, consider adding authentication, rate limiting, and database caching.
