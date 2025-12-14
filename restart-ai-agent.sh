#!/bin/bash
# Restart AI Agent Server Script

echo "🔄 Restarting AI Agent Server"
echo "=============================="
echo ""

# Find and kill existing AI agent processes
echo "1️⃣  Stopping existing AI agent processes..."
pkill -f "api_server.py" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null

# Wait for processes to stop
sleep 2

# Verify they're stopped
if pgrep -f "api_server.py" > /dev/null; then
    echo "⚠️  Force killing remaining processes..."
    pkill -9 -f "api_server.py"
fi

echo "✅ Stopped all existing processes"
echo ""

# Check if asyncpg is installed
echo "2️⃣  Verifying asyncpg installation..."
if python3 -c "import asyncpg" 2>/dev/null; then
    VERSION=$(python3 -c "import asyncpg; print(asyncpg.__version__)")
    echo "✅ asyncpg is installed (version: $VERSION)"
else
    echo "⚠️  asyncpg not found, installing..."
    pip3 install --user asyncpg
fi

echo ""
echo "3️⃣  Starting AI Agent Server..."
cd /Users/maxsolutions/Documents/GitHub/LoanAI/AI_agent

# Start the server in the background
nohup python3 api_server.py > ../logs/ai-agent.log 2>&1 &
AI_AGENT_PID=$!

echo "✅ AI Agent Server started (PID: $AI_AGENT_PID)"
echo ""

# Wait a moment and verify it started
sleep 3

if pgrep -f "api_server.py" > /dev/null; then
    echo "✅ AI Agent Server is running!"
    echo ""
    echo "📊 Server Status:"
    echo "   - Process ID: $AI_AGENT_PID"
    echo "   - Log file: logs/ai-agent.log"
    echo "   - URL: http://localhost:8000"
    echo ""
    echo "To test: curl http://localhost:8000/"
    echo "To stop: pkill -f api_server.py"
    echo ""
    
    # Test the endpoint
    sleep 2
    if curl -s http://localhost:8000/ > /dev/null; then
        echo "✅ Server is responding to requests!"
    else
        echo "⚠️  Server started but not responding yet (give it a few seconds)"
    fi
else
    echo "❌ Failed to start AI Agent Server"
    echo "Check logs/ai-agent.log for errors"
    exit 1
fi
