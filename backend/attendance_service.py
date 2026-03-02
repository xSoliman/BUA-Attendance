"""
Attendance Service Module

This module defines the data models for attendance recording operations.
It provides Pydantic models for requests and responses, and an enum for status codes.
"""

from enum import Enum
from pydantic import BaseModel, Field
from sheets_service import find_student_row, mark_attendance


class AttendanceStatus(str, Enum):
    """Status codes for attendance recording operations."""
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    ERROR = "error"


class AttendanceRequest(BaseModel):
    """Request model for recording attendance.
    
    Attributes:
        spreadsheet_id: The unique identifier from the Google Sheet URL
        sheet_name: The name of the course sheet tab
        column_name: The name of the attendance column (e.g., "Week 1")
        student_id: The student's unique identifier from their QR code
    """
    spreadsheet_id: str = Field(..., description="Google Sheets spreadsheet ID")
    sheet_name: str = Field(..., description="Name of the course sheet")
    column_name: str = Field(..., description="Name of the attendance column")
    student_id: str = Field(..., description="Student's unique identifier")


class AttendanceResult(BaseModel):
    """Result model for attendance recording operations.
    
    Attributes:
        status: The outcome of the attendance recording attempt
        message: A human-readable description of the result
    """
    status: AttendanceStatus = Field(..., description="Status of the operation")
    message: str = Field(..., description="Human-readable result message")


def process_attendance(
    spreadsheet_id: str,
    sheet_name: str,
    column_name: str,
    student_id: str
) -> AttendanceResult:
    """
    Process attendance recording by combining student lookup and attendance marking.
    
    This function orchestrates the complete attendance recording process:
    1. Looks up the student's row in the sheet by their Student_ID
    2. If found, marks attendance by writing "P" to the appropriate cell
    3. If not found, returns NOT_FOUND status without modifying the sheet
    4. Handles any errors that occur during the process
    
    Args:
        spreadsheet_id: The unique identifier from the Google Sheet URL
        sheet_name: The name of the course sheet tab
        column_name: The name of the attendance column (e.g., "Week 1")
        student_id: The student's unique identifier from their QR code
        
    Returns:
        AttendanceResult with status and message indicating the outcome
        
    Requirements: 1.9
    
    Examples:
        >>> result = process_attendance("1abc...", "CS101", "Week 1", "20210001")
        >>> result.status
        <AttendanceStatus.SUCCESS: 'success'>
        >>> result.message
        'Attendance recorded'
        
        >>> result = process_attendance("1abc...", "CS101", "Week 1", "99999999")
        >>> result.status
        <AttendanceStatus.NOT_FOUND: 'not_found'>
        >>> result.message
        'Student Not Found'
    """
    try:
        # Step 1: Look up the student's row
        row = find_student_row(spreadsheet_id, sheet_name, student_id)
        
        # Step 2: Check if student was found
        if row is None:
            # Student not found - return NOT_FOUND status without modifying sheet
            return AttendanceResult(
                status=AttendanceStatus.NOT_FOUND,
                message="Student Not Found"
            )
        
        # Step 3: Mark attendance for the found student
        mark_attendance(spreadsheet_id, sheet_name, row, column_name)
        
        # Step 4: Return success result
        return AttendanceResult(
            status=AttendanceStatus.SUCCESS,
            message="Attendance recorded"
        )
        
    except Exception as e:
        # Handle any errors that occur during the process
        return AttendanceResult(
            status=AttendanceStatus.ERROR,
            message=f"Failed to record attendance: {str(e)}"
        )
