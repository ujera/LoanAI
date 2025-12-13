#!/bin/bash
# Verification script to test the fix

echo "🔍 Testing Application Status Update Fix"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo "1️⃣  Checking backend server..."
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend is NOT running!${NC}"
    echo "   Please start: npm run dev"
    exit 1
fi

# Check if AI agent is running
echo ""
echo "2️⃣  Checking AI agent server..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ AI Agent is running${NC}"
else
    echo -e "${RED}❌ AI Agent is NOT running!${NC}"
    echo "   Please start: cd AI_agent && python api_server.py"
    exit 1
fi

# Submit test application
echo ""
echo "3️⃣  Submitting test application..."
RESPONSE=$(curl -s -X POST http://localhost:3000/api/loan-application \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Test",
    "lastName": "User",
    "personalId": "12345678901",
    "gender": "male",
    "birthYear": "1995",
    "phone": "+995555000000",
    "address": "Tbilisi, Georgia",
    "educationLevel": "bachelor",
    "university": "Georgian Technical University",
    "employmentStatus": "employed",
    "companyName": "Test Company LLC",
    "monthlySalary": "2000",
    "experienceYears": "3",
    "loanPurpose": "business",
    "loanAmount": "10000",
    "loanDuration": "12",
    "additionalInfo": "Test application for verification"
  }')

# Extract customer ID
CUSTOMER_ID=$(echo $RESPONSE | grep -o '"customerId":"[^"]*"' | cut -d'"' -f4)

if [ -z "$CUSTOMER_ID" ]; then
    echo -e "${RED}❌ Failed to submit application${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ Application submitted${NC}"
echo "   Customer ID: $CUSTOMER_ID"

# Wait for AI processing
echo ""
echo "4️⃣  Waiting for AI processing..."
for i in {1..15}; do
    echo -n "."
    sleep 2
done
echo ""

# Check application status
echo ""
echo "5️⃣  Checking application status..."
STATUS_RESPONSE=$(curl -s "http://localhost:3000/api/loan-application?customerId=$CUSTOMER_ID")

# Parse the response
APP_STATUS=$(echo $STATUS_RESPONSE | grep -o '"application_status":"[^"]*"' | cut -d'"' -f4)
ELIGIBILITY_SCORE=$(echo $STATUS_RESPONSE | grep -o '"eligibility_score":[^,}]*' | cut -d':' -f2 | tr -d ' ')

echo ""
echo "📊 RESULTS:"
echo "=========="
echo "Customer ID: $CUSTOMER_ID"
echo "Application Status: $APP_STATUS"
echo "Eligibility Score: $ELIGIBILITY_SCORE"
echo ""

# Verify the fix
if [ "$APP_STATUS" = "pending" ]; then
    echo -e "${RED}❌ FIX FAILED: Status is still 'pending'${NC}"
    echo ""
    echo "The database was not updated by the AI agent."
    echo "Check AI agent logs for errors."
    exit 1
elif [ "$APP_STATUS" = "approved" ] || [ "$APP_STATUS" = "rejected" ] || [ "$APP_STATUS" = "manual_review" ]; then
    echo -e "${GREEN}✅ FIX SUCCESSFUL!${NC}"
    echo ""
    echo "The application status was properly updated to: $APP_STATUS"
    if [ ! -z "$ELIGIBILITY_SCORE" ] && [ "$ELIGIBILITY_SCORE" != "null" ]; then
        echo "Eligibility score was calculated: $ELIGIBILITY_SCORE"
    fi
    echo ""
    echo "Full response:"
    echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"
    exit 0
else
    echo -e "${YELLOW}⚠️  UNEXPECTED STATUS: $APP_STATUS${NC}"
    echo ""
    echo "Full response:"
    echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"
    exit 1
fi
