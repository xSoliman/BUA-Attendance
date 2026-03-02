"""
Unit tests for Google Sheets Service Account authentication module.

Tests Requirements: 1.1, 2.5
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock
import gspread
from google.oauth2.service_account import Credentials

# Import the module to test
import sheets_auth


class TestLoadCredentials:
    """Test credential loading from environment variables."""
    
    def test_load_from_json_string(self, monkeypatch):
        """Test loading credentials from GOOGLE_SERVICE_ACCOUNT_JSON."""
        mock_creds = {
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "key123",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
            "client_id": "123456",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test"
        }
        
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_JSON', json.dumps(mock_creds))
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_FILE', raising=False)
        
        with patch.object(Credentials, 'from_service_account_info') as mock_from_info:
            mock_from_info.return_value = MagicMock(spec=Credentials)
            credentials = sheets_auth._load_credentials()
            
            mock_from_info.assert_called_once()
            assert credentials is not None
    
    def test_load_from_file_path(self, monkeypatch, tmp_path):
        """Test loading credentials from GOOGLE_SERVICE_ACCOUNT_FILE."""
        mock_creds = {
            "type": "service_account",
            "project_id": "test-project",
            "client_email": "test@test-project.iam.gserviceaccount.com"
        }
        
        # Create temporary credentials file
        creds_file = tmp_path / "service-account.json"
        creds_file.write_text(json.dumps(mock_creds))
        
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_JSON', raising=False)
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_FILE', str(creds_file))
        
        with patch.object(Credentials, 'from_service_account_file') as mock_from_file:
            mock_from_file.return_value = MagicMock(spec=Credentials)
            credentials = sheets_auth._load_credentials()
            
            mock_from_file.assert_called_once()
            assert credentials is not None
    
    def test_invalid_json_raises_error(self, monkeypatch):
        """Test that invalid JSON raises ValueError."""
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_JSON', 'invalid json {')
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_FILE', raising=False)
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            sheets_auth._load_credentials()
    
    def test_missing_file_raises_error(self, monkeypatch):
        """Test that missing file path raises ValueError."""
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_JSON', raising=False)
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_FILE', '/nonexistent/path.json')
        
        with pytest.raises(ValueError, match="Service account file not found"):
            sheets_auth._load_credentials()
    
    def test_no_credentials_raises_error(self, monkeypatch):
        """Test that missing credentials raises ValueError."""
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_JSON', raising=False)
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_FILE', raising=False)
        
        with pytest.raises(ValueError, match="Service Account credentials not configured"):
            sheets_auth._load_credentials()


class TestGetGspreadClient:
    """Test gspread client initialization."""
    
    def test_client_initialization(self, monkeypatch):
        """Test that client is initialized correctly."""
        mock_creds = {
            "type": "service_account",
            "project_id": "test-project",
            "client_email": "test@test-project.iam.gserviceaccount.com"
        }
        
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_JSON', json.dumps(mock_creds))
        
        # Reset the global client
        sheets_auth._client = None
        
        with patch.object(Credentials, 'from_service_account_info') as mock_creds_init:
            mock_creds_init.return_value = MagicMock(spec=Credentials)
            
            with patch('gspread.authorize') as mock_authorize:
                mock_client = MagicMock(spec=gspread.Client)
                mock_authorize.return_value = mock_client
                
                client = sheets_auth.get_gspread_client()
                
                assert client is mock_client
                mock_authorize.assert_called_once()
    
    def test_client_singleton_pattern(self, monkeypatch):
        """Test that the same client instance is reused."""
        mock_creds = {
            "type": "service_account",
            "project_id": "test-project",
            "client_email": "test@test-project.iam.gserviceaccount.com"
        }
        
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_JSON', json.dumps(mock_creds))
        
        # Reset the global client
        sheets_auth._client = None
        
        with patch.object(Credentials, 'from_service_account_info'):
            with patch('gspread.authorize') as mock_authorize:
                mock_client = MagicMock(spec=gspread.Client)
                mock_authorize.return_value = mock_client
                
                client1 = sheets_auth.get_gspread_client()
                client2 = sheets_auth.get_gspread_client()
                
                # Should only authorize once
                assert mock_authorize.call_count == 1
                assert client1 is client2


class TestGetServiceAccountEmail:
    """Test service account email retrieval."""
    
    def test_get_email_from_json(self, monkeypatch):
        """Test retrieving email from GOOGLE_SERVICE_ACCOUNT_JSON."""
        expected_email = "test@test-project.iam.gserviceaccount.com"
        mock_creds = {
            "type": "service_account",
            "client_email": expected_email
        }
        
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_JSON', json.dumps(mock_creds))
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_FILE', raising=False)
        
        email = sheets_auth.get_service_account_email()
        assert email == expected_email
    
    def test_get_email_from_file(self, monkeypatch, tmp_path):
        """Test retrieving email from GOOGLE_SERVICE_ACCOUNT_FILE."""
        expected_email = "test@test-project.iam.gserviceaccount.com"
        mock_creds = {
            "type": "service_account",
            "client_email": expected_email
        }
        
        # Create temporary credentials file
        creds_file = tmp_path / "service-account.json"
        creds_file.write_text(json.dumps(mock_creds))
        
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_JSON', raising=False)
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_FILE', str(creds_file))
        
        email = sheets_auth.get_service_account_email()
        assert email == expected_email
    
    def test_get_email_no_credentials_raises_error(self, monkeypatch):
        """Test that missing credentials raises ValueError."""
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_JSON', raising=False)
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_FILE', raising=False)
        
        with pytest.raises(ValueError, match="Service Account credentials not configured"):
            sheets_auth.get_service_account_email()
    
    def test_get_email_invalid_json(self, monkeypatch):
        """Test that invalid JSON falls back to file path or raises error."""
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_JSON', 'invalid json')
        monkeypatch.delenv('GOOGLE_SERVICE_ACCOUNT_FILE', raising=False)
        
        with pytest.raises(ValueError, match="Service Account credentials not configured"):
            sheets_auth.get_service_account_email()
    
    def test_get_email_missing_client_email_field(self, monkeypatch):
        """Test handling of credentials without client_email field."""
        mock_creds = {
            "type": "service_account",
            "project_id": "test-project"
            # Missing client_email
        }
        
        monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_JSON', json.dumps(mock_creds))
        
        email = sheets_auth.get_service_account_email()
        assert email == ''  # Should return empty string if field is missing
