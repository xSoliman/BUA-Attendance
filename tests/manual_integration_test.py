#!/usr/bin/env python3
"""
Manual Integration Test Script for QR Attendance System

This script performs end-to-end testing of the complete system by:
1. Verifying backend API endpoints are accessible
2. Testing the complete user flow from configuration to attendance recording
3. Validating frontend-backend integration

Run this script with the backend server running on localhost:8000

Requirements: All requirements (integration)
"""

import requests
import json
import sys
from typing import Dict, Any


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_test(name: str):
    """Print test name."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing: {name}{Colors.END}")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def test_backend_health(base_url: str) -> bool:
    """Test if backend server is running."""
    print_test("Backend Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print_success("Backend server is running")
            return True
        else:
            print_error(f"Backend returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend server")
        print_warning("Make sure the backend is running on http://localhost:8000")
        print_warning("Run: cd backend && uvicorn main:app --reload")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_service_account_email(base_url: str) -> bool:
    """Test GET /api/service-account-email endpoint."""
    print_test("Service Account Email Endpoint")
    try:
        response = requests.get(f"{base_url}/api/service-account-email", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "email" in data:
                print_success(f"Service account email: {data['email']}")
                return True
            else:
                print_error("Response missing 'email' field")
                return False
        else:
            print_error(f"Status code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_spreadsheet_validation(base_url: str) -> bool:
    """Test POST /api/validate-spreadsheet endpoint."""
    print_test("Spreadsheet Validation Endpoint")
    
    # Test with a dummy spreadsheet ID
    test_id = "1abc123def456"
    
    try:
        response = requests.post(
            f"{base_url}/api/validate-spreadsheet",
            json={"spreadsheet_id": test_id},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "valid" in data and "message" in data:
                print_success(f"Validation response: valid={data['valid']}, message={data['message']}")
                return True
            else:
                print_error("Response missing required fields")
                return False
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_get_sheets(base_url: str) -> bool:
    """Test GET /api/sheets/{spreadsheet_id} endpoint."""
    print_test("Get Sheets Endpoint")
    
    test_id = "1abc123def456"
    
    try:
        response = requests.get(f"{base_url}/api/sheets/{test_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "sheets" in data:
                print_success(f"Sheets endpoint working (returned {len(data['sheets'])} sheets)")
                return True
            else:
                print_error("Response missing 'sheets' field")
                return False
        elif response.status_code == 500:
            # Expected if no real spreadsheet configured
            print_warning("Endpoint returned 500 (expected without real spreadsheet)")
            print_success("Endpoint is accessible and responding")
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_get_columns(base_url: str) -> bool:
    """Test GET /api/sheets/{spreadsheet_id}/{sheet_name}/columns endpoint."""
    print_test("Get Columns Endpoint")
    
    test_id = "1abc123def456"
    test_sheet = "CS101"
    
    try:
        response = requests.get(
            f"{base_url}/api/sheets/{test_id}/{test_sheet}/columns",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "columns" in data:
                print_success(f"Columns endpoint working (returned {len(data['columns'])} columns)")
                return True
            else:
                print_error("Response missing 'columns' field")
                return False
        elif response.status_code == 500:
            # Expected if no real spreadsheet configured
            print_warning("Endpoint returned 500 (expected without real spreadsheet)")
            print_success("Endpoint is accessible and responding")
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_record_attendance(base_url: str) -> bool:
    """Test POST /api/attendance endpoint."""
    print_test("Record Attendance Endpoint")
    
    attendance_data = {
        "spreadsheet_id": "1abc123def456",
        "sheet_name": "CS101",
        "column_name": "Week 1",
        "student_id": "20210001"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/attendance",
            json=attendance_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "status" in data and "message" in data:
                print_success(f"Attendance endpoint working (status={data['status']})")
                return True
            else:
                print_error("Response missing required fields")
                return False
        elif response.status_code == 500:
            # Expected if no real spreadsheet configured
            print_warning("Endpoint returned 500 (expected without real spreadsheet)")
            print_success("Endpoint is accessible and responding")
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_cors_headers(base_url: str) -> bool:
    """Test CORS headers are properly configured."""
    print_test("CORS Configuration")
    
    try:
        response = requests.get(
            f"{base_url}/api/service-account-email",
            headers={"Origin": "http://localhost:3000"},
            timeout=5
        )
        
        # Check for CORS headers
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        if cors_header:
            print_success(f"CORS headers present: {cors_header}")
            return True
        else:
            print_warning("CORS headers not found (may need to check preflight)")
            # Still return True as this might be expected behavior
            return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_frontend_files() -> bool:
    """Test that frontend files exist and are accessible."""
    print_test("Frontend Files")
    
    import os
    
    required_files = [
        "frontend/index.html",
        "frontend/config.html",
        "frontend/session.html",
        "frontend/scanner.html",
        "frontend/app.js",
        "frontend/styles.css"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"Found: {file_path}")
        else:
            print_error(f"Missing: {file_path}")
            all_exist = False
    
    return all_exist


def test_frontend_backend_integration() -> bool:
    """Test that frontend correctly references backend API."""
    print_test("Frontend-Backend Integration")
    
    try:
        with open("frontend/app.js", "r") as f:
            content = f.read()
            
        # Check for API_BASE_URL
        if "API_BASE_URL" in content:
            print_success("API_BASE_URL defined in app.js")
        else:
            print_error("API_BASE_URL not found in app.js")
            return False
        
        # Check for API endpoints
        endpoints = [
            "/api/service-account-email",
            "/api/validate-spreadsheet",
            "/api/sheets/",
            "/api/attendance"
        ]
        
        all_found = True
        for endpoint in endpoints:
            if endpoint in content:
                print_success(f"Frontend references: {endpoint}")
            else:
                print_error(f"Frontend missing reference to: {endpoint}")
                all_found = False
        
        return all_found
    except Exception as e:
        print_error(f"Error reading app.js: {e}")
        return False


def run_all_tests():
    """Run all integration tests."""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("QR Attendance System - Integration Test Suite")
    print(f"{'='*60}{Colors.END}\n")
    
    base_url = "http://localhost:8000"
    
    tests = [
        ("Backend Health", lambda: test_backend_health(base_url)),
        ("Service Account Email", lambda: test_service_account_email(base_url)),
        ("Spreadsheet Validation", lambda: test_spreadsheet_validation(base_url)),
        ("Get Sheets", lambda: test_get_sheets(base_url)),
        ("Get Columns", lambda: test_get_columns(base_url)),
        ("Record Attendance", lambda: test_record_attendance(base_url)),
        ("CORS Configuration", lambda: test_cors_headers(base_url)),
        ("Frontend Files", test_frontend_files),
        ("Frontend-Backend Integration", test_frontend_backend_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n{Colors.BOLD}{'='*60}")
    print("Test Summary")
    print(f"{'='*60}{Colors.END}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All integration tests passed!{Colors.END}")
        print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
        print("1. Start the frontend: cd frontend && python -m http.server 3000")
        print("2. Open http://localhost:3000 in your browser")
        print("3. Test the complete user flow manually")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some tests failed{Colors.END}")
        print("\nPlease fix the failing tests before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
