"""
Google Sheets Service Account Authentication Module

This module handles authentication with Google Sheets API using Service Account credentials.
It provides functions to initialize the gspread client and retrieve service account information.

Requirements: 1.1, 2.5
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Sheets API scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Global client instance
_client = None


def _load_credentials():
    """
    Load Service Account credentials from environment variables.
    
    Supports two methods:
    1. GOOGLE_SERVICE_ACCOUNT_JSON: Inline JSON string
    2. GOOGLE_SERVICE_ACCOUNT_FILE: Path to JSON key file
    
    Returns:
        Credentials: Google OAuth2 service account credentials
        
    Raises:
        ValueError: If credentials are not configured or invalid
    """
    # Try loading from inline JSON
    json_str = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    if json_str:
        try:
            credentials_dict = json.loads(json_str)
            return Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in GOOGLE_SERVICE_ACCOUNT_JSON: {e}")
    
    # Try loading from file path
    file_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    if file_path:
        if not os.path.exists(file_path):
            raise ValueError(f"Service account file not found: {file_path}")
        return Credentials.from_service_account_file(file_path, scopes=SCOPES)
    
    raise ValueError(
        "Service Account credentials not configured. "
        "Set either GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SERVICE_ACCOUNT_FILE environment variable."
    )


def get_gspread_client():
    """
    Initialize and return a gspread client with Service Account authentication.
    
    This function uses a singleton pattern to reuse the same client instance
    across multiple calls, avoiding unnecessary authentication overhead.
    
    Returns:
        gspread.Client: Authenticated gspread client
        
    Raises:
        ValueError: If credentials are not configured
        Exception: If authentication fails
    """
    global _client
    
    if _client is None:
        credentials = _load_credentials()
        _client = gspread.authorize(credentials)
    
    return _client


def get_service_account_email():
    """
    Retrieve the Service Account email address.
    
    This email must be added as an Editor to any Google Sheet
    that the system needs to access.
    
    Returns:
        str: Service Account email address
        
    Raises:
        ValueError: If credentials are not configured or invalid
    """
    # Try loading from inline JSON
    json_str = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    if json_str:
        try:
            credentials_dict = json.loads(json_str)
            return credentials_dict.get('client_email', '')
        except json.JSONDecodeError:
            pass
    
    # Try loading from file path
    file_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    if file_path:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                credentials_dict = json.load(f)
                return credentials_dict.get('client_email', '')
    
    raise ValueError(
        "Service Account credentials not configured. "
        "Set either GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SERVICE_ACCOUNT_FILE environment variable."
    )
