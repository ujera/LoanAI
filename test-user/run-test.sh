#!/bin/bash
# Quick test script to submit test user Luka Narsia

echo "🚀 Starting Test User Submission"
echo "================================"
echo ""
echo "Test User: Luka Narsia"
echo "Employer: GeoTech Solutions LLC"
echo "Position: Software Engineer"
echo ""
echo "Checking prerequisites..."
echo ""

# Check if backend is running
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not running!"
    echo "   Please run: npm run dev"
    exit 1
fi

# Check if Python is available
if command -v python3 &> /dev/null; then
    echo "✅ Python3 is available"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    echo "✅ Python is available"
    PYTHON_CMD="python"
else
    echo "❌ Python is not available!"
    echo "   Trying Node.js instead..."
    if command -v node &> /dev/null; then
        echo "✅ Node.js is available"
        node submit-test-user.js
        exit $?
    else
        echo "❌ Neither Python nor Node.js is available!"
        exit 1
    fi
fi

# Check if requests library is installed
if ! $PYTHON_CMD -c "import requests" 2>/dev/null; then
    echo "⚠️  requests library not found, installing..."
    pip3 install requests
fi

echo ""
echo "================================"
echo "Submitting test user..."
echo ""

# Run the Python script
$PYTHON_CMD submit-test-user.py
