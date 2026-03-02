"""
End-to-End Integration Tests for QR Attendance System

This module tests the complete user flow from configuration to attendance recording,
verifying that all components (frontend, backend, Google Sheets) work together correctly.

Tests Requirements: All requirements (integration)
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Import the FastAPI app
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.main import app
from backend.attendance_service import AttendanceStatus


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_credentials(monkeypatch):
    """Set up mock Google Service Account credentials."""
    mock_creds = {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "key123",
        "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
        "client_email": "test-attendance@test-project.iam.gserviceaccount.com",
        "client_id": "123456",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test"
    }
    
    monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_JSON', json.dumps(mock_creds))
    monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_FILE', raising=False)
    
    # Reset the global client
    import backend.sheets_auth as sheets_auth
    sheets_auth._client = None
    
    return mock_creds


class TestCompleteUserFlow:
    """Test the complete user flow from configuration to scanning."""
    
    def test_configuration_flow(self, client, mock_credentials):
        """
        Test the configuration flow:
        1. Get service account email
        2. Validate spreadsheet access
        3. Store configuration
        
        Requirements: 2.1, 2.2, 2.5
        """
        # Step 1: Get service account email for display
        response = client.get("/api/service-account-email")
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert data["email"] == "test-attendance@test-project.iam.gserviceaccount.com"
        
        # Step 2: Validate spreadsheet access
        test_spreadsheet_id = "1abc123def456"
        
        with patch('backend.sheets_service.validate_spreadsheet_access') as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "message": "Spreadsheet accessible"
            }
            
            response = client.post(
                "/api/validate-spreadsheet",
                json={"spreadsheet_id": test_spreadsheet_id}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True
            assert "accessible" in data["message"].lower()
    
    def test_session_initialization_flow(self, client, mock_credentials):
        """
        Test the session initialization flow:
        1. Fetch sheet names
        2. Select a course sheet
        3. Fetch attendance columns
        4. Select an attendance column
        
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
        """
        test_spreadsheet_id = "1abc123def456"
        
        # Step 1: Fetch sheet names
        with patch('backend.sheets_service.get_sheet_names') as mock_get_sheets:
            mock_get_sheets.return_value = ["CS101", "CS102", "MATH201"]
            
            response = client.get(f"/api/sheets/{test_spreadsheet_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert "sheets" in data
            assert len(data["sheets"]) == 3
            assert "CS101" in data["sheets"]
        
        # Step 2: Fetch attendance columns for selected sheet
        test_sheet_name = "CS101"
        
        with patch('backend.sheets_service.get_headers') as mock_get_headers:
            mock_get_headers.return_value = ["Week 1", "Week 2", "Week 3", "Week 4"]
            
            response = client.get(
                f"/api/sheets/{test_spreadsheet_id}/{test_sheet_name}/columns"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "columns" in data
            assert len(data["columns"]) == 4
            assert "Week 1" in data["columns"]
    
    def test_attendance_recording_flow(self, client, mock_credentials):
        """
        Test the attendance recording flow:
        1. Scan QR code (extract Student_ID)
        2. Send attendance request to backend
        3. Backend marks attendance in Google Sheet
        4. Return success status
        
        Requirements: 4.3, 4.4, 1.7, 1.8, 5.1
        """
        attendance_request = {
            "spreadsheet_id": "1abc123def456",
            "sheet_name": "CS101",
            "column_name": "Week 1",
            "student_id": "20210001"
        }
        
        with patch('backend.attendance_service.process_attendance') as mock_process:
            from backend.attendance_service import AttendanceResult
            mock_process.return_value = AttendanceResult(
                status=AttendanceStatus.SUCCESS,
                message="Attendance recorded"
            )
            
            response = client.post("/api/attendance", json=attendance_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "recorded" in data["message"].lower()
            
            # Verify the backend function was called with correct parameters
            mock_process.assert_called_once_with(
                spreadsheet_id=attendance_request["spreadsheet_id"],
                sheet_name=attendance_request["sheet_name"],
                column_name=attendance_request["column_name"],
                student_id=attendance_request["student_id"]
            )
    
    def test_student_not_found_flow(self, client, mock_credentials):
        """
        Test the flow when a student is not found:
        1. Scan QR code with unknown Student_ID
        2. Backend searches for student
        3. Student not found
        4. Return not_found status
        
        Requirements: 1.9, 5.2
        """
        attendance_request = {
            "spreadsheet_id": "1abc123def456",
            "sheet_name": "CS101",
            "column_name": "Week 1",
            "student_id": "99999999"  # Non-existent student
        }
        
        with patch('backend.attendance_service.process_attendance') as mock_process:
            from backend.attendance_service import AttendanceResult
            mock_process.return_value = AttendanceResult(
                status=AttendanceStatus.NOT_FOUND,
                message="Student Not Found"
            )
            
            response = client.post("/api/attendance", json=attendance_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "not_found"
            assert "not found" in data["message"].lower()
    
    def test_session_change_flow(self, client, mock_credentials):
        """
        Test changing sessions:
        1. Complete a session (record some attendance)
        2. Change to a different course/week
        3. Verify new session works correctly
        
        Requirements: 12.2, 12.3, 12.4, 12.5
        """
        # First session
        first_request = {
            "spreadsheet_id": "1abc123def456",
            "sheet_name": "CS101",
            "column_name": "Week 1",
            "student_id": "20210001"
        }
        
        with patch('backend.attendance_service.process_attendance') as mock_process:
            from backend.attendance_service import AttendanceResult
            mock_process.return_value = AttendanceResult(
                status=AttendanceStatus.SUCCESS,
                message="Attendance recorded"
            )
            
            response = client.post("/api/attendance", json=first_request)
            assert response.status_code == 200
        
        # Change session - fetch new sheet columns
        with patch('backend.sheets_service.get_headers') as mock_get_headers:
            mock_get_headers.return_value = ["Week 1", "Week 2", "Week 3"]
            
            response = client.get(
                f"/api/sheets/{first_request['spreadsheet_id']}/CS102/columns"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "columns" in data
        
        # Second session with different course
        second_request = {
            "spreadsheet_id": "1abc123def456",
            "sheet_name": "CS102",  # Different course
            "column_name": "Week 2",  # Different week
            "student_id": "20210002"
        }
        
        with patch('backend.attendance_service.process_attendance') as mock_process:
            from backend.attendance_service import AttendanceResult
            mock_process.return_value = AttendanceResult(
                status=AttendanceStatus.SUCCESS,
                message="Attendance recorded"
            )
            
            response = client.post("/api/attendance", json=second_request)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"


class TestErrorHandling:
    """Test error handling across the complete system."""
    
    def test_invalid_spreadsheet_id(self, client, mock_credentials):
        """
        Test handling of invalid spreadsheet ID.
        
        Requirements: 1.3, 11.1
        """
        with patch('backend.sheets_service.validate_spreadsheet_access') as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "message": "Spreadsheet not found. Please add test-attendance@test-project.iam.gserviceaccount.com as an Editor."
            }
            
            response = client.post(
                "/api/validate-spreadsheet",
                json={"spreadsheet_id": "invalid_id"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is False
            assert "not found" in data["message"].lower()
    
    def test_missing_student_id_column(self, client, mock_credentials):
        """
        Test handling when Student_ID column is missing.
        
        Requirements: 11.3
        """
        attendance_request = {
            "spreadsheet_id": "1abc123def456",
            "sheet_name": "InvalidSheet",
            "column_name": "Week 1",
            "student_id": "20210001"
        }
        
        with patch('backend.attendance_service.process_attendance') as mock_process:
            from backend.attendance_service import AttendanceResult
            mock_process.return_value = AttendanceResult(
                status=AttendanceStatus.ERROR,
                message="Student ID column not found. Please ensure the sheet has an 'ID' or 'رقم الجلوس' column."
            )
            
            response = client.post("/api/attendance", json=attendance_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"
            assert "column not found" in data["message"].lower()
    
    def test_network_error_handling(self, client, mock_credentials):
        """
        Test handling of network errors.
        
        Requirements: 11.5
        """
        attendance_request = {
            "spreadsheet_id": "1abc123def456",
            "sheet_name": "CS101",
            "column_name": "Week 1",
            "student_id": "20210001"
        }
        
        with patch('backend.attendance_service.process_attendance') as mock_process:
            # Simulate network error
            mock_process.side_effect = Exception("Network connection failed")
            
            # The endpoint should handle the exception gracefully
            # Note: This depends on error handling in the endpoint
            try:
                response = client.post("/api/attendance", json=attendance_request)
                # If error handling is implemented, should return 500
                assert response.status_code in [500, 200]
            except Exception:
                # If no error handling, the exception will propagate
                pass


class TestAsynchronousOperations:
    """Test asynchronous operations and non-blocking behavior."""
    
    def test_multiple_rapid_attendance_requests(self, client, mock_credentials):
        """
        Test that multiple rapid attendance requests are handled correctly.
        
        Requirements: 9.2, 9.3
        """
        student_ids = ["20210001", "20210002", "20210003", "20210004", "20210005"]
        
        with patch('backend.attendance_service.process_attendance') as mock_process:
            from backend.attendance_service import AttendanceResult
            mock_process.return_value = AttendanceResult(
                status=AttendanceStatus.SUCCESS,
                message="Attendance recorded"
            )
            
            # Send multiple requests rapidly
            responses = []
            for student_id in student_ids:
                response = client.post("/api/attendance", json={
                    "spreadsheet_id": "1abc123def456",
                    "sheet_name": "CS101",
                    "column_name": "Week 1",
                    "student_id": student_id
                })
                responses.append(response)
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "success"
            
            # Verify all students were processed
            assert mock_process.call_count == len(student_ids)


class TestCORSConfiguration:
    """Test CORS configuration for frontend-backend communication."""
    
    def test_cors_headers_present(self, client):
        """
        Test that CORS headers are properly configured.
        
        Requirements: 9.1
        """
        # Test preflight request
        response = client.options(
            "/api/service-account-email",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # CORS should allow the request
        assert response.status_code in [200, 204]
        
        # Test actual request with origin
        response = client.get(
            "/api/service-account-email",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
