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
    only the attendance column headers. It automatically detects the sheet structure:
    - If column C is "Section": Returns headers from column D onwards (ID, Name, Section, Week 1, ...)
    - Otherwise: Returns headers from column C onwards (ID, Name, Week 1, ...) for backward compatibility
    
    The function filters out:
    - Empty headers
    - "Total Attendance" column (used for summary, not for marking attendance)
    
    This ensures compatibility with both old sheets (without Section column) and new sheets
    (with Section column and Total Attendance column).
    
    Args:
        spreadsheet_id: The unique identifier from the Google Sheet URL
        sheet_name: The name of the specific sheet/tab to read from
        
    Returns:
        List of attendance column header names (e.g., "Week 1", "Week 2", etc.).
        Empty strings and "Total Attendance" are filtered out.
        
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
    
    # Determine starting column based on sheet structure
    # Check if column C (index 2) is "Section" - if so, start from column D (index 3)
    # Otherwise, start from column C (index 2) for backward compatibility
    start_index = 2  # Default: column C
    if len(header_row) > 2:
        col_c_header = header_row[2].strip().lower() if isinstance(header_row[2], str) else str(header_row[2]).strip().lower()
        if col_c_header == "section":
            start_index = 3  # Skip Section column, start from column D
    
    # Filter headers starting from the determined column onwards
    # Also filter out empty strings and "Total Attendance" column
    attendance_headers = []
    for header in header_row[start_index:]:
        # Strip whitespace and check if there's any content
        cleaned_header = header.strip() if isinstance(header, str) else str(header).strip()
        
        # Skip empty headers and "Total Attendance" column
        if cleaned_header and cleaned_header.lower() != "total attendance":
            attendance_headers.append(cleaned_header)
    
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


def col_index_to_a1(col_index: int) -> str:
    """Convert a 0-based column index to A1 notation letter(s). Supports beyond Z (AA, AB, etc.)"""
    result = ""
    col_index += 1  # make 1-based
    while col_index > 0:
        col_index, remainder = divmod(col_index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def process_batch_attendance(
    spreadsheet_id: str, 
    sheet_name: str, 
    column_name: str, 
    student_ids: list[str]
) -> dict:
    """
    Process attendance for multiple students efficiently using batch operations.
    """
    try:
        client = get_gspread_client()
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        
        # Get header row to find columns
        header_row = worksheet.row_values(1)
        
        # Find Student_ID column
        student_id_col_index = find_student_id_column(header_row)
        
        # Find attendance column
        try:
            attendance_col_index = header_row.index(column_name)
        except ValueError:
            raise ValueError(
                f"Column '{column_name}' not found in sheet '{sheet_name}'. "
                f"Available columns: {', '.join(header_row)}"
            )
        
        # Get all data from the sheet in one API call
        all_data = worksheet.get_all_values()
        
        # Create a mapping of student_id -> row_number
        student_row_map = {}
        for i, row_data in enumerate(all_data[1:], start=2):  # Skip header row
            if len(row_data) > student_id_col_index:
                cell_value = str(row_data[student_id_col_index]).strip()
                if cell_value:
                    student_row_map[cell_value] = i
        
        # Prepare batch updates
        successful = []
        not_found = []
        failed = []
        batch_updates = []
        
        col_letter = col_index_to_a1(attendance_col_index)
        
        for student_id in student_ids:
            student_id_str = str(student_id).strip()
            
            if student_id_str in student_row_map:
                row_number = student_row_map[student_id_str]
                cell_address = f"{col_letter}{row_number}"
                batch_updates.append({
                    'range': cell_address,
                    'values': [['P']]
                })
                successful.append(student_id)
            else:
                not_found.append(student_id)
        
        # Perform batch update in one API call
        if batch_updates:
            worksheet.batch_update(batch_updates)
        
        return {
            'successful': successful,
            'not_found': not_found,
            'failed': failed
        }
        
    except Exception as e:
        # Re-raise so the caller can surface the actual error message
        raise
