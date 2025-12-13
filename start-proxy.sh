#!/bin/bash

################################################################################
# Start Cloud SQL Proxy Manually
# This script helps you start the Cloud SQL Proxy with correct credentials
################################################################################

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${BLUE}🔌 Starting Cloud SQL Proxy...${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "config/cloud_sql_proxy" ]; then
    echo -e "${RED}Error: cloud_sql_proxy not found in config/ directory${NC}"
    echo -e "${YELLOW}Please run this from the LoanAI root directory${NC}"
    echo -e "${YELLOW}Or run: cd config && ./setup-proxy.sh${NC}"
    exit 1
fi

# Check if credentials exist
if [ ! -f "config/gcp-credentials.json" ]; then
    echo -e "${RED}Error: gcp-credentials.json not found in config/ directory${NC}"
    echo -e "${YELLOW}Please add your GCP service account credentials${NC}"
    exit 1
fi

# Check if port is already in use
if lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠  Port 5432 is already in use${NC}"
    echo -e "${YELLOW}Cloud SQL Proxy may already be running${NC}"
    echo ""
    echo "Processes on port 5432:"
    lsof -i :5432
    exit 0
fi

cd config

echo -e "${BLUE}Setting up credentials...${NC}"
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gcp-credentials.json"

echo -e "${BLUE}Starting proxy on port 5432...${NC}"
echo -e "${YELLOW}Instance: fourth-flag-481108-s5:us-central1:loanai-db-dev${NC}"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop the proxy${NC}"
echo ""

# Start the proxy
./cloud_sql_proxy --port 5432 fourth-flag-481108-s5:us-central1:loanai-db-dev
