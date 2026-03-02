"""
Pytest configuration and shared fixtures for QR Attendance System tests.
"""

import pytest
import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


@pytest.fixture
def mock_spreadsheet_id():
    """Fixture providing a mock spreadsheet ID for testing."""
    return "1abc123def456ghi789jkl012mno345pqr678stu"


@pytest.fixture
def mock_student_ids():
    """Fixture providing a list of mock student IDs."""
    return ["20210001", "20210002", "20210003", "20210004", "20210005"]


@pytest.fixture
def mock_sheet_names():
    """Fixture providing mock course sheet names."""
    return ["CS101", "CS102", "MATH201"]


@pytest.fixture
def mock_column_names():
    """Fixture providing mock attendance column names."""
    return ["Week 1", "Week 2", "Week 3", "Week 4"]


@pytest.fixture
def mock_service_account_email():
    """Fixture providing a mock service account email."""
    return "attendance-system@test-project.iam.gserviceaccount.com"


@pytest.fixture
def sample_csv_data():
    """Fixture providing sample CSV data for QR code generation."""
    return [
        {"Student_ID": "20210001", "Name": "Ahmed Mohamed"},
        {"Student_ID": "20210002", "Name": "Sara Ali"},
        {"Student_ID": "20210003", "Name": "Mohamed Hassan"},
    ]


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "property_test: mark test as a property-based test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
