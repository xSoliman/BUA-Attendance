# Architecture Integration - QR Attendance System

This document explains how all components of the QR Attendance System are wired together to create a complete, working application.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User's Browser                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │ config.html│  │session.html│  │   scanner.html         │ │
│  │            │  │            │  │  ┌──────────────────┐  │ │
│  │  - Input   │→ │  - Select  │→ │  │  QR Scanner      │  │ │
│  │    Sheet   │  │    Course  │  │  │  (html5-qrcode)  │  │ │
│  │    ID      │  │  - Select  │  │  └──────────────────┘  │ │
│  │            │  │    Week    │  │  - Manual Entry        │ │
│  └────────────┘  └────────────┘  │  - Toast Notifications │ │
│         │               │         └────────────────────────┘ │
│         └───────────────┴─────────────────┬─────────────────┘
│                                           │
│                    app.js (Frontend Logic)│
│                    - API calls            │
│                    - State management     │
│                    - Cooldown cache       │
│                    - localStorage         │
└───────────────────────────────────────────┼──────────────────┘
                                            │
                                            │ HTTP/JSON
                                            │
┌───────────────────────────────────────────▼──────────────────┐
│                    Backend Server (FastAPI)                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                      main.py                             │ │
│  │  - CORS middleware                                       │ │
│  │  - API endpoints                                         │ │
│  │  - Request/Response handling                             │ │
│  └──────────┬──────────────────────────────────────────────┘ │
│             │                                                 │
│  ┌──────────▼──────────┐  ┌──────────────────────────────┐  │
│  │  sheets_auth.py     │  │  attendance_service.py       │  │
│  │  - Service Account  │  │  - Business logic            │  │
│  │  - gspread client   │  │  - Student lookup            │  │
│  └──────────┬──────────┘  │  - Attendance marking        │  │
│             │              └──────────┬───────────────────┘  │
│  ┌──────────▼─────────────────────────▼───────────────────┐ │
│  │              sheets_service.py                          │ │
│  │  - Spreadsheet validation                               │ │
│  │  - Sheet names retrieval                                │ │
│  │  - Column headers fetching                              │ │
│  │  - Student_ID column identification                     │ │
│  └──────────┬──────────────────────────────────────────────┘ │
└─────────────┼────────────────────────────────────────────────┘
              │
              │ Google Sheets API
              │
┌─────────────▼────────────────────────────────────────────────┐
│                    Google Sheets                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Spreadsheet                                            │  │
│  │  ├─ CS101 (Sheet)                                       │  │
│  │  │  ├─ ID | Name | Email | Week 1 | Week 2 | ...       │  │
│  │  │  ├─ 20210001 | Student A | ... | P | | ...          │  │
│  │  │  └─ 20210002 | Student B | ... | | | ...            │  │
│  │  ├─ CS102 (Sheet)                                       │  │
│  │  └─ MATH201 (Sheet)                                     │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

## Component Wiring Details

### 1. Frontend Pages → app.js

All HTML pages load `app.js` which provides:

- **Configuration Management**: `getStoredConfig()`, `saveConfig()`, `clearConfig()`
- **API Communication**: `fetchServiceAccountEmail()`, `validateSpreadsheet()`, `fetchSheets()`, `fetchColumns()`, `recordAttendance()`
- **State Management**: `sessionContext`, `cooldownCache`
- **Page Initialization**: `initPage()`, `initConfigPage()`, `initSessionPage()`, `initScannerPage()`
- **UI Feedback**: `showToast()`, `updateStartButton()`

**Wiring Mechanism**: Each page calls `initPage()` on `DOMContentLoaded`, which routes to the appropriate initialization function based on the current page.

### 2. app.js → Backend API

Frontend communicates with backend via REST API:

```javascript
// Example: Recording attendance
const response = await fetch(`${API_BASE_URL}/attendance`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        spreadsheet_id: sessionContext.spreadsheetId,
        sheet_name: sessionContext.sheetName,
        column_name: sessionContext.columnName,
        student_id: studentId
    })
});
```

**API Base URL**: `http://localhost:8000/api` (configured in `app.js`)

**Endpoints Used**:
- `GET /api/service-account-email` → Display to user
- `POST /api/validate-spreadsheet` → Verify access
- `GET /api/sheets/{id}` → Populate course dropdown
- `GET /api/sheets/{id}/{sheet}/columns` → Populate week dropdown
- `POST /api/attendance` → Record attendance

### 3. Backend API → Service Modules

FastAPI routes delegate to service modules:

```python
# main.py
@app.post("/api/attendance")
async def record_attendance(request: AttendanceRequest):
    result = process_attendance(
        spreadsheet_id=request.spreadsheet_id,
        sheet_name=request.sheet_name,
        column_name=request.column_name,
        student_id=request.student_id
    )
    return result
```

**Service Layer**:
- `sheets_auth.py` → Manages Service Account authentication
- `sheets_service.py` → Handles Google Sheets API operations
- `attendance_service.py` → Implements business logic

### 4. Service Modules → Google Sheets API

Services use `gspread` library to interact with Google Sheets:

```python
# sheets_service.py
def get_sheet_names(spreadsheet_id: str) -> List[str]:
    client = get_gspread_client()
    spreadsheet = client.open_by_key(spreadsheet_id)
    return [sheet.title for sheet in spreadsheet.worksheets()]
```

**Authentication**: Service Account credentials loaded from `.env` file

### 5. Data Flow: Complete Attendance Recording

```
1. User scans QR code
   ↓
2. html5-qrcode extracts Student_ID
   ↓
3. app.js checks cooldown cache
   ↓
4. If not in cooldown, call recordAttendance(studentId)
   ↓
5. POST /api/attendance with session context + student_id
   ↓
6. Backend: process_attendance() in attendance_service.py
   ↓
7. Find student row by Student_ID
   ↓
8. Find column index by column name
   ↓
9. Write "P" to cell via Google Sheets API
   ↓
10. Return success/error status
   ↓
11. Frontend displays toast notification
   ↓
12. Add student to cooldown cache
```

## Configuration Wiring

### Environment Variables (Backend)

```env
# backend/.env
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
FRONTEND_URL=http://localhost:3000
```

**Loaded by**: `python-dotenv` in `main.py`
**Used by**: `sheets_auth.py` for authentication, `main.py` for CORS

### LocalStorage (Frontend)

```javascript
// Stored in browser
{
  "qr-attendance-config": {
    "spreadsheetId": "1abc123...",
    "lastUpdated": "2024-01-15T10:30:00Z"
  }
}
```

**Managed by**: `app.js` functions `getStoredConfig()`, `saveConfig()`
**Persists**: Across page reloads and browser sessions

### SessionStorage (Frontend)

```javascript
// Stored in browser session
{
  "qr-attendance-session": {
    "spreadsheetId": "1abc123...",
    "sheetName": "CS101",
    "columnName": "Week 1"
  }
}
```

**Managed by**: `app.js` functions `getSessionContext()`, `saveSessionContext()`
**Persists**: Only during current browser session

## CORS Configuration

Enables frontend-backend communication across different origins:

```python
# backend/main.py
origins = [
    "http://localhost:3000",  # Frontend dev server
    "http://localhost:8000",  # Alternative port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Why needed**: Browser security prevents cross-origin requests by default
**What it allows**: Frontend on port 3000 can call backend on port 8000

## State Management

### Frontend State

1. **Configuration State** (localStorage)
   - Spreadsheet ID
   - Persists across sessions

2. **Session State** (sessionStorage)
   - Current course (sheet name)
   - Current week (column name)
   - Persists during session only

3. **Runtime State** (JavaScript variables)
   - Cooldown cache (Map)
   - QR scanner instance
   - Toast notifications
   - Cleared on page reload

### Backend State

**Stateless Design**: Backend maintains no session state
- Each request contains all necessary context
- Service Account credentials loaded once at startup
- gspread client cached as singleton

## Error Handling Integration

### Frontend Error Handling

```javascript
try {
    const response = await fetch(...);
    const result = await response.json();
    
    if (result.status === 'success') {
        showToast('Attendance Recorded', 'success');
    } else if (result.status === 'not_found') {
        showToast('Student Not Found', 'error');
    } else {
        showToast(result.message, 'error');
    }
} catch (error) {
    if (!navigator.onLine) {
        showToast('Offline - will retry when connected', 'warning');
    } else {
        showToast('Network error. Please try again.', 'error');
    }
}
```

### Backend Error Handling

```python
try:
    # Google Sheets operation
    result = sheets_service.some_operation()
    return result
except gspread.exceptions.APIError as e:
    if e.response.status_code == 403:
        return {"valid": False, "message": "Access denied..."}
    elif e.response.status_code == 429:
        # Retry logic
        pass
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

## Asynchronous Operations

### Frontend Async Pattern

```javascript
// Non-blocking attendance recording
async function recordAttendance(studentId) {
    // Fire and forget - scanner continues working
    fetch('/api/attendance', {...})
        .then(response => response.json())
        .then(result => showToast(...))
        .catch(error => handleError(...));
}
```

### Backend Async Pattern

```python
# FastAPI handles async automatically
@app.post("/api/attendance")
async def record_attendance(request: AttendanceRequest):
    # Runs asynchronously, doesn't block other requests
    result = process_attendance(...)
    return result
```

## Testing Integration

### Manual Integration Test

```bash
# Run integration test script
./test_integration.sh
```

**Tests**:
1. Backend health check
2. All API endpoints
3. CORS configuration
4. Frontend file existence
5. Frontend-backend API references

### Complete User Flow Test

1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && python -m http.server 3000`
3. Open browser: `http://localhost:3000`
4. Follow configuration → session → scanning flow
5. Verify attendance is recorded in Google Sheet

## Deployment Integration

### Development

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
python -m http.server 3000
```

### Production (Docker)

```bash
# Build and run with docker-compose
docker-compose up -d
```

**docker-compose.yml** wires:
- Backend service (port 8000)
- Frontend service (port 80)
- Environment variables
- Volume mounts

## Key Integration Points

1. **API URL Configuration**: `API_BASE_URL` in `app.js` must match backend URL
2. **CORS Origins**: Backend must allow frontend origin
3. **Service Account**: Must be shared with Google Sheets
4. **Environment Variables**: Backend `.env` must be configured
5. **HTML5 QR Code Library**: Loaded via CDN in `scanner.html`
6. **LocalStorage Keys**: Must match between pages
7. **Session Context**: Must be passed from session page to scanner page

## Troubleshooting Integration Issues

### Frontend can't reach backend
- Check `API_BASE_URL` in `app.js`
- Verify backend is running on correct port
- Check browser console for CORS errors

### CORS errors
- Verify frontend origin is in `origins` list in `main.py`
- Check CORS middleware is configured
- Ensure credentials are allowed

### Authentication errors
- Verify `.env` file exists and is loaded
- Check Service Account JSON is valid
- Ensure Service Account is shared with spreadsheet

### Scanner not working
- Verify `html5-qrcode` library is loaded
- Check camera permissions in browser
- Ensure HTTPS (required for camera on non-localhost)

---

**Integration Status**: ✅ Complete
**Last Updated**: Task 17.3
**Next Steps**: Run integration tests and verify complete user flow
