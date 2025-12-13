#!/bin/bash

################################################################################
# LoanAI Stop All Services Script
# 
# This script stops all running LoanAI services
################################################################################

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PID_FILE=".loanai_pids"

echo ""
echo -e "${YELLOW}🛑 Stopping LoanAI Services...${NC}"
echo ""

# Stop processes from PID file
if [ -f "$PID_FILE" ]; then
    while IFS= read -r pid; do
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid" 2>/dev/null
            echo -e "${GREEN}✓ Stopped process $pid${NC}"
        else
            echo -e "${YELLOW}⚠ Process $pid not running${NC}"
        fi
    done < "$PID_FILE"
    rm -f "$PID_FILE"
    echo ""
    echo -e "${GREEN}✓ All tracked services stopped${NC}"
else
    echo -e "${YELLOW}⚠ No PID file found. Attempting to stop services by port...${NC}"
    echo ""
fi

# Stop by port as fallback
echo -e "${YELLOW}Checking for services on common ports...${NC}"

# Stop process on port 3000 (Next.js)
PORT_3000_PID=$(lsof -ti:3000)
if [ ! -z "$PORT_3000_PID" ]; then
    kill $PORT_3000_PID 2>/dev/null
    echo -e "${GREEN}✓ Stopped service on port 3000 (Next.js)${NC}"
fi

# Stop process on port 8000 (AI Agent)
PORT_8000_PID=$(lsof -ti:8000)
if [ ! -z "$PORT_8000_PID" ]; then
    kill $PORT_8000_PID 2>/dev/null
    echo -e "${GREEN}✓ Stopped service on port 8000 (AI Agent)${NC}"
fi

# Stop process on port 5432 (Cloud SQL Proxy)
PORT_5432_PID=$(lsof -ti:5432)
if [ ! -z "$PORT_5432_PID" ]; then
    kill $PORT_5432_PID 2>/dev/null
    echo -e "${GREEN}✓ Stopped service on port 5432 (Cloud SQL Proxy)${NC}"
fi

echo ""
echo -e "${GREEN}✅ All LoanAI services stopped${NC}"
echo ""
