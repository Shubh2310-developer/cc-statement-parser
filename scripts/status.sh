#!/bin/bash

# Credit Card Statement Parser - Check Services Status
# This script checks the status of backend and frontend services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# PID files
PID_DIR="$PROJECT_DIR/pids"
BACKEND_PID="$PID_DIR/backend.pid"
FRONTEND_PID="$PID_DIR/frontend.pid"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  CC Statement Parser - Status${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check service status
check_service_status() {
    local pid_file=$1
    local service_name=$2
    local port=$3

    echo -e "${BLUE}$service_name:${NC}"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "  Status: ${GREEN}Running${NC}"
            echo "  PID: $pid"

            # Check if port is listening
            if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                echo -e "  Port $port: ${GREEN}Listening${NC}"
            else
                echo -e "  Port $port: ${RED}Not listening${NC}"
            fi
        else
            echo -e "  Status: ${RED}Not running${NC} (stale PID file)"
        fi
    else
        echo -e "  Status: ${RED}Not running${NC}"

        # Check if something is on the port anyway
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            local port_pid=$(lsof -Pi :$port -sTCP:LISTEN -t)
            echo -e "  Port $port: ${YELLOW}In use by PID $port_pid${NC}"
        else
            echo "  Port $port: Available"
        fi
    fi
    echo ""
}

# Check backend
check_service_status "$BACKEND_PID" "Backend (FastAPI)" "8000"

# Check frontend
check_service_status "$FRONTEND_PID" "Frontend (React)" "5173"

# Check API health
echo -e "${BLUE}API Health Check:${NC}"
if curl -s -f http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    response=$(curl -s http://localhost:8000/api/v1/health)
    echo -e "  Status: ${GREEN}Healthy${NC}"
    echo "  Response: $response"
else
    echo -e "  Status: ${RED}Unavailable${NC}"
fi
echo ""

# Check frontend accessibility
echo -e "${BLUE}Frontend Check:${NC}"
if curl -s -f http://localhost:5173 >/dev/null 2>&1; then
    echo -e "  Status: ${GREEN}Accessible${NC}"
    echo "  URL: http://localhost:5173"
else
    echo -e "  Status: ${RED}Unavailable${NC}"
fi
echo ""

echo -e "${BLUE}========================================${NC}"
echo ""
