#!/bin/bash

# QR Attendance System - Integration Test Runner
# This script sets up a test environment and runs integration tests

set -e

echo "=========================================="
echo "QR Attendance System - Integration Tests"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo "Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${YELLOW}⚠ Backend is not running${NC}"
    echo ""
    echo "Starting backend server..."
    echo "Please ensure you have configured backend/.env with your Service Account credentials"
    echo ""
    
    # Check if .env exists
    if [ ! -f "backend/.env" ]; then
        echo -e "${RED}✗ backend/.env not found${NC}"
        echo ""
        echo "Please create backend/.env from backend/.env.example and add your credentials"
        echo "Then run this script again"
        exit 1
    fi
    
    # Start backend in background
    cd backend
    uvicorn main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    echo "Waiting for backend to start..."
    sleep 3
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend started successfully (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${RED}✗ Failed to start backend${NC}"
        exit 1
    fi
fi

echo ""
echo "Running integration tests..."
echo ""

# Run the Python integration test script
python tests/manual_integration_test.py

TEST_RESULT=$?

echo ""
echo "=========================================="
echo "Integration Test Complete"
echo "=========================================="

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "You can now test the complete system:"
    echo "1. Keep the backend running"
    echo "2. In a new terminal, run: cd frontend && python -m http.server 3000"
    echo "3. Open http://localhost:3000 in your browser"
    echo "4. Test the complete user flow"
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo "Please review the output above and fix any issues"
fi

exit $TEST_RESULT
