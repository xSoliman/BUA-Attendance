"""
Unit tests for Google Sheets service module.

Tests Requirements: 1.2, 1.3
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
import gspread
from backend.sheets_service import validate_spreadsheet_access


class TestValidateSpreadsheetAccess:
    """Test spreadsheet access validation."""
    
    def test_valid_spreadsheet_access(self):
        """Test successful validation when spreadsheet is accessible."""
        spreadsheet_id = "1abc123def456"
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_client = MagicMock()
            mock_spreadsheet = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            result = validate_spreadsheet_access(spreadsheet_id)
            
            assert result['valid'] is True
            assert result['message'] == "Spreadsheet accessible"
            mock_client.open_by_key.assert_called_once_with(spreadsheet_id)
    
    def test_403_permission_denied(self):
        """Test handling of 403 Forbidden error (permission denied)."""
        spreadsheet_id = "1abc123def456"
        service_email = "test@test-project.iam.gserviceaccount.com"
        
        # Create a mock response object with status_code
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_response.json.return_value = {"error": "Forbidden"}
        
        # Create APIError with the mock response
        api_error = gspread.exceptions.APIError(mock_response)
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.open_by_key.side_effect = api_error
            mock_get_client.return_value = mock_client
            
            with patch('backend.sheets_service.get_service_account_email') as mock_get_email:
                mock_get_email.return_value = service_email
                
                result = validate_spreadsheet_access(spreadsheet_id)
                
                assert result['valid'] is False
                assert service_email in result['message']
                assert "access denied" in result['message'].lower() or "not found" in result['message'].lower()
    
    def test_other_api_error(self):
        """Test handling of other API errors (non-403)."""
        spreadsheet_id = "1abc123def456"
        
        # Create a mock response object with status_code 500
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.return_value = {"error": "Internal Server Error"}
        
        # Create APIError with the mock response
        api_error = gspread.exceptions.APIError(mock_response)
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.open_by_key.side_effect = api_error
            mock_get_client.return_value = mock_client
            
            result = validate_spreadsheet_access(spreadsheet_id)
            
            assert result['valid'] is False
            assert "Google Sheets API error" in result['message']
    
    def test_spreadsheet_not_found(self):
        """Test handling of SpreadsheetNotFound exception."""
        spreadsheet_id = "1invalid_id"
        service_email = "test@test-project.iam.gserviceaccount.com"
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.open_by_key.side_effect = gspread.exceptions.SpreadsheetNotFound
            mock_get_client.return_value = mock_client
            
            with patch('backend.sheets_service.get_service_account_email') as mock_get_email:
                mock_get_email.return_value = service_email
                
                result = validate_spreadsheet_access(spreadsheet_id)
                
                assert result['valid'] is False
                assert "not found" in result['message'].lower()
                assert service_email in result['message']
    
    def test_unexpected_exception(self):
        """Test handling of unexpected exceptions."""
        spreadsheet_id = "1abc123def456"
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.open_by_key.side_effect = Exception("Unexpected error occurred")
            mock_get_client.return_value = mock_client
            
            result = validate_spreadsheet_access(spreadsheet_id)
            
            assert result['valid'] is False
            assert "Unexpected error" in result['message']
    
    def test_empty_spreadsheet_id(self):
        """Test validation with empty spreadsheet ID."""
        spreadsheet_id = ""
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.open_by_key.side_effect = Exception("Invalid spreadsheet ID")
            mock_get_client.return_value = mock_client
            
            result = validate_spreadsheet_access(spreadsheet_id)
            
            assert result['valid'] is False
            assert "error" in result['message'].lower()
    
    def test_whitespace_spreadsheet_id(self):
        """Test validation with whitespace-only spreadsheet ID."""
        spreadsheet_id = "   "
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.open_by_key.side_effect = gspread.exceptions.SpreadsheetNotFound
            mock_get_client.return_value = mock_client
            
            with patch('backend.sheets_service.get_service_account_email') as mock_get_email:
                mock_get_email.return_value = "test@test.com"
                
                result = validate_spreadsheet_access(spreadsheet_id)
                
                assert result['valid'] is False



class TestGetSheetNames:
    """Test sheet names retrieval functionality."""
    
    def test_get_sheet_names_success(self):
        """Test successful retrieval of sheet names."""
        spreadsheet_id = "1abc123def456"
        expected_sheet_names = ["CS101", "CS102", "MATH201"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            # Create mock worksheets
            mock_worksheets = []
            for name in expected_sheet_names:
                mock_worksheet = MagicMock()
                mock_worksheet.title = name
                mock_worksheets.append(mock_worksheet)
            
            # Setup mock client and spreadsheet
            mock_client = MagicMock()
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheets.return_value = mock_worksheets
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_sheet_names
            result = get_sheet_names(spreadsheet_id)
            
            assert result == expected_sheet_names
            mock_client.open_by_key.assert_called_once_with(spreadsheet_id)
            mock_spreadsheet.worksheets.assert_called_once()
    
    def test_get_sheet_names_single_sheet(self):
        """Test retrieval when spreadsheet has only one sheet."""
        spreadsheet_id = "1abc123def456"
        expected_sheet_names = ["Sheet1"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.title = "Sheet1"
            
            mock_client = MagicMock()
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheets.return_value = [mock_worksheet]
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_sheet_names
            result = get_sheet_names(spreadsheet_id)
            
            assert result == expected_sheet_names
            assert len(result) == 1
    
    def test_get_sheet_names_with_special_characters(self):
        """Test retrieval of sheet names containing special characters."""
        spreadsheet_id = "1abc123def456"
        expected_sheet_names = ["CS-101", "Math 201", "Lab_Session", "علوم الحاسب"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheets = []
            for name in expected_sheet_names:
                mock_worksheet = MagicMock()
                mock_worksheet.title = name
                mock_worksheets.append(mock_worksheet)
            
            mock_client = MagicMock()
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheets.return_value = mock_worksheets
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_sheet_names
            result = get_sheet_names(spreadsheet_id)
            
            assert result == expected_sheet_names
    
    def test_get_sheet_names_preserves_order(self):
        """Test that sheet names are returned in the correct order."""
        spreadsheet_id = "1abc123def456"
        expected_sheet_names = ["First", "Second", "Third", "Fourth"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheets = []
            for name in expected_sheet_names:
                mock_worksheet = MagicMock()
                mock_worksheet.title = name
                mock_worksheets.append(mock_worksheet)
            
            mock_client = MagicMock()
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheets.return_value = mock_worksheets
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_sheet_names
            result = get_sheet_names(spreadsheet_id)
            
            assert result == expected_sheet_names
            # Verify order is preserved
            for i, name in enumerate(expected_sheet_names):
                assert result[i] == name
    
    def test_get_sheet_names_api_error(self):
        """Test handling of API errors when retrieving sheet names."""
        spreadsheet_id = "1abc123def456"
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.return_value = {"error": "Internal Server Error"}
        
        api_error = gspread.exceptions.APIError(mock_response)
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.open_by_key.side_effect = api_error
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_sheet_names
            
            with pytest.raises(gspread.exceptions.APIError):
                get_sheet_names(spreadsheet_id)
    
    def test_get_sheet_names_spreadsheet_not_found(self):
        """Test handling when spreadsheet doesn't exist."""
        spreadsheet_id = "1invalid_id"
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.open_by_key.side_effect = gspread.exceptions.SpreadsheetNotFound
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_sheet_names
            
            with pytest.raises(gspread.exceptions.SpreadsheetNotFound):
                get_sheet_names(spreadsheet_id)
    
    def test_get_sheet_names_many_sheets(self):
        """Test retrieval with a large number of sheets."""
        spreadsheet_id = "1abc123def456"
        # Create 20 sheet names
        expected_sheet_names = [f"Sheet{i}" for i in range(1, 21)]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheets = []
            for name in expected_sheet_names:
                mock_worksheet = MagicMock()
                mock_worksheet.title = name
                mock_worksheets.append(mock_worksheet)
            
            mock_client = MagicMock()
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheets.return_value = mock_worksheets
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_sheet_names
            result = get_sheet_names(spreadsheet_id)
            
            assert result == expected_sheet_names
            assert len(result) == 20



class TestGetHeaders:
    """Test header row fetching functionality."""
    
    def test_get_headers_success(self):
        """Test successful retrieval of attendance column headers."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        # Row 1 with columns A-C as student info, D onwards as attendance
        full_header_row = ["ID", "Name", "Email", "Week 1", "Week 2", "Week 3", "Week 4"]
        expected_headers = ["Week 1", "Week 2", "Week 3", "Week 4"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            # Setup mock worksheet
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = full_header_row
            
            # Setup mock spreadsheet
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            # Setup mock client
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_headers
            result = get_headers(spreadsheet_id, sheet_name)
            
            assert result == expected_headers
            mock_client.open_by_key.assert_called_once_with(spreadsheet_id)
            mock_spreadsheet.worksheet.assert_called_once_with(sheet_name)
            mock_worksheet.row_values.assert_called_once_with(1)
    
    def test_get_headers_filters_from_column_d(self):
        """Test that headers are filtered starting from column D (index 3)."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        full_header_row = ["ID", "Name", "Email", "Week 1", "Week 2"]
        expected_headers = ["Week 1", "Week 2"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = full_header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_headers
            result = get_headers(spreadsheet_id, sheet_name)
            
            # Verify that columns A-C are not included
            assert "ID" not in result
            assert "Name" not in result
            assert "Email" not in result
            # Verify that columns D onwards are included
            assert result == expected_headers
    
    def test_get_headers_filters_empty_strings(self):
        """Test that empty header cells are filtered out."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        # Header row with some empty cells
        full_header_row = ["ID", "Name", "Email", "Week 1", "", "Week 2", "  ", "Week 3"]
        expected_headers = ["Week 1", "Week 2", "Week 3"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = full_header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_headers
            result = get_headers(spreadsheet_id, sheet_name)
            
            assert result == expected_headers
            # Verify empty strings and whitespace-only strings are filtered
            assert "" not in result
            assert "  " not in result
    
    def test_get_headers_no_attendance_columns(self):
        """Test when there are no attendance columns (only A-C populated)."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        full_header_row = ["ID", "Name", "Email"]
        expected_headers = []
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = full_header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_headers
            result = get_headers(spreadsheet_id, sheet_name)
            
            assert result == expected_headers
            assert len(result) == 0
    
    def test_get_headers_with_arabic_headers(self):
        """Test retrieval of headers with Arabic text."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        full_header_row = ["رقم الجلوس", "الاسم", "البريد", "الأسبوع 1", "الأسبوع 2"]
        expected_headers = ["الأسبوع 1", "الأسبوع 2"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = full_header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_headers
            result = get_headers(spreadsheet_id, sheet_name)
            
            assert result == expected_headers
    
    def test_get_headers_many_columns(self):
        """Test retrieval with many attendance columns."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        # Create header row with 15 attendance columns
        attendance_cols = [f"Week {i}" for i in range(1, 16)]
        full_header_row = ["ID", "Name", "Email"] + attendance_cols
        expected_headers = attendance_cols
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = full_header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_headers
            result = get_headers(spreadsheet_id, sheet_name)
            
            assert result == expected_headers
            assert len(result) == 15
    
    def test_get_headers_worksheet_not_found(self):
        """Test handling when specified worksheet doesn't exist."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "NonExistentSheet"
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.side_effect = gspread.exceptions.WorksheetNotFound
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_headers
            
            with pytest.raises(gspread.exceptions.WorksheetNotFound):
                get_headers(spreadsheet_id, sheet_name)
    
    def test_get_headers_api_error(self):
        """Test handling of API errors when retrieving headers."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.return_value = {"error": "Internal Server Error"}
        
        api_error = gspread.exceptions.APIError(mock_response)
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.open_by_key.side_effect = api_error
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_headers
            
            with pytest.raises(gspread.exceptions.APIError):
                get_headers(spreadsheet_id, sheet_name)
    
    def test_get_headers_preserves_order(self):
        """Test that header order is preserved."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        full_header_row = ["ID", "Name", "Email", "Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]
        expected_headers = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = full_header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import get_headers
            result = get_headers(spreadsheet_id, sheet_name)
            
            assert result == expected_headers
            # Verify order is preserved
            for i, header in enumerate(expected_headers):
                assert result[i] == header



class TestFindStudentIdColumn:
    """Test Student_ID column identification functionality."""
    
    def test_find_student_id_column_first_position(self):
        """Test finding Student_ID column in first position (column A)."""
        headers = ["ID", "Name", "Email"]
        
        from backend.sheets_service import find_student_id_column
        result = find_student_id_column(headers)
        
        assert result == 0
    
    def test_find_student_id_column_second_position(self):
        """Test finding Student_ID column in second position (column B)."""
        headers = ["Name", "ID", "Email"]
        
        from backend.sheets_service import find_student_id_column
        result = find_student_id_column(headers)
        
        assert result == 1
    
    def test_find_student_id_column_third_position(self):
        """Test finding Student_ID column in third position (column C)."""
        headers = ["Name", "Email", "ID"]
        
        from backend.sheets_service import find_student_id_column
        result = find_student_id_column(headers)
        
        assert result == 2
    
    def test_find_student_id_column_case_insensitive(self):
        """Test that column identification is case-insensitive."""
        # Test lowercase
        headers_lower = ["id", "Name", "Email"]
        from backend.sheets_service import find_student_id_column
        result_lower = find_student_id_column(headers_lower)
        assert result_lower == 0
        
        # Test uppercase
        headers_upper = ["ID", "Name", "Email"]
        result_upper = find_student_id_column(headers_upper)
        assert result_upper == 0
        
        # Test mixed case
        headers_mixed = ["Id", "Name", "Email"]
        result_mixed = find_student_id_column(headers_mixed)
        assert result_mixed == 0
    
    def test_find_student_id_column_arabic(self):
        """Test finding Student_ID column with Arabic header."""
        headers = ["رقم الجلوس", "الاسم", "البريد"]
        
        from backend.sheets_service import find_student_id_column
        result = find_student_id_column(headers)
        
        assert result == 0
    
    def test_find_student_id_column_arabic_second_position(self):
        """Test finding Arabic Student_ID column in second position."""
        headers = ["الاسم", "رقم الجلوس", "البريد"]
        
        from backend.sheets_service import find_student_id_column
        result = find_student_id_column(headers)
        
        assert result == 1
    
    def test_find_student_id_column_with_whitespace(self):
        """Test finding Student_ID column with leading/trailing whitespace."""
        headers = ["  ID  ", "Name", "Email"]
        
        from backend.sheets_service import find_student_id_column
        result = find_student_id_column(headers)
        
        assert result == 0
    
    def test_find_student_id_column_not_found(self):
        """Test error when Student_ID column is not found."""
        headers = ["Name", "Email", "Phone"]
        
        from backend.sheets_service import find_student_id_column
        
        with pytest.raises(ValueError) as exc_info:
            find_student_id_column(headers)
        
        assert "Student_ID column not found" in str(exc_info.value)
        assert "ID" in str(exc_info.value) or "رقم الجلوس" in str(exc_info.value)
    
    def test_find_student_id_column_beyond_third_column(self):
        """Test that search is limited to first three columns (A-C)."""
        # ID is in 4th position (column D), should not be found
        headers = ["Name", "Email", "Phone", "ID"]
        
        from backend.sheets_service import find_student_id_column
        
        with pytest.raises(ValueError) as exc_info:
            find_student_id_column(headers)
        
        assert "Student_ID column not found" in str(exc_info.value)
    
    def test_find_student_id_column_empty_headers(self):
        """Test error when headers list is empty."""
        headers = []
        
        from backend.sheets_service import find_student_id_column
        
        with pytest.raises(ValueError) as exc_info:
            find_student_id_column(headers)
        
        assert "Student_ID column not found" in str(exc_info.value)
    
    def test_find_student_id_column_single_header(self):
        """Test with single header that matches."""
        headers = ["ID"]
        
        from backend.sheets_service import find_student_id_column
        result = find_student_id_column(headers)
        
        assert result == 0
    
    def test_find_student_id_column_two_headers(self):
        """Test with two headers where second matches."""
        headers = ["Name", "ID"]
        
        from backend.sheets_service import find_student_id_column
        result = find_student_id_column(headers)
        
        assert result == 1
    
    def test_find_student_id_column_prefers_first_match(self):
        """Test that function returns first match when multiple ID columns exist."""
        # Both first and third columns are "ID", should return first
        headers = ["ID", "Name", "ID"]
        
        from backend.sheets_service import find_student_id_column
        result = find_student_id_column(headers)
        
        assert result == 0
    
    def test_find_student_id_column_partial_match_not_found(self):
        """Test that partial matches don't count (e.g., 'Student_ID' != 'ID')."""
        headers = ["Student_ID", "Name", "Email"]
        
        from backend.sheets_service import find_student_id_column
        
        with pytest.raises(ValueError) as exc_info:
            find_student_id_column(headers)
        
        assert "Student_ID column not found" in str(exc_info.value)
    
    def test_find_student_id_column_with_special_characters(self):
        """Test that headers with special characters don't match."""
        headers = ["ID#", "Name", "Email"]
        
        from backend.sheets_service import find_student_id_column
        
        with pytest.raises(ValueError) as exc_info:
            find_student_id_column(headers)
        
        assert "Student_ID column not found" in str(exc_info.value)



class TestFindStudentRow:
    """Test student row lookup functionality."""
    
    def test_find_student_row_found_first_row(self):
        """Test finding student in the first data row (row 2)."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        student_id = "20210001"
        
        # Mock header row and student ID column
        header_row = ["ID", "Name", "Email"]
        student_id_column = ["ID", "20210001", "20210002", "20210003"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            mock_worksheet.col_values.return_value = student_id_column
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            result = find_student_row(spreadsheet_id, sheet_name, student_id)
            
            assert result == 2
            mock_worksheet.col_values.assert_called_once_with(1)  # Column A (1-based)
    
    def test_find_student_row_found_middle_row(self):
        """Test finding student in a middle row."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        student_id = "20210005"
        
        header_row = ["ID", "Name", "Email"]
        student_id_column = ["ID", "20210001", "20210002", "20210003", "20210004", "20210005", "20210006"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            mock_worksheet.col_values.return_value = student_id_column
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            result = find_student_row(spreadsheet_id, sheet_name, student_id)
            
            assert result == 6
    
    def test_find_student_row_found_last_row(self):
        """Test finding student in the last row."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        student_id = "20210003"
        
        header_row = ["ID", "Name", "Email"]
        student_id_column = ["ID", "20210001", "20210002", "20210003"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            mock_worksheet.col_values.return_value = student_id_column
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            result = find_student_row(spreadsheet_id, sheet_name, student_id)
            
            assert result == 4
    
    def test_find_student_row_not_found(self):
        """Test when student ID is not found in the sheet."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        student_id = "99999999"
        
        header_row = ["ID", "Name", "Email"]
        student_id_column = ["ID", "20210001", "20210002", "20210003"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            mock_worksheet.col_values.return_value = student_id_column
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            result = find_student_row(spreadsheet_id, sheet_name, student_id)
            
            assert result is None
    
    def test_find_student_row_with_whitespace(self):
        """Test finding student ID with leading/trailing whitespace."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        student_id = "  20210001  "
        
        header_row = ["ID", "Name", "Email"]
        student_id_column = ["ID", "20210001", "20210002", "20210003"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            mock_worksheet.col_values.return_value = student_id_column
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            result = find_student_row(spreadsheet_id, sheet_name, student_id)
            
            assert result == 2
    
    def test_find_student_row_cell_has_whitespace(self):
        """Test finding student when cell value has whitespace."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        student_id = "20210001"
        
        header_row = ["ID", "Name", "Email"]
        student_id_column = ["ID", "  20210001  ", "20210002", "20210003"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            mock_worksheet.col_values.return_value = student_id_column
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            result = find_student_row(spreadsheet_id, sheet_name, student_id)
            
            assert result == 2
    
    def test_find_student_row_id_in_second_column(self):
        """Test finding student when ID column is in position B."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        student_id = "20210001"
        
        header_row = ["Name", "ID", "Email"]
        student_id_column = ["ID", "20210001", "20210002", "20210003"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            mock_worksheet.col_values.return_value = student_id_column
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            result = find_student_row(spreadsheet_id, sheet_name, student_id)
            
            assert result == 2
            mock_worksheet.col_values.assert_called_once_with(2)  # Column B (1-based)
    
    def test_find_student_row_arabic_header(self):
        """Test finding student with Arabic ID column header."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        student_id = "20210001"
        
        header_row = ["رقم الجلوس", "الاسم", "البريد"]
        student_id_column = ["رقم الجلوس", "20210001", "20210002", "20210003"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            mock_worksheet.col_values.return_value = student_id_column
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            result = find_student_row(spreadsheet_id, sheet_name, student_id)
            
            assert result == 2
    
    def test_find_student_row_empty_sheet(self):
        """Test when sheet has only header row (no students)."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        student_id = "20210001"
        
        header_row = ["ID", "Name", "Email"]
        student_id_column = ["ID"]  # Only header, no data rows
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            mock_worksheet.col_values.return_value = student_id_column
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            result = find_student_row(spreadsheet_id, sheet_name, student_id)
            
            assert result is None
    
    def test_find_student_row_no_id_column(self):
        """Test error when Student_ID column is not found."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        student_id = "20210001"
        
        header_row = ["Name", "Email", "Phone"]  # No ID column
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            
            with pytest.raises(ValueError) as exc_info:
                find_student_row(spreadsheet_id, sheet_name, student_id)
            
            assert "Student_ID column not found" in str(exc_info.value)
    
    def test_find_student_row_worksheet_not_found(self):
        """Test error when worksheet doesn't exist."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "NonExistentSheet"
        student_id = "20210001"
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.side_effect = gspread.exceptions.WorksheetNotFound
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            
            with pytest.raises(gspread.exceptions.WorksheetNotFound):
                find_student_row(spreadsheet_id, sheet_name, student_id)
    
    def test_find_student_row_case_sensitive(self):
        """Test that student ID matching is case-sensitive."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        student_id = "abc123"
        
        header_row = ["ID", "Name", "Email"]
        student_id_column = ["ID", "ABC123", "20210002", "20210003"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            mock_worksheet.col_values.return_value = student_id_column
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            result = find_student_row(spreadsheet_id, sheet_name, student_id)
            
            # Should not find "abc123" when cell contains "ABC123"
            assert result is None
    
    def test_find_student_row_numeric_id(self):
        """Test finding student with numeric ID."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        student_id = "20210001"
        
        header_row = ["ID", "Name", "Email"]
        # Simulate numeric values from spreadsheet (gspread may return numbers)
        student_id_column = ["ID", 20210001, 20210002, 20210003]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            mock_worksheet.col_values.return_value = student_id_column
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            result = find_student_row(spreadsheet_id, sheet_name, student_id)
            
            # Should find match when comparing as strings
            assert result == 2
    
    def test_find_student_row_returns_first_match(self):
        """Test that function returns first match when duplicate IDs exist."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        student_id = "20210001"
        
        header_row = ["ID", "Name", "Email"]
        student_id_column = ["ID", "20210001", "20210002", "20210001"]  # Duplicate at row 4
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            mock_worksheet.col_values.return_value = student_id_column
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            result = find_student_row(spreadsheet_id, sheet_name, student_id)
            
            # Should return first match (row 2)
            assert result == 2
    
    def test_find_student_row_empty_string_id(self):
        """Test searching for empty string student ID."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        student_id = ""
        
        header_row = ["ID", "Name", "Email"]
        student_id_column = ["ID", "20210001", "", "20210003"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            mock_worksheet.col_values.return_value = student_id_column
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import find_student_row
            result = find_student_row(spreadsheet_id, sheet_name, student_id)
            
            # Should find the empty cell at row 3
            assert result == 3



class TestMarkAttendance:
    """Test attendance marking functionality."""
    
    def test_mark_attendance_success(self):
        """Test successful attendance marking."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        row = 2
        column_name = "Week 1"
        
        header_row = ["ID", "Name", "Email", "Week 1", "Week 2", "Week 3"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import mark_attendance
            mark_attendance(spreadsheet_id, sheet_name, row, column_name)
            
            # Verify update_cell was called with correct parameters
            # Column "Week 1" is at index 3 (0-based), so column number is 4 (1-based)
            mock_worksheet.update_cell.assert_called_once_with(2, 4, "P")
    
    def test_mark_attendance_different_column(self):
        """Test marking attendance in different columns."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        row = 3
        column_name = "Week 3"
        
        header_row = ["ID", "Name", "Email", "Week 1", "Week 2", "Week 3"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import mark_attendance
            mark_attendance(spreadsheet_id, sheet_name, row, column_name)
            
            # Column "Week 3" is at index 5 (0-based), so column number is 6 (1-based)
            mock_worksheet.update_cell.assert_called_once_with(3, 6, "P")
    
    def test_mark_attendance_first_column(self):
        """Test marking attendance in the first column (column A)."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        row = 2
        column_name = "ID"
        
        header_row = ["ID", "Name", "Email", "Week 1"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import mark_attendance
            mark_attendance(spreadsheet_id, sheet_name, row, column_name)
            
            # Column "ID" is at index 0 (0-based), so column number is 1 (1-based)
            mock_worksheet.update_cell.assert_called_once_with(2, 1, "P")
    
    def test_mark_attendance_last_column(self):
        """Test marking attendance in the last column."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        row = 5
        column_name = "Week 15"
        
        header_row = ["ID", "Name", "Email"] + [f"Week {i}" for i in range(1, 16)]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import mark_attendance
            mark_attendance(spreadsheet_id, sheet_name, row, column_name)
            
            # Column "Week 15" is at index 17 (0-based), so column number is 18 (1-based)
            mock_worksheet.update_cell.assert_called_once_with(5, 18, "P")
    
    def test_mark_attendance_column_not_found(self):
        """Test error when column name is not found."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        row = 2
        column_name = "Week 99"
        
        header_row = ["ID", "Name", "Email", "Week 1", "Week 2"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import mark_attendance
            
            with pytest.raises(ValueError) as exc_info:
                mark_attendance(spreadsheet_id, sheet_name, row, column_name)
            
            assert "Column 'Week 99' not found" in str(exc_info.value)
            assert sheet_name in str(exc_info.value)
            # Verify update_cell was not called
            mock_worksheet.update_cell.assert_not_called()
    
    def test_mark_attendance_arabic_column(self):
        """Test marking attendance with Arabic column name."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        row = 2
        column_name = "الأسبوع 1"
        
        header_row = ["رقم الجلوس", "الاسم", "البريد", "الأسبوع 1", "الأسبوع 2"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import mark_attendance
            mark_attendance(spreadsheet_id, sheet_name, row, column_name)
            
            # Column "الأسبوع 1" is at index 3 (0-based), so column number is 4 (1-based)
            mock_worksheet.update_cell.assert_called_once_with(2, 4, "P")
    
    def test_mark_attendance_worksheet_not_found(self):
        """Test error when worksheet doesn't exist."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "NonExistentSheet"
        row = 2
        column_name = "Week 1"
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.side_effect = gspread.exceptions.WorksheetNotFound
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import mark_attendance
            
            with pytest.raises(gspread.exceptions.WorksheetNotFound):
                mark_attendance(spreadsheet_id, sheet_name, row, column_name)
    
    def test_mark_attendance_api_error(self):
        """Test handling of API errors when marking attendance."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        row = 2
        column_name = "Week 1"
        
        header_row = ["ID", "Name", "Email", "Week 1"]
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.return_value = {"error": "Internal Server Error"}
        
        api_error = gspread.exceptions.APIError(mock_response)
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            mock_worksheet.update_cell.side_effect = api_error
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import mark_attendance
            
            with pytest.raises(gspread.exceptions.APIError):
                mark_attendance(spreadsheet_id, sheet_name, row, column_name)
    
    def test_mark_attendance_multiple_rows(self):
        """Test marking attendance for different rows."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        column_name = "Week 1"
        
        header_row = ["ID", "Name", "Email", "Week 1", "Week 2"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import mark_attendance
            
            # Mark attendance for row 2
            mark_attendance(spreadsheet_id, sheet_name, 2, column_name)
            mock_worksheet.update_cell.assert_called_with(2, 4, "P")
            
            # Mark attendance for row 5
            mark_attendance(spreadsheet_id, sheet_name, 5, column_name)
            mock_worksheet.update_cell.assert_called_with(5, 4, "P")
            
            # Mark attendance for row 10
            mark_attendance(spreadsheet_id, sheet_name, 10, column_name)
            mock_worksheet.update_cell.assert_called_with(10, 4, "P")
            
            # Verify update_cell was called 3 times
            assert mock_worksheet.update_cell.call_count == 3
    
    def test_mark_attendance_case_sensitive_column(self):
        """Test that column name matching is case-sensitive."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        row = 2
        column_name = "week 1"  # lowercase
        
        header_row = ["ID", "Name", "Email", "Week 1", "Week 2"]  # uppercase W
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import mark_attendance
            
            # Should raise ValueError because "week 1" != "Week 1"
            with pytest.raises(ValueError) as exc_info:
                mark_attendance(spreadsheet_id, sheet_name, row, column_name)
            
            assert "Column 'week 1' not found" in str(exc_info.value)
    
    def test_mark_attendance_empty_column_name(self):
        """Test error when column name is empty string."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        row = 2
        column_name = ""
        
        header_row = ["ID", "Name", "Email", "Week 1", "Week 2"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import mark_attendance
            
            with pytest.raises(ValueError) as exc_info:
                mark_attendance(spreadsheet_id, sheet_name, row, column_name)
            
            assert "Column '' not found" in str(exc_info.value)
    
    def test_mark_attendance_writes_p_value(self):
        """Test that the function writes exactly 'P' to the cell."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        row = 2
        column_name = "Week 1"
        
        header_row = ["ID", "Name", "Email", "Week 1"]
        
        with patch('backend.sheets_service.get_gspread_client') as mock_get_client:
            mock_worksheet = MagicMock()
            mock_worksheet.row_values.return_value = header_row
            
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            
            mock_client = MagicMock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_get_client.return_value = mock_client
            
            from backend.sheets_service import mark_attendance
            mark_attendance(spreadsheet_id, sheet_name, row, column_name)
            
            # Verify the third argument is exactly "P"
            call_args = mock_worksheet.update_cell.call_args
            assert call_args[0][2] == "P"



class TestProcessAttendance:
    """Test process_attendance function that combines lookup and marking."""
    
    def test_process_attendance_success(self):
        """Test successful attendance recording when student is found."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        column_name = "Week 1"
        student_id = "20210001"
        
        with patch('backend.attendance_service.find_student_row') as mock_find_row, \
             patch('backend.attendance_service.mark_attendance') as mock_mark:
            # Mock student found at row 2
            mock_find_row.return_value = 2
            
            from backend.attendance_service import process_attendance, AttendanceStatus
            result = process_attendance(spreadsheet_id, sheet_name, column_name, student_id)
            
            # Verify result
            assert result.status == AttendanceStatus.SUCCESS
            assert result.message == "Attendance recorded"
            
            # Verify functions were called correctly
            mock_find_row.assert_called_once_with(spreadsheet_id, sheet_name, student_id)
            mock_mark.assert_called_once_with(spreadsheet_id, sheet_name, 2, column_name)
    
    def test_process_attendance_student_not_found(self):
        """Test handling when student is not found in the sheet."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        column_name = "Week 1"
        student_id = "99999999"
        
        with patch('backend.attendance_service.find_student_row') as mock_find_row, \
             patch('backend.attendance_service.mark_attendance') as mock_mark:
            # Mock student not found
            mock_find_row.return_value = None
            
            from backend.attendance_service import process_attendance, AttendanceStatus
            result = process_attendance(spreadsheet_id, sheet_name, column_name, student_id)
            
            # Verify result
            assert result.status == AttendanceStatus.NOT_FOUND
            assert result.message == "Student Not Found"
            
            # Verify find_student_row was called
            mock_find_row.assert_called_once_with(spreadsheet_id, sheet_name, student_id)
            
            # Verify mark_attendance was NOT called (no sheet modification)
            mock_mark.assert_not_called()
    
    def test_process_attendance_no_sheet_modification_on_not_found(self):
        """Test that sheet is not modified when student is not found."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        column_name = "Week 1"
        student_id = "99999999"
        
        with patch('backend.attendance_service.find_student_row') as mock_find_row, \
             patch('backend.attendance_service.mark_attendance') as mock_mark:
            # Mock student not found
            mock_find_row.return_value = None
            
            from backend.attendance_service import process_attendance
            result = process_attendance(spreadsheet_id, sheet_name, column_name, student_id)
            
            # Verify mark_attendance was never called
            assert mock_mark.call_count == 0
    
    def test_process_attendance_error_handling(self):
        """Test error handling when an exception occurs during processing."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        column_name = "Week 1"
        student_id = "20210001"
        
        with patch('backend.attendance_service.find_student_row') as mock_find_row:
            # Mock an exception during lookup
            mock_find_row.side_effect = Exception("Network error")
            
            from backend.attendance_service import process_attendance, AttendanceStatus
            result = process_attendance(spreadsheet_id, sheet_name, column_name, student_id)
            
            # Verify error result
            assert result.status == AttendanceStatus.ERROR
            assert "Failed to record attendance" in result.message
            assert "Network error" in result.message
    
    def test_process_attendance_error_during_marking(self):
        """Test error handling when marking attendance fails."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        column_name = "Week 1"
        student_id = "20210001"
        
        with patch('backend.attendance_service.find_student_row') as mock_find_row, \
             patch('backend.attendance_service.mark_attendance') as mock_mark:
            # Mock student found
            mock_find_row.return_value = 2
            # Mock error during marking
            mock_mark.side_effect = ValueError("Column 'Week 1' not found")
            
            from backend.attendance_service import process_attendance, AttendanceStatus
            result = process_attendance(spreadsheet_id, sheet_name, column_name, student_id)
            
            # Verify error result
            assert result.status == AttendanceStatus.ERROR
            assert "Failed to record attendance" in result.message
            assert "Column 'Week 1' not found" in result.message
    
    def test_process_attendance_with_different_student_ids(self):
        """Test processing attendance for different student IDs."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        column_name = "Week 1"
        
        test_cases = [
            ("20210001", 2, True),   # Found at row 2
            ("20210002", 3, True),   # Found at row 3
            ("99999999", None, False),  # Not found
            ("12345678", 10, True),  # Found at row 10
        ]
        
        from backend.attendance_service import process_attendance, AttendanceStatus
        
        for student_id, row, should_succeed in test_cases:
            with patch('backend.attendance_service.find_student_row') as mock_find_row, \
                 patch('backend.attendance_service.mark_attendance') as mock_mark:
                mock_find_row.return_value = row
                
                result = process_attendance(spreadsheet_id, sheet_name, column_name, student_id)
                
                if should_succeed:
                    assert result.status == AttendanceStatus.SUCCESS
                    assert result.message == "Attendance recorded"
                    mock_mark.assert_called_once()
                else:
                    assert result.status == AttendanceStatus.NOT_FOUND
                    assert result.message == "Student Not Found"
                    mock_mark.assert_not_called()
    
    def test_process_attendance_with_whitespace_student_id(self):
        """Test processing attendance with student ID containing whitespace."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        column_name = "Week 1"
        student_id = "  20210001  "
        
        with patch('backend.attendance_service.find_student_row') as mock_find_row, \
             patch('backend.attendance_service.mark_attendance') as mock_mark:
            mock_find_row.return_value = 2
            
            from backend.attendance_service import process_attendance, AttendanceStatus
            result = process_attendance(spreadsheet_id, sheet_name, column_name, student_id)
            
            # Verify result
            assert result.status == AttendanceStatus.SUCCESS
            
            # Verify find_student_row was called with the whitespace-containing ID
            # (the function should handle whitespace internally)
            mock_find_row.assert_called_once_with(spreadsheet_id, sheet_name, student_id)
    
    def test_process_attendance_empty_student_id(self):
        """Test processing attendance with empty student ID."""
        spreadsheet_id = "1abc123def456"
        sheet_name = "CS101"
        column_name = "Week 1"
        student_id = ""
        
        with patch('backend.attendance_service.find_student_row') as mock_find_row, \
             patch('backend.attendance_service.mark_attendance') as mock_mark:
            # Empty ID should not be found
            mock_find_row.return_value = None
            
            from backend.attendance_service import process_attendance, AttendanceStatus
            result = process_attendance(spreadsheet_id, sheet_name, column_name, student_id)
            
            # Verify result
            assert result.status == AttendanceStatus.NOT_FOUND
            assert result.message == "Student Not Found"
            mock_mark.assert_not_called()
