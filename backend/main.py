"""
FastAPI Application for QR Attendance System

This module initializes the FastAPI application with CORS middleware
and configures request timeout settings for the attendance system.

Requirements: 9.1
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from sheets_auth import get_service_account_email
from sheets_service import (
    validate_spreadsheet_access,
    get_sheet_names,
    get_headers,
    process_batch_attendance
)
from attendance_service import (
    AttendanceRequest,
    AttendanceResult,
    process_attendance
)
from routers.tools import router as tools_router

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="QR Attendance System API",
    description="Backend API for recording student attendance via QR code scanning",
    version="1.0.0"
)

# Configure CORS middleware
# Allow frontend to make requests from different origins
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",  # Docker local frontend
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
]

# Add custom origins from environment variable if provided
custom_origin = os.getenv("FRONTEND_ORIGIN")
if custom_origin:
    origins.append(custom_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tools_router)


@app.get("/")
async def root():
    """
    Root endpoint for health check.
    
    Returns:
        dict: Simple message indicating the API is running
    """
    return {
        "message": "QR Attendance System API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: Health status of the API
    """
    return {"status": "healthy"}


# ============================================================================
# API Endpoints
# ============================================================================


class SpreadsheetValidation(BaseModel):
    """Request model for spreadsheet validation."""
    spreadsheet_id: str


@app.get("/api/service-account-email")
async def get_service_email():
    """
    Get the Service Account email address.
    
    This endpoint returns the email address of the Service Account that must be
    added as an Editor to any Google Sheet the system needs to access.
    
    Returns:
        dict: Object containing the Service Account email
        
    Requirements: 2.5
    
    Example Response:
        {
            "email": "attendance-system@project-id.iam.gserviceaccount.com"
        }
    """
    try:
        email = get_service_account_email()
        return {"email": email}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/validate-spreadsheet")
async def validate_spreadsheet(request: SpreadsheetValidation):
    """
    Validate that the Service Account has access to a Google Spreadsheet.
    
    This endpoint checks if the spreadsheet exists and if the Service Account
    has the necessary permissions to read and write to it.
    
    Args:
        request: SpreadsheetValidation object containing the spreadsheet_id
        
    Returns:
        dict: Validation result with 'valid' boolean and 'message' string
        
    Requirements: 1.2, 1.3
    
    Example Request:
        {
            "spreadsheet_id": "1abc..."
        }
        
    Example Response (Success):
        {
            "valid": true,
            "message": "Spreadsheet accessible"
        }
        
    Example Response (Error):
        {
            "valid": false,
            "message": "Spreadsheet not found. Please add [email] as an Editor."
        }
    """
    result = validate_spreadsheet_access(request.spreadsheet_id)
    return result


@app.get("/api/sheets/{spreadsheet_id}")
async def get_sheets(spreadsheet_id: str):
    """
    Get all sheet names from a Google Spreadsheet.
    
    This endpoint retrieves the list of all sheet (tab) names in the specified
    spreadsheet. This is used during session initialization to allow TAs to
    select which course sheet they want to record attendance for.
    
    Args:
        spreadsheet_id: The unique identifier from the Google Sheet URL
        
    Returns:
        dict: Object containing a list of sheet names
        
    Raises:
        HTTPException: If there's an error accessing the spreadsheet
        
    Requirements: 1.4, 3.2
    
    Example Response:
        {
            "sheets": ["CS101", "CS102", "MATH201"]
        }
    """
    try:
        sheets = get_sheet_names(spreadsheet_id)
        return {"sheets": sheets}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sheet names: {str(e)}"
        )


@app.get("/api/sheets/{spreadsheet_id}/{sheet_name}/columns")
async def get_attendance_columns(spreadsheet_id: str, sheet_name: str):
    """
    Get attendance column names from a specific sheet.
    
    This endpoint retrieves the header row from the specified sheet and returns
    only the columns starting from column D (index 3) onwards. These columns
    represent attendance columns (e.g., "Week 1", "Week 2", etc.).
    
    Args:
        spreadsheet_id: The unique identifier from the Google Sheet URL
        sheet_name: The name of the specific sheet/tab to read from
        
    Returns:
        dict: Object containing a list of attendance column names
        
    Raises:
        HTTPException: If there's an error accessing the spreadsheet or sheet
        
    Requirements: 1.5, 3.3, 3.4
    
    Example Response:
        {
            "columns": ["Week 1", "Week 2", "Week 3", "Week 4"]
        }
    """
    try:
        columns = get_headers(spreadsheet_id, sheet_name)
        return {"columns": columns}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve columns: {str(e)}"
        )


@app.post("/api/attendance")
async def record_attendance(request: AttendanceRequest):
    """
    Record attendance for a student asynchronously.
    
    This endpoint processes an attendance recording request by:
    1. Looking up the student's row in the sheet by their Student_ID
    2. If found, marking attendance by writing "P" to the appropriate cell
    3. If not found, returning a "Student Not Found" status
    
    The operation is performed asynchronously to maintain UI responsiveness.
    
    Args:
        request: AttendanceRequest object containing:
            - spreadsheet_id: The Google Sheet identifier
            - sheet_name: The course sheet name
            - column_name: The attendance column name (e.g., "Week 1")
            - student_id: The student's unique identifier
            
    Returns:
        AttendanceResult: Object containing status and message
        
    Requirements: 1.7, 1.8, 1.9, 9.1
    
    Example Request:
        {
            "spreadsheet_id": "1abc...",
            "sheet_name": "CS101",
            "column_name": "Week 1",
            "student_id": "20210001"
        }
        
    Example Response (Success):
        {
            "status": "success",
            "message": "Attendance recorded"
        }
        
    Example Response (Not Found):
        {
            "status": "not_found",
            "message": "Student Not Found"
        }
        
    Example Response (Error):
        {
            "status": "error",
            "message": "Failed to record attendance: [error details]"
        }
    """
    result = process_attendance(
        spreadsheet_id=request.spreadsheet_id,
        sheet_name=request.sheet_name,
        column_name=request.column_name,
        student_id=request.student_id
    )
    return result


class BatchAttendanceRequest(BaseModel):
    """Request model for batch attendance recording."""
    spreadsheet_id: str
    sheet_name: str
    column_name: str
    student_ids: list[str]


class BatchAttendanceResult(BaseModel):
    """Result model for batch attendance recording."""
    total: int
    successful: int
    failed: int
    not_found: int
    details: list[dict]


@app.post("/api/attendance/batch")
async def record_batch_attendance(request: BatchAttendanceRequest):
    """
    Record attendance for multiple students in a single batch operation.
    
    This endpoint processes multiple attendance records at once using optimized
    batch operations that minimize API calls to Google Sheets. Instead of making
    2*N API calls (N lookups + N writes), it makes only 2 total API calls
    (1 read all data + 1 batch write).
    
    Args:
        request: BatchAttendanceRequest object containing:
            - spreadsheet_id: The Google Sheet identifier
            - sheet_name: The course sheet name
            - column_name: The attendance column name (e.g., "Week 1")
            - student_ids: List of student IDs to mark attendance for
            
    Returns:
        BatchAttendanceResult: Object containing summary and details
        
    Example Request:
        {
            "spreadsheet_id": "1abc...",
            "sheet_name": "CS101",
            "column_name": "Week 1",
            "student_ids": ["20210001", "20210002", "20210003"]
        }
        
    Example Response:
        {
            "total": 3,
            "successful": 2,
            "failed": 0,
            "not_found": 1,
            "details": [
                {"student_id": "20210001", "status": "success", "message": "Attendance recorded"},
                {"student_id": "20210002", "status": "success", "message": "Attendance recorded"},
                {"student_id": "20210003", "status": "not_found", "message": "Student Not Found"}
            ]
        }
    """
    try:
        # Use optimized batch processing
        result = process_batch_attendance(
            spreadsheet_id=request.spreadsheet_id,
            sheet_name=request.sheet_name,
            column_name=request.column_name,
            student_ids=request.student_ids
        )
        
        # Build detailed results
        details = []
        
        # Add successful students
        for student_id in result['successful']:
            details.append({
                "student_id": student_id,
                "status": "success",
                "message": "Attendance recorded"
            })
        
        # Add not found students
        for student_id in result['not_found']:
            details.append({
                "student_id": student_id,
                "status": "not_found",
                "message": "Student Not Found"
            })
        
        # Add failed students
        for student_id in result['failed']:
            details.append({
                "student_id": student_id,
                "status": "error",
                "message": "Failed to record attendance"
            })
        
        return BatchAttendanceResult(
            total=len(request.student_ids),
            successful=len(result['successful']),
            failed=len(result['failed']),
            not_found=len(result['not_found']),
            details=details
        )
        
    except Exception as e:
        # If there's a critical error, mark all as failed with the actual error message
        details = []
        for student_id in request.student_ids:
            details.append({
                "student_id": student_id,
                "status": "error",
                "message": f"Batch processing failed: {str(e)}"
            })
        
        return BatchAttendanceResult(
            total=len(request.student_ids),
            successful=0,
            failed=len(request.student_ids),
            not_found=0,
            details=details
        )
