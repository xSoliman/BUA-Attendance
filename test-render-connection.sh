#!/bin/bash

# Render Connection Test Script
# This script helps diagnose connection issues between frontend and backend

echo "🔍 Render Deployment Connection Test"
echo "====================================="
echo ""

# Get URLs from user
read -p "Enter your BACKEND URL (e.g., https://bua-attendance.onrender.com): " BACKEND_URL
read -p "Enter your FRONTEND URL (e.g., https://bua-attendance-frontend.onrender.com): " FRONTEND_URL

echo ""
echo "Testing with:"
echo "  Backend: $BACKEND_URL"
echo "  Frontend: $FRONTEND_URL"
echo ""

# Test 1: Backend Health
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1: Backend Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing: $BACKEND_URL/health"
echo ""
HEALTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BACKEND_URL/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$HEALTH_RESPONSE" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ PASS: Backend is healthy"
    echo "   Response: $BODY"
else
    echo "❌ FAIL: Backend health check failed (HTTP $HTTP_CODE)"
    echo "   Response: $BODY"
    echo "   → Check if backend is deployed and running"
fi
echo ""

# Test 2: Service Account Email
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 2: Service Account Email Endpoint"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing: $BACKEND_URL/api/service-account-email"
echo ""
EMAIL_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BACKEND_URL/api/service-account-email")
HTTP_CODE=$(echo "$EMAIL_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$EMAIL_RESPONSE" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ PASS: Service account endpoint works"
    echo "   Response: $BODY"
else
    echo "❌ FAIL: Service account endpoint failed (HTTP $HTTP_CODE)"
    echo "   Response: $BODY"
    echo "   → Check GOOGLE_SERVICE_ACCOUNT_JSON environment variable"
fi
echo ""

# Test 3: CORS
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 3: CORS Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing CORS from: $FRONTEND_URL"
echo ""
CORS_RESPONSE=$(curl -s -I -H "Origin: $FRONTEND_URL" \
                     -H "Access-Control-Request-Method: GET" \
                     -H "Access-Control-Request-Headers: Content-Type" \
                     "$BACKEND_URL/api/service-account-email")

if echo "$CORS_RESPONSE" | grep -q "access-control-allow-origin"; then
    ALLOWED_ORIGIN=$(echo "$CORS_RESPONSE" | grep -i "access-control-allow-origin" | cut -d: -f2- | tr -d '\r\n' | xargs)
    echo "✅ PASS: CORS is configured"
    echo "   Allowed Origin: $ALLOWED_ORIGIN"
else
    echo "❌ FAIL: CORS not configured"
    echo "   → Add FRONTEND_ORIGIN environment variable to backend"
    echo "   → Value should be: $FRONTEND_URL"
fi
echo ""

# Test 4: Frontend Accessibility
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 4: Frontend Accessibility"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing: $FRONTEND_URL"
echo ""
FRONTEND_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -I "$FRONTEND_URL")
HTTP_CODE=$(echo "$FRONTEND_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ PASS: Frontend is accessible"
else
    echo "❌ FAIL: Frontend not accessible (HTTP $HTTP_CODE)"
    echo "   → Check if frontend is deployed"
fi
echo ""

# Test 5: API URL Configuration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 5: Frontend API Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Checking frontend/app.js..."
echo ""
if [ -f "frontend/app.js" ]; then
    API_URL=$(grep "API_BASE_URL" frontend/app.js | head -1 | cut -d"'" -f2)
    echo "Current API_BASE_URL: $API_URL"
    
    if [ "$API_URL" = "$BACKEND_URL/api" ]; then
        echo "✅ PASS: API_BASE_URL is correct"
    else
        echo "❌ FAIL: API_BASE_URL mismatch"
        echo "   Expected: $BACKEND_URL/api"
        echo "   Found: $API_URL"
        echo "   → Update frontend/app.js line 4"
    fi
else
    echo "⚠️  WARNING: frontend/app.js not found in current directory"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Configuration:"
echo "  Backend URL: $BACKEND_URL"
echo "  Frontend URL: $FRONTEND_URL"
echo "  API Endpoint: $BACKEND_URL/api"
echo ""
echo "Required Environment Variables (Backend):"
echo "  GOOGLE_SERVICE_ACCOUNT_JSON: (check Render dashboard)"
echo "  FRONTEND_ORIGIN: $FRONTEND_URL"
echo ""
echo "Required Configuration (Frontend):"
echo "  API_BASE_URL: $BACKEND_URL/api"
echo ""
echo "Next Steps:"
echo "1. Fix any failed tests above"
echo "2. Commit and push changes: git add . && git commit -m 'Fix config' && git push"
echo "3. Wait for Render to redeploy (~2 minutes)"
echo "4. Test in browser: $FRONTEND_URL"
echo ""
echo "For detailed troubleshooting, see: RENDER_TROUBLESHOOTING.md"
