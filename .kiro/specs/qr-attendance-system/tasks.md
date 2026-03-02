# Implementation Plan: QR Attendance System

## Overview

This implementation plan breaks down the QR Attendance System into discrete coding tasks. The system consists of three main components: a Python FastAPI backend for Google Sheets integration, a vanilla JavaScript frontend for mobile scanning, and a Python script for QR code generation. Tasks are organized to build incrementally, with early validation of core functionality through property-based tests.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure: `backend/`, `frontend/`, `qr_generator/`, `tests/`
  - Create `backend/requirements.txt` with FastAPI, gspread, uvicorn, python-dotenv, pydantic
  - Create `backend/.env.example` for Service Account credentials template
  - Create `frontend/index.html`, `frontend/config.html`, `frontend/session.html`, `frontend/scanner.html`
  - Create `frontend/styles.css` with Tailwind CSS CDN
  - Create `frontend/app.js` for main application logic
  - Create `qr_generator/requirements.txt` with qrcode, Pillow, pandas
  - Create `tests/conftest.py` for pytest configuration
  - _Requirements: All requirements (project foundation)_

- [ ] 2. Implement backend Google Sheets service
  - [x] 2.1 Create Service Account authentication module
    - Write `backend/sheets_auth.py` with gspread client initialization
    - Load Service Account credentials from environment variables
    - Implement `get_service_account_email()` function
    - _Requirements: 1.1, 2.5_
  
  - [x] 2.2 Implement spreadsheet validation
    - Write `validate_spreadsheet_access(spreadsheet_id)` function
    - Handle `gspread.exceptions.APIError` for 403 errors
    - Return validation result with error messages
    - _Requirements: 1.2, 1.3_
  
  - [ ]* 2.3 Write property test for spreadsheet validation
    - **Property 1: Spreadsheet Access Validation**
    - **Validates: Requirements 1.2**
  
  - [x] 2.4 Implement sheet names retrieval
    - Write `get_sheet_names(spreadsheet_id)` function
    - Return list of all sheet tab names
    - _Requirements: 1.4, 3.2_
  
  - [ ]* 2.5 Write property test for sheet names retrieval
    - **Property 2: Sheet Names Retrieval**
    - **Validates: Requirements 1.4, 3.2**
  
  - [x] 2.6 Implement header row fetching
    - Write `get_headers(spreadsheet_id, sheet_name)` function
    - Return all column headers from row 1
    - Filter headers starting from column D (index 3) for attendance columns
    - _Requirements: 1.5, 3.3, 3.4_
  
  - [ ]* 2.7 Write property test for attendance column filtering
    - **Property 7: Attendance Column Filtering**
    - **Validates: Requirements 1.5, 3.3, 3.4**
  
  - [x] 2.8 Implement Student_ID column identification
    - Write `find_student_id_column(headers)` function
    - Search for "ID" or "رقم الجلوس" (case-insensitive) in columns A-C
    - Return column index or raise error if not found
    - _Requirements: 1.6_
  
  - [ ]* 2.9 Write property test for Student_ID column identification
    - **Property 3: Student ID Column Identification**
    - **Validates: Requirements 1.6**

- [ ] 3. Implement attendance recording logic
  - [x] 3.1 Create attendance service module
    - Write `backend/attendance_service.py` with `AttendanceRequest` and `AttendanceResult` Pydantic models
    - Define `AttendanceStatus` enum (SUCCESS, NOT_FOUND, ERROR)
    - _Requirements: 1.7, 1.8, 1.9_
  
  - [x] 3.2 Implement student row lookup
    - Write `find_student_row(spreadsheet_id, sheet_name, student_id)` function
    - Search Student_ID column for matching value
    - Return row index or None if not found
    - _Requirements: 1.7_
  
  - [x] 3.3 Implement attendance marking
    - Write `mark_attendance(spreadsheet_id, sheet_name, row, column_name)` function
    - Find column index by header name
    - Write "P" to cell at (row, column)
    - _Requirements: 1.8_
  
  - [ ]* 3.4 Write property test for attendance marking round-trip
    - **Property 4: Attendance Marking Round-Trip**
    - **Validates: Requirements 1.7, 1.8**
  
  - [x] 3.5 Implement student not found handling
    - Write `process_attendance()` function that combines lookup and marking
    - Return `AttendanceResult` with NOT_FOUND status when student doesn't exist
    - Ensure no sheet modification on NOT_FOUND
    - _Requirements: 1.9_
  
  - [ ]* 3.6 Write property test for student not found handling
    - **Property 5: Student Not Found Handling**
    - **Validates: Requirements 1.9**

- [ ] 4. Implement FastAPI endpoints
  - [x] 4.1 Create FastAPI application with CORS
    - Write `backend/main.py` with FastAPI app initialization
    - Configure CORS middleware for frontend origin
    - Set up request timeout (30 seconds)
    - _Requirements: 9.1_
  
  - [x] 4.2 Implement GET /api/service-account-email endpoint
    - Return Service Account email from authentication module
    - _Requirements: 2.5_
  
  - [x] 4.3 Implement POST /api/validate-spreadsheet endpoint
    - Accept `SpreadsheetValidation` request body
    - Call `validate_spreadsheet_access()`
    - Return validation result JSON
    - _Requirements: 1.2, 1.3_
  
  - [x] 4.4 Implement GET /api/sheets/{spreadsheet_id} endpoint
    - Call `get_sheet_names()`
    - Return list of sheet names
    - _Requirements: 1.4, 3.2_
  
  - [x] 4.5 Implement GET /api/sheets/{spreadsheet_id}/{sheet_name}/columns endpoint
    - Call `get_headers()` with filtering for columns D onwards
    - Return attendance column names
    - _Requirements: 1.5, 3.3, 3.4_
  
  - [x] 4.6 Implement POST /api/attendance endpoint
    - Accept `AttendanceRequest` body (spreadsheet_id, sheet_name, column_name, student_id)
    - Call `process_attendance()` asynchronously
    - Return `AttendanceResult` JSON
    - _Requirements: 1.7, 1.8, 1.9, 9.1_
  
  - [ ]* 4.7 Write unit tests for API endpoints
    - Test each endpoint with valid and invalid inputs
    - Mock Google Sheets service
    - Test error responses (403, 404, 500)
    - _Requirements: All backend requirements_

- [ ] 5. Implement error handling and retry logic
  - [x] 5.1 Create error handling middleware
    - Write exception handlers for `gspread.exceptions.APIError`
    - Handle 403 (permission denied) with user-friendly message
    - Handle 429 (rate limit) with retry indication
    - Handle generic errors with logging
    - _Requirements: 11.1, 11.2_
  
  - [x] 5.2 Implement rate limit retry with exponential backoff
    - Write retry decorator with 2s, 4s, 8s delays
    - Maximum 3 retry attempts
    - Apply to all Google Sheets operations
    - _Requirements: 11.2_
  
  - [ ]* 5.3 Write property test for rate limit retry
    - **Property 27: Rate Limit Retry**
    - **Validates: Requirements 11.2**
  
  - [x] 5.4 Implement validation error handling
    - Check for missing Student_ID column and return clear error
    - Check for invalid attendance column and return error
    - _Requirements: 11.3, 11.4_
  
  - [ ]* 5.5 Write unit tests for error scenarios
    - Test authentication errors
    - Test network errors
    - Test validation errors
    - _Requirements: 11.1, 11.3, 11.4, 11.5_

- [x] 6. Checkpoint - Backend validation
  - Ensure all backend tests pass, ask the user if questions arise.

- [ ] 7. Implement frontend configuration page
  - [x] 7.1 Create configuration page HTML structure
    - Write `frontend/config.html` with Spreadsheet_ID input field
    - Add Service Account email display area
    - Add validation status indicator
    - Add "Save Configuration" button
    - _Requirements: 2.1, 2.5_
  
  - [x] 7.2 Implement configuration page JavaScript logic
    - Write `loadConfig()` to retrieve Spreadsheet_ID from localStorage
    - Write `fetchServiceAccountEmail()` to call GET /api/service-account-email
    - Write `validateSpreadsheet()` to call POST /api/validate-spreadsheet
    - Write `saveConfig()` to store Spreadsheet_ID in localStorage
    - Write `clearConfig()` to remove stored configuration
    - Navigate to session initialization on successful validation
    - _Requirements: 2.2, 2.3, 2.4_
  
  - [ ]* 7.3 Write property test for configuration persistence
    - **Property 6: Configuration Persistence Round-Trip**
    - **Validates: Requirements 2.2, 2.3**
  
  - [ ]* 7.4 Write unit tests for configuration page
    - Test localStorage operations
    - Test validation flow
    - Test error display
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 8. Implement frontend session initialization page
  - [x] 8.1 Create session initialization HTML structure
    - Write `frontend/session.html` with Course_Sheet dropdown
    - Add Attendance_Column dropdown
    - Add "Start Scanner" button (initially disabled)
    - Add "Change Configuration" button
    - Add loading indicators
    - _Requirements: 3.1, 3.5, 3.6_
  
  - [x] 8.2 Implement session initialization JavaScript logic
    - Write `fetchSheets()` to call GET /api/sheets/{spreadsheet_id}
    - Write `fetchColumns()` to call GET /api/sheets/{spreadsheet_id}/{sheet_name}/columns
    - Write `onSheetSelected()` to populate column dropdown
    - Write `onColumnSelected()` to enable "Start Scanner" button
    - Write `startSession()` to store session context and navigate to scanner
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6_
  
  - [ ]* 8.3 Write property test for session initialization validation
    - **Property 8: Session Initialization Validation**
    - **Validates: Requirements 3.5**
  
  - [ ]* 8.4 Write unit tests for session initialization
    - Test sheet fetching
    - Test column fetching
    - Test button enable/disable logic
    - Test session context storage
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ] 9. Implement QR scanner interface
  - [x] 9.1 Create scanner HTML structure
    - Write `frontend/scanner.html` with camera viewfinder div
    - Add session info display (sheet name + column name)
    - Add manual entry text input and submit button
    - Add toast notification container
    - Add "Change Session" button
    - _Requirements: 4.1, 4.2, 7.1, 12.1, 12.2_
  
  - [x] 9.2 Implement scanner initialization
    - Write `initializeScanner()` using html5-qrcode library
    - Request camera access with error handling
    - Configure scanner for continuous scanning
    - Display camera viewfinder at 80% viewport width
    - _Requirements: 4.1, 4.2, 4.6_
  
  - [x] 9.3 Implement QR code processing
    - Write `onScanSuccess(decodedText)` callback
    - Extract Student_ID from decoded text
    - Check cooldown cache before processing
    - Call `recordAttendance()` if not in cooldown
    - _Requirements: 4.3, 4.4, 6.2_
  
  - [ ]* 9.4 Write property test for QR code data extraction
    - **Property 9: QR Code Data Extraction**
    - **Validates: Requirements 4.3**
  
  - [ ]* 9.5 Write property test for scanner continuous operation
    - **Property 10: Scanner Continuous Operation**
    - **Validates: Requirements 4.5**
  
  - [x] 9.6 Implement manual entry processing
    - Write `onManualSubmit()` event handler
    - Process manual Student_ID identically to scanned ID
    - Clear input field after submission
    - _Requirements: 7.2, 7.3_
  
  - [ ]* 9.7 Write property test for manual entry equivalence
    - **Property 17: Manual Entry Equivalence**
    - **Validates: Requirements 7.2, 7.4**
  
  - [ ]* 9.8 Write property test for manual entry field reset
    - **Property 18: Manual Entry Field Reset**
    - **Validates: Requirements 7.3**

- [ ] 10. Implement attendance recording and feedback
  - [x] 10.1 Implement attendance recording function
    - Write `recordAttendance(studentId)` async function
    - Call POST /api/attendance with session context
    - Handle response status (success, not_found, error)
    - Display appropriate toast notification
    - Add Student_ID to cooldown cache on success
    - _Requirements: 5.1, 5.2, 5.3, 6.1_
  
  - [ ]* 10.2 Write property test for attendance result feedback
    - **Property 11: Attendance Result Feedback**
    - **Validates: Requirements 5.1, 5.2, 5.3**
  
  - [x] 10.3 Implement toast notification component
    - Write `showToast(message, type)` function
    - Create toast element with color coding (green/red/yellow)
    - Add to toast container
    - Auto-dismiss after 3 seconds
    - Support multiple simultaneous toasts
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 10.4 Write property test for toast auto-dismiss
    - **Property 12: Toast Auto-Dismiss**
    - **Validates: Requirements 5.4**
  
  - [ ]* 10.5 Write property test for concurrent toast display
    - **Property 13: Concurrent Toast Display**
    - **Validates: Requirements 5.5**
  
  - [ ]* 10.6 Write unit tests for toast notifications
    - Test toast creation and styling
    - Test auto-dismiss timing
    - Test multiple toast stacking
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 11. Implement cooldown management
  - [x] 11.1 Create cooldown cache data structure
    - Write `cooldownCache` as Map<Student_ID, timestamp>
    - Initialize on scanner page load
    - _Requirements: 6.1_
  
  - [x] 11.2 Implement cooldown checking
    - Write `checkCooldown(studentId)` function
    - Check if Student_ID exists in cache
    - Calculate time elapsed since last scan
    - Return true if less than 30 seconds elapsed
    - _Requirements: 6.2_
  
  - [x] 11.3 Implement duplicate scan prevention
    - In `onScanSuccess()`, call `checkCooldown()` before recording
    - Display "Already Scanned" yellow toast if in cooldown
    - Skip API call if in cooldown
    - _Requirements: 6.3, 6.4_
  
  - [ ]* 11.4 Write property test for cooldown list maintenance
    - **Property 14: Cooldown List Maintenance**
    - **Validates: Requirements 6.1**
  
  - [ ]* 11.5 Write property test for duplicate scan prevention
    - **Property 15: Duplicate Scan Prevention**
    - **Validates: Requirements 6.2, 6.3, 6.4**
  
  - [x] 11.6 Implement cooldown expiration
    - Write `cleanupCooldown()` function
    - Remove entries older than 30 seconds
    - Call periodically (every 5 seconds)
    - _Requirements: 6.5_
  
  - [ ]* 11.7 Write property test for cooldown expiration
    - **Property 16: Cooldown Expiration**
    - **Validates: Requirements 6.5**
  
  - [ ]* 11.8 Write unit tests for cooldown management
    - Test cooldown cache operations
    - Test 30-second boundary conditions
    - Test cleanup function
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 12. Implement session management
  - [x] 12.1 Display current session context
    - Show selected Course_Sheet and Attendance_Column in scanner UI
    - _Requirements: 12.1_
  
  - [ ]* 12.2 Write property test for session context display
    - **Property 28: Session Context Display**
    - **Validates: Requirements 12.1**
  
  - [x] 12.3 Implement session change functionality
    - Write `changeSession()` function
    - Stop camera using html5-qrcode API
    - Clear cooldown cache
    - Navigate to session initialization page
    - Preserve Spreadsheet_ID in localStorage
    - _Requirements: 12.2, 12.3, 12.4, 12.5_
  
  - [ ]* 12.4 Write property test for session change cleanup
    - **Property 29: Session Change Cleanup**
    - **Validates: Requirements 12.4, 12.5**
  
  - [ ]* 12.5 Write unit tests for session management
    - Test session context display
    - Test camera cleanup on session change
    - Test cooldown cache clearing
    - Test localStorage preservation
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 13. Implement mobile-responsive UI
  - [x] 13.1 Create responsive CSS with Tailwind
    - Write `frontend/styles.css` with mobile-first breakpoints
    - Style camera viewfinder to 80% viewport width on mobile
    - Set minimum tap target sizes to 44x44 pixels
    - Set minimum font size to 16 pixels
    - Position manual entry controls within thumb reach
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ]* 13.2 Write unit tests for responsive UI
    - Test viewport-based styling
    - Test touch target sizes
    - Test font sizes
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 14. Implement asynchronous operations
  - [x] 14.1 Ensure all API calls are non-blocking
    - Use async/await for all fetch() calls
    - Maintain scanner interactivity during API calls
    - _Requirements: 9.1, 9.2_
  
  - [ ]* 14.2 Write property test for non-blocking operations
    - **Property 19: Non-Blocking Operations**
    - **Validates: Requirements 9.2**
  
  - [x] 14.3 Implement operation queueing for rapid scans
    - Write queue mechanism for concurrent attendance requests
    - Process queue asynchronously
    - _Requirements: 9.3_
  
  - [ ]* 14.4 Write property test for asynchronous queue processing
    - **Property 20: Asynchronous Queue Processing**
    - **Validates: Requirements 9.3**
  
  - [x] 14.5 Implement loading indicators
    - Display spinner for operations longer than 1 second
    - _Requirements: 9.4_
  
  - [ ]* 14.6 Write property test for loading indicator display
    - **Property 21: Loading Indicator Display**
    - **Validates: Requirements 9.4**
  
  - [x] 14.7 Implement error recovery for failed operations
    - Display error notification on failure
    - Continue scanner operation without interruption
    - _Requirements: 9.5_
  
  - [ ]* 14.8 Write property test for error recovery
    - **Property 22: Error Recovery**
    - **Validates: Requirements 9.5**

- [x] 15. Checkpoint - Frontend validation
  - Ensure all frontend tests pass, ask the user if questions arise.

- [ ] 16. Implement QR code generator script
  - [x] 16.1 Create QR generator script structure
    - Write `qr_generator/generate_qr.py` with main function
    - Accept CSV file path as command-line argument
    - Create output directory if not exists
    - _Requirements: 10.1, 10.6_
  
  - [x] 16.2 Implement CSV parsing
    - Read CSV file with pandas
    - Extract Student_ID and Name columns
    - Validate required columns exist
    - _Requirements: 10.1_
  
  - [x] 16.3 Implement QR code generation
    - For each student, generate QR code with qrcode library
    - Encode only Student_ID in QR code
    - _Requirements: 10.2, 10.3_
  
  - [ ]* 16.4 Write property test for QR code generation cardinality
    - **Property 23: QR Code Generation Cardinality**
    - **Validates: Requirements 10.1, 10.2**
  
  - [ ]* 16.5 Write property test for QR code content round-trip
    - **Property 24: QR Code Content Round-Trip**
    - **Validates: Requirements 10.3**
  
  - [x] 16.6 Implement image footer generation
    - Use Pillow to add text footer to QR code image
    - Footer text: "Name: {Name} | ID: {Student_ID}"
    - _Requirements: 10.4_
  
  - [x] 16.7 Implement file saving
    - Save each QR code as "{Student_ID}.png"
    - Save to output directory
    - _Requirements: 10.5_
  
  - [ ]* 16.8 Write property test for QR code image metadata
    - **Property 25: QR Code Image Metadata**
    - **Validates: Requirements 10.4, 10.5**
  
  - [ ]* 16.9 Write property test for output directory creation
    - **Property 26: Output Directory Creation**
    - **Validates: Requirements 10.6**
  
  - [ ]* 16.10 Write unit tests for QR generator
    - Test CSV parsing with various formats
    - Test filename sanitization
    - Test error handling for invalid CSV
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

- [ ] 17. Integration and deployment setup
  - [x] 17.1 Create deployment configuration
    - Write `backend/Dockerfile` for FastAPI application
    - Write `docker-compose.yml` for local development
    - Create `.env.example` with all required environment variables
    - _Requirements: All requirements (deployment)_
  
  - [x] 17.2 Create README documentation
    - Write setup instructions for Service Account creation
    - Document environment variable configuration
    - Provide usage instructions for TAs
    - Document QR generator script usage
    - _Requirements: All requirements (documentation)_
  
  - [x] 17.3 Wire all components together
    - Ensure frontend pages link correctly
    - Verify API endpoints are accessible from frontend
    - Test complete user flow from configuration to scanning
    - _Requirements: All requirements (integration)_
  
  - [ ]* 17.4 Write integration tests
    - Test complete attendance recording flow
    - Test session initialization with real Google Sheets (test account)
    - Test error handling with simulated failures
    - _Requirements: All requirements (integration testing)_

- [x] 18. Final checkpoint - End-to-end validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property-based tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The implementation follows a bottom-up approach: backend services → API endpoints → frontend components → integration
- All Google Sheets operations use asynchronous patterns to maintain UI responsiveness
- The mobile-first design ensures usability in lab environments
- Service Account credentials must be configured before running the backend
