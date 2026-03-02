"""
Google Sheets Service Module

This module provides functions for interacting with Google Sheets,
including validation, data retrieval, and attendance marking.

Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9
"""

import gspread
from typing import Dict, Any
from sheets_auth import get_gspread_client, get_service_account_email


def validate_spreadsheet_access(spreadsheet_id: str) -> Dict[str, Any]:
    """
    Validate that the Service Account has access to the specified Google Sheet.
    
    This function attempts to open the spreadsheet and checks if the Service Account
    has the necessary permissions. If access is denied (403 error), it returns
    a helpful error message instructing the user to add the Service Account as an Editor.
    
    Args:
        spreadsheet_id: The unique identifier from the Google Sheet URL
        
    Returns:
        Dict with keys:
            - valid (bool): True if spreadsheet is accessible, False otherwise
            - message (str): Success message or error description
            
    Requirements: 1.2, 1.3
    
    Examples:
        >>> result = validate_spreadsheet_access("1abc...")
        >>> result['valid']
        True
        >>> result['message']
        'Spreadsheet accessible'
    """
    try:
        client = get_gspread_client()
        # Attempt to open the spreadsheet - this will raise an exception if access is denied
        spreadsheet = client.open_by_key(spreadsheet_id)
        
        return {
            "valid": True,
            "message": "Spreadsheet accessible"
        }
        
    except gspread.exceptions.APIError as e:
        # Handle 403 Forbidden errors (permission denied)
        if e.response.status_code == 403:
            service_email = get_service_account_email()
            return {
                "valid": False,
                "message": f"Spreadsheet not found or access denied. Please add {service_email} as an Editor to your Google Sheet."
            }
        else:
            # Handle other API errors
            return {
                "valid": False,
                "message": f"Google Sheets API error: {str(e)}"
            }
            
    except gspread.exceptions.SpreadsheetNotFound:
        # Handle spreadsheet not found
        service_email = get_service_account_email()
        return {
            "valid": False,
            "message": f"Spreadsheet not found. Please verify the Spreadsheet ID and ensure {service_email} is added as an Editor."
        }
        
    except Exception as e:
        # Handle any other unexpected errors
        return {
            "valid": False,
            "message": f"Unexpected error: {str(e)}"
        }


def get_sheet_names(spreadsheet_id: str) -> list[str]:
    """
    Retrieve all sheet tab names from a Google Spreadsheet.
    
    This function fetches the list of all sheet (tab) names in the specified
    spreadsheet. This is used during session initialization to allow TAs to
    select which course sheet they want to record attendance for.
    
    Args:
        spreadsheet_id: The unique identifier from the Google Sheet URL
        
    Returns:
        List of sheet names (strings) in the order they appear in the spreadsheet
        
    Raises:
        gspread.exceptions.APIError: If there's an API error accessing the spreadsheet
        gspread.exceptions.SpreadsheetNotFound: If the spreadsheet doesn't exist
        
    Requirements: 1.4, 3.2
    
    Examples:
        >>> sheet_names = get_sheet_names("1abc...")
        >>> sheet_names
        ['CS101', 'CS102', 'MATH201']
    """
    client = get_gspread_client()
    spreadsheet = client.open_by_key(spreadsheet_id)
    
    # Get all worksheets and extract their titles
    worksheets = spreadsheet.worksheets()
    sheet_names = [worksheet.title for worksheet in worksheets]
    
    return sheet_names


def get_headers(spreadsheet_id: str, sheet_name: str) -> list[str]:
    """
    Retrieve column headers from row 1 of a specific sheet, filtered for attendance columns.
    
    This function fetches the header row (row 1) from the specified sheet and returns
    only the headers starting from column D (index 3) onwards. These columns represent
    attendance columns (e.g., "Week 1", "Week 2", etc.), while columns A-C typically
    contain student information (ID, Name, Email).
    
    Args:
        spreadsheet_id: The unique identifier from the Google Sheet URL
        sheet_name: The name of the specific sheet/tab to read from
        
    Returns:
        List of column header names starting from column D onwards.
        Empty strings in the header row are filtered out.
        
    Raises:
        gspread.exceptions.APIError: If there's an API error accessing the spreadsheet
        gspread.exceptions.WorksheetNotFound: If the specified sheet doesn't exist
        
    Requirements: 1.5, 3.3, 3.4
    
    Examples:
        >>> headers = get_headers("1abc...", "CS101")
        >>> headers
        ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    """
    client = get_gspread_client()
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(sheet_name)
    
    # Get all values from row 1 (header row)
    header_row = worksheet.row_values(1)
    
    # Filter headers starting from column D (index 3) onwards
    # Also filter out empty strings
    attendance_headers = [header for header in header_row[3:] if header.strip()]
    
    return attendance_headers



def find_student_id_column(headers: list[str]) -> int:
    """
    Identify which column contains the Student_ID by searching for specific header names.
    
    This function searches for headers matching "ID" or "رقم الجلوس" (Arabic for "seat number")
    in a case-insensitive manner. The search is limited to the first three columns (A-C)
    as per the expected sheet structure where student information is stored in the leftmost columns.
    
    Args:
        headers: List of column headers from the sheet (typically from columns A-C)
        
    Returns:
        Zero-based column index where the Student_ID column is found
        
    Raises:
        ValueError: If no Student_ID column is found in the provided headers
        
    Requirements: 1.6
    
    Examples:
        >>> find_student_id_column(['ID', 'Name', 'Email'])
        0
        >>> find_student_id_column(['Name', 'id', 'Email'])
        1
        >>> find_student_id_column(['Name', 'رقم الجلوس', 'Email'])
        1
        >>> find_student_id_column(['Name', 'Email', 'Phone'])
        Traceback (most recent call last):
            ...
        ValueError: Student_ID column not found. Expected 'ID' or 'رقم الجلوس' in columns A-C.
    """
    # Search only in the first 3 columns (A-C)
    search_range = min(len(headers), 3)
    
    for i in range(search_range):
        header = headers[i].strip().lower()
        # Check for "ID" or "رقم الجلوس" (case-insensitive)
        if header == "id" or header == "رقم الجلوس":
            return i
    
    # If not found, raise an error
    raise ValueError(
        "Student_ID column not found. Expected 'ID' or 'رقم الجلوس' in columns A-C."
    )



def find_student_row(spreadsheet_id: str, sheet_name: str, student_id: str) -> int | None:
    """
    Locate a student's row in the sheet by searching for their Student_ID.
    
    This function searches the Student_ID column (identified by headers "ID" or "رقم الجلوس")
    for a matching student ID value. The search is performed on all rows starting from row 2
    (since row 1 contains headers). The function returns the row index (1-based) where the
    student is found, or None if the student doesn't exist in the sheet.
    
    Args:
        spreadsheet_id: The unique identifier from the Google Sheet URL
        sheet_name: The name of the specific sheet/tab to search in
        student_id: The Student_ID value to search for
        
    Returns:
        Row index (1-based) where the student is found, or None if not found
        
    Raises:
        ValueError: If the Student_ID column is not found in the sheet
        gspread.exceptions.APIError: If there's an API error accessing the spreadsheet
        gspread.exceptions.WorksheetNotFound: If the specified sheet doesn't exist
        
    Requirements: 1.7
    
    Examples:
        >>> row = find_student_row("1abc...", "CS101", "20210001")
        >>> row
        2
        >>> row = find_student_row("1abc...", "CS101", "99999999")
        >>> row is None
        True
    """
    client = get_gspread_client()
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(sheet_name)
    
    # Get the header row to identify the Student_ID column
    header_row = worksheet.row_values(1)
    
    # Find which column contains the Student_ID
    student_id_col_index = find_student_id_column(header_row)
    
    # Get all values from the Student_ID column (1-based column index for gspread)
    # Column index in gspread is 1-based, so we add 1
    student_id_column_values = worksheet.col_values(student_id_col_index + 1)
    
    # Search for the student_id in the column (starting from row 2, index 1)
    # Row 1 is the header, so we start searching from index 1 onwards
    for i, cell_value in enumerate(student_id_column_values[1:], start=2):
        # Compare as strings, stripping whitespace
        if str(cell_value).strip() == str(student_id).strip():
            return i
    
    # Student not found
    return None



def mark_attendance(spreadsheet_id: str, sheet_name: str, row: int, column_name: str) -> None:
    """
    Mark attendance by writing "P" to the specified cell.
    
    This function writes the value "P" (for Present) to the cell at the intersection
    of the specified row and the column with the given header name. The column is
    identified by searching the header row for a matching column name.
    
    Args:
        spreadsheet_id: The unique identifier from the Google Sheet URL
        sheet_name: The name of the specific sheet/tab to write to
        row: The row number (1-based) where attendance should be marked
        column_name: The name of the attendance column (e.g., "Week 1", "Week 2")
        
    Raises:
        ValueError: If the specified column_name is not found in the header row
        gspread.exceptions.APIError: If there's an API error accessing the spreadsheet
        gspread.exceptions.WorksheetNotFound: If the specified sheet doesn't exist
        
    Requirements: 1.8
    
    Examples:
        >>> mark_attendance("1abc...", "CS101", 2, "Week 1")
        # Writes "P" to the cell at row 2 in the "Week 1" column
    """
    client = get_gspread_client()
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(sheet_name)
    
    # Get the header row to find the column index
    header_row = worksheet.row_values(1)
    
    # Find the column index by searching for the column_name
    try:
        # Find the index of the column (0-based)
        column_index = header_row.index(column_name)
        # Convert to 1-based index for gspread
        column_number = column_index + 1
    except ValueError:
        raise ValueError(
            f"Column '{column_name}' not found in sheet '{sheet_name}'. "
            f"Available columns: {', '.join(header_row)}"
        )
    
    # Write "P" to the cell at (row, column_number)
    worksheet.update_cell(row, column_number, "P")
