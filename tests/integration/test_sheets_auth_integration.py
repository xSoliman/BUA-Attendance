"""
Integration tests for Google Sheets Service Account authentication module.

These tests verify the authentication module works correctly with environment
variables and can be integrated into the FastAPI application.

Tests Requirements: 1.1, 2.5
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock

import sheets_auth


class TestAuthenticationIntegration:
    """Integration tests for authentication workflow."""
    
    def test_complete_authentication_flow_with_json(self, monkeypatch):
        """Test complete flow: load credentials -> get client -> get email."""
        mock_creds = {
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "key123",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
            "client_email": "attendance@test-project.iam.gserviceaccount.com",
            "client_id": "123456",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test"
        }
        
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_JSON', json.dumps(mock_creds))
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_FILE', raising=False)
        
        # Reset global client
        sheets_auth._client = None
        
        # Step 1: Get service account email
        email = sheets_auth.get_service_account_email()
        assert email == "attendance@test-project.iam.gserviceaccount.com"
        
        # Step 2: Initialize client with mocked credentials
        from google.oauth2.service_account import Credentials
        
        with patch.object(Credentials, 'from_service_account_info') as mock_creds_init:
            mock_credentials = MagicMock(spec=Credentials)
            mock_creds_init.return_value = mock_credentials
            
            with patch('gspread.authorize') as mock_authorize:
                mock_client = MagicMock()
                mock_authorize.return_value = mock_client
                
                client = sheets_auth.get_gspread_client()
                assert client is not None
                
                # Step 3: Verify singleton pattern - same client returned
                client2 = sheets_auth.get_gspread_client()
                assert client is client2
    
    def test_authentication_with_file_path(self, monkeypatch, tmp_path):
        """Test authentication flow using file path."""
        mock_creds = {
            "type": "service_account",
            "project_id": "test-project",
            "client_email": "file-based@test-project.iam.gserviceaccount.com",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n"
        }
        
        # Create temporary credentials file
        creds_file = tmp_path / "service-account.json"
        creds_file.write_text(json.dumps(mock_creds))
        
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_JSON', raising=False)
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_FILE', str(creds_file))
        
        # Reset global client
        sheets_auth._client = None
        
        # Get email
        email = sheets_auth.get_service_account_email()
        assert email == "file-based@test-project.iam.gserviceaccount.com"
        
        # Initialize client with mocked credentials
        from google.oauth2.service_account import Credentials
        
        with patch.object(Credentials, 'from_service_account_file') as mock_creds_init:
            mock_credentials = MagicMock(spec=Credentials)
            mock_creds_init.return_value = mock_credentials
            
            with patch('gspread.authorize') as mock_authorize:
                mock_client = MagicMock()
                mock_authorize.return_value = mock_client
                
                client = sheets_auth.get_gspread_client()
                assert client is not None
    
    def test_error_handling_in_application_context(self, monkeypatch):
        """Test that errors are properly raised for application error handling."""
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_JSON', raising=False)
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_FILE', raising=False)
        
        # Reset global client
        sheets_auth._client = None
        
        # Both functions should raise ValueError with helpful message
        with pytest.raises(ValueError) as exc_info:
            sheets_auth.get_service_account_email()
        assert "Service Account credentials not configured" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            sheets_auth.get_gspread_client()
        assert "Service Account credentials not configured" in str(exc_info.value)
    
    def test_json_priority_over_file(self, monkeypatch, tmp_path):
        """Test that JSON env var takes priority over file path."""
        json_creds = {
            "type": "service_account",
            "client_email": "json-priority@test-project.iam.gserviceaccount.com"
        }
        
        file_creds = {
            "type": "service_account",
            "client_email": "file-priority@test-project.iam.gserviceaccount.com"
        }
        
        # Create file
        creds_file = tmp_path / "service-account.json"
        creds_file.write_text(json.dumps(file_creds))
        
        # Set both environment variables
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_JSON', json.dumps(json_creds))
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_FILE', str(creds_file))
        
        # JSON should take priority
        email = sheets_auth.get_service_account_email()
        assert email == "json-priority@test-project.iam.gserviceaccount.com"


@pytest.mark.integration
class TestRealWorldScenarios:
    """Test scenarios that mimic real-world usage."""
    
    def test_fastapi_startup_scenario(self, monkeypatch):
        """Simulate FastAPI application startup with authentication."""
        mock_creds = {
            "type": "service_account",
            "project_id": "qr-attendance-prod",
            "client_email": "qr-attendance@qr-attendance-prod.iam.gserviceaccount.com",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n"
        }
        
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_JSON', json.dumps(mock_creds))
        
        # Reset global client
        sheets_auth._client = None
        
        # Simulate startup: get email for display to user
        service_email = sheets_auth.get_service_account_email()
        assert service_email == "qr-attendance@qr-attendance-prod.iam.gserviceaccount.com"
        
        # Simulate first API request: initialize client
        from google.oauth2.service_account import Credentials
        
        with patch.object(Credentials, 'from_service_account_info') as mock_creds_init:
            mock_credentials = MagicMock(spec=Credentials)
            mock_creds_init.return_value = mock_credentials
            
            with patch('gspread.authorize') as mock_authorize:
                mock_client = MagicMock()
                mock_authorize.return_value = mock_client
                
                client = sheets_auth.get_gspread_client()
                assert client is not None
                
                # Simulate subsequent API requests: reuse client
                for _ in range(5):
                    same_client = sheets_auth.get_gspread_client()
                    assert same_client is client
                
                # Verify authorize was only called once
                assert mock_authorize.call_count == 1
    
    def test_multiple_concurrent_requests(self, monkeypatch):
        """Test that concurrent requests share the same client instance."""
        mock_creds = {
            "type": "service_account",
            "client_email": "concurrent@test-project.iam.gserviceaccount.com",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n"
        }
        
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_JSON', json.dumps(mock_creds))
        
        # Reset global client
        sheets_auth._client = None
        
        from google.oauth2.service_account import Credentials
        
        with patch.object(Credentials, 'from_service_account_info') as mock_creds_init:
            mock_credentials = MagicMock(spec=Credentials)
            mock_creds_init.return_value = mock_credentials
            
            with patch('gspread.authorize') as mock_authorize:
                mock_client = MagicMock()
                mock_authorize.return_value = mock_client
                
                # Simulate multiple concurrent requests
                clients = [sheets_auth.get_gspread_client() for _ in range(10)]
                
                # All should be the same instance
                assert all(c is clients[0] for c in clients)
                
                # Authorize should only be called once
                assert mock_authorize.call_count == 1
