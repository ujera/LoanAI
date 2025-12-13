#!/bin/bash

################################################################################
# LoanAI Master Startup Script
# 
# This script starts all necessary services for the LoanAI application:
# 1. Cloud SQL Proxy (for database connection)
# 2. AI Agent API Server (FastAPI backend for loan processing)
# 3. Next.js Application (Frontend + Backend API)
#
# Usage: ./start-all.sh
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# PID file to track background processes
PID_FILE=".loanai_pids"

# Trap to cleanup on exit
trap cleanup EXIT INT TERM

cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down all services...${NC}"
    
    if [ -f "$PID_FILE" ]; then
        while IFS= read -r pid; do
            if ps -p "$pid" > /dev/null 2>&1; then
                kill "$pid" 2>/dev/null || true
                echo -e "${GREEN}✓ Stopped process $pid${NC}"
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
    
    echo -e "${GREEN}✓ All services stopped${NC}"
    exit 0
}

print_header() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${PURPLE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Clear old PID file
rm -f "$PID_FILE"

print_header "🚀 LoanAI Application Startup"
echo -e "${CYAN}Starting all services for the LoanAI Loan Processing System${NC}"
echo ""

################################################################################
# 1. PRE-FLIGHT CHECKS
################################################################################

print_section "Running Pre-flight Checks..."

# Check if .env exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_info "Please create .env file with required credentials"
    exit 1
fi
print_success ".env file found"

# Check if GCP credentials exist
if [ ! -f "config/gcp-credentials.json" ]; then
    print_warning "GCP credentials not found at config/gcp-credentials.json"
    print_info "Database and storage features may not work"
else
    print_success "GCP credentials found"
fi

# Check if Cloud SQL Proxy exists
if [ ! -f "config/cloud_sql_proxy" ]; then
    print_warning "Cloud SQL Proxy not found"
    print_info "Run: cd config && ./setup-proxy.sh"
    print_info "Skipping database proxy startup..."
    START_PROXY=false
else
    print_success "Cloud SQL Proxy found"
    START_PROXY=true
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
fi
print_success "Node.js found: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
fi
print_success "npm found: $(npm --version)"

# Check Python3
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed"
    exit 1
fi
print_success "Python3 found: $(python3 --version)"

################################################################################
# 2. INSTALL DEPENDENCIES
################################################################################

print_section "Installing Dependencies..."

# Install Node.js dependencies
if [ ! -d "node_modules" ]; then
    print_info "Installing Node.js dependencies..."
    npm install
    print_success "Node.js dependencies installed"
else
    print_success "Node.js dependencies already installed"
fi

# Install Python dependencies for AI Agent
if [ ! -d "AI_agent/venv" ]; then
    print_info "Creating Python virtual environment..."
    cd AI_agent
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    deactivate
    cd ..
    print_success "Python environment created and dependencies installed"
else
    print_success "Python virtual environment already exists"
fi

################################################################################
# 3. START CLOUD SQL PROXY
################################################################################

if [ "$START_PROXY" = true ]; then
    print_section "Starting Cloud SQL Proxy..."
    
    cd config
    
    # Check if proxy is already running
    if lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port 5432 is already in use"
        print_info "Cloud SQL Proxy may already be running"
    else
        print_info "Starting proxy on port 5432..."
        
        # Set Google credentials environment variable
        export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gcp-credentials.json"
        
        # Start Cloud SQL Proxy in background
        nohup ./cloud_sql_proxy --port 5432 fourth-flag-481108-s5:us-central1:loanai-db-dev > ../logs/proxy.log 2>&1 &
        PROXY_PID=$!
        echo "$PROXY_PID" >> "../$PID_FILE"
        
        # Wait for proxy to be ready
        sleep 3
        
        if ps -p $PROXY_PID > /dev/null; then
            print_success "Cloud SQL Proxy started (PID: $PROXY_PID)"
            print_info "Logs: logs/proxy.log"
        else
            print_error "Failed to start Cloud SQL Proxy"
            print_info "Check logs/proxy.log for details"
            print_warning "You can start it manually: cd config && GOOGLE_APPLICATION_CREDENTIALS=\$(pwd)/gcp-credentials.json ./cloud_sql_proxy --port 5432 fourth-flag-481108-s5:us-central1:loanai-db-dev"
        fi
    fi
    
    cd ..
else
    print_warning "Skipping Cloud SQL Proxy (not found)"
fi

################################################################################
# 4. START AI AGENT API SERVER
################################################################################

print_section "Starting AI Agent API Server..."

# Create logs directory if it doesn't exist
mkdir -p logs

cd AI_agent

# Check if port 8000 is available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port 8000 is already in use"
    print_info "AI Agent API may already be running"
else
    print_info "Starting AI Agent API on port 8000..."
    
    # Activate virtual environment and start server
    source venv/bin/activate
    nohup python api_server.py > ../logs/ai-agent.log 2>&1 &
    AI_AGENT_PID=$!
    echo "$AI_AGENT_PID" >> "../$PID_FILE"
    deactivate
    
    # Wait for server to be ready
    sleep 4
    
    if ps -p $AI_AGENT_PID > /dev/null; then
        print_success "AI Agent API started (PID: $AI_AGENT_PID)"
        print_info "API: http://localhost:8000"
        print_info "Docs: http://localhost:8000/docs"
        print_info "Logs: logs/ai-agent.log"
    else
        print_error "Failed to start AI Agent API"
        print_info "Check logs/ai-agent.log for details"
    fi
fi

cd ..

################################################################################
# 5. START NEXT.JS APPLICATION
################################################################################

print_section "Starting Next.js Application..."

# Check if port 3000 is available
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port 3000 is already in use"
    print_info "Next.js may already be running"
else
    print_info "Starting Next.js development server on port 3000..."
    
    # Check if Cloud SQL Proxy is running
    if ! lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Cloud SQL Proxy is not running"
        print_info "Database operations will fail, but frontend will still work"
        print_info "You can start the proxy separately with: ./start-proxy.sh"
    fi
    
    # Start Next.js in background (use dev:force to skip predev check)
    nohup npm run dev:force > logs/nextjs.log 2>&1 &
    NEXTJS_PID=$!
    echo "$NEXTJS_PID" >> "$PID_FILE"
    
    # Wait for Next.js to be ready
    print_info "Waiting for Next.js to compile..."
    sleep 8
    
    if ps -p $NEXTJS_PID > /dev/null; then
        print_success "Next.js started (PID: $NEXTJS_PID)"
        print_info "Application: http://localhost:3000"
        print_info "Logs: logs/nextjs.log"
    else
        print_error "Failed to start Next.js"
        print_info "Check logs/nextjs.log for details"
        print_info "Try running manually: npm run dev"
    fi
fi

################################################################################
# 6. SUMMARY
################################################################################

sleep 2

print_header "✅ LoanAI Application Started Successfully!"

echo -e "${GREEN}All services are now running:${NC}"
echo ""
echo -e "${CYAN}┌─────────────────────────────────────────────────────────────┐${NC}"
echo -e "${CYAN}│  SERVICE              │  STATUS  │  URL/PORT              │${NC}"
echo -e "${CYAN}├─────────────────────────────────────────────────────────────┤${NC}"

if [ "$START_PROXY" = true ] && lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${CYAN}│  Cloud SQL Proxy      │${GREEN}  ✓ UP    ${CYAN}│  localhost:5432        │${NC}"
else
    echo -e "${CYAN}│  Cloud SQL Proxy      │${YELLOW}  ⚠ DOWN  ${CYAN}│  localhost:5432        │${NC}"
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${CYAN}│  AI Agent API         │${GREEN}  ✓ UP    ${CYAN}│  http://localhost:8000 │${NC}"
else
    echo -e "${CYAN}│  AI Agent API         │${YELLOW}  ⚠ DOWN  ${CYAN}│  http://localhost:8000 │${NC}"
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${CYAN}│  Next.js App          │${GREEN}  ✓ UP    ${CYAN}│  http://localhost:3000 │${NC}"
else
    echo -e "${CYAN}│  Next.js App          │${YELLOW}  ⚠ DOWN  ${CYAN}│  http://localhost:3000 │${NC}"
fi

echo -e "${CYAN}└─────────────────────────────────────────────────────────────┘${NC}"
echo ""

echo -e "${BLUE}📖 Important URLs:${NC}"
echo -e "   • Application:        ${GREEN}http://localhost:3000${NC}"
echo -e "   • AI Agent API:       ${GREEN}http://localhost:8000${NC}"
echo -e "   • AI Agent Docs:      ${GREEN}http://localhost:8000/docs${NC}"
echo -e "   • Health Check:       ${GREEN}http://localhost:8000/health${NC}"
echo ""

echo -e "${BLUE}📝 Log Files:${NC}"
echo -e "   • Next.js:            logs/nextjs.log"
echo -e "   • AI Agent:           logs/ai-agent.log"
if [ "$START_PROXY" = true ]; then
    echo -e "   • Cloud SQL Proxy:    logs/proxy.log"
fi
echo ""

echo -e "${BLUE}📊 View Logs in Real-time:${NC}"
echo -e "   • Next.js:            ${YELLOW}tail -f logs/nextjs.log${NC}"
echo -e "   • AI Agent:           ${YELLOW}tail -f logs/ai-agent.log${NC}"
if [ "$START_PROXY" = true ]; then
    echo -e "   • Cloud SQL Proxy:    ${YELLOW}tail -f logs/proxy.log${NC}"
fi
echo ""

echo -e "${BLUE}🛑 Stop All Services:${NC}"
echo -e "   Press ${RED}Ctrl+C${NC} in this terminal"
echo ""

print_header "🎉 Ready to Process Loan Applications!"

echo -e "${PURPLE}The system is now ready to:${NC}"
echo -e "  1. Accept loan applications from customers"
echo -e "  2. Store data in Google Cloud SQL"
echo -e "  3. Upload documents to Google Cloud Storage"
echo -e "  4. Process applications through AI Multi-Agent System"
echo -e "  5. Return intelligent loan decisions"
echo ""

# Keep script running and wait for user interrupt
echo -e "${YELLOW}Press Ctrl+C to stop all services...${NC}"
echo ""

# Wait for interrupt
while true; do
    sleep 1
done
