#!/bin/bash

# Credit Card Statement Parser - Start All Services
# This script starts both backend and frontend services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Log files
LOG_DIR="$PROJECT_DIR/logs"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

# PID files
PID_DIR="$PROJECT_DIR/pids"
BACKEND_PID="$PID_DIR/backend.pid"
FRONTEND_PID="$PID_DIR/frontend.pid"

# Create necessary directories
mkdir -p "$LOG_DIR"
mkdir -p "$PID_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  CC Statement Parser - Start Services${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check if a service is already running
check_service() {
    local pid_file=$1
    local service_name=$2

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠ $service_name is already running (PID: $pid)${NC}"
            return 0
        else
            # PID file exists but process is not running, clean it up
            rm -f "$pid_file"
        fi
    fi
    return 1
}

# Function to start backend
start_backend() {
    echo -e "${BLUE}Starting Backend...${NC}"

    if check_service "$BACKEND_PID" "Backend"; then
        return 0
    fi

    # Check if backend directory exists
    if [ ! -d "$BACKEND_DIR" ]; then
        echo -e "${RED}✗ Backend directory not found: $BACKEND_DIR${NC}"
        exit 1
    fi

    # Initialize database if needed
    cd "$BACKEND_DIR"
    echo "  → Initializing database..."
    python init_db_standalone.py 2>&1 | tee -a "$BACKEND_LOG"

    # Start backend server
    echo "  → Starting FastAPI server on port 8000..."
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
    local backend_pid=$!
    echo $backend_pid > "$BACKEND_PID"

    # Wait a bit and check if it started successfully
    sleep 3
    if ps -p $backend_pid > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend started successfully (PID: $backend_pid)${NC}"
        echo "  → API: http://localhost:8000"
        echo "  → Docs: http://localhost:8000/docs"
        echo "  → Logs: $BACKEND_LOG"
    else
        echo -e "${RED}✗ Backend failed to start. Check logs: $BACKEND_LOG${NC}"
        rm -f "$BACKEND_PID"
        exit 1
    fi
}

# Function to start frontend
start_frontend() {
    echo ""
    echo -e "${BLUE}Starting Frontend...${NC}"

    if check_service "$FRONTEND_PID" "Frontend"; then
        return 0
    fi

    # Check if frontend directory exists
    if [ ! -d "$FRONTEND_DIR" ]; then
        echo -e "${RED}✗ Frontend directory not found: $FRONTEND_DIR${NC}"
        exit 1
    fi

    cd "$FRONTEND_DIR"

    # Check if node_modules exists, install if not
    if [ ! -d "node_modules" ]; then
        echo "  → Installing dependencies..."
        npm install 2>&1 | tee -a "$FRONTEND_LOG"
    fi

    # Start frontend dev server
    echo "  → Starting React dev server on port 5173..."
    nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
    local frontend_pid=$!
    echo $frontend_pid > "$FRONTEND_PID"

    # Wait a bit and check if it started successfully
    sleep 5
    if ps -p $frontend_pid > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend started successfully (PID: $frontend_pid)${NC}"
        echo "  → App: http://localhost:5173"
        echo "  → Logs: $FRONTEND_LOG"
    else
        echo -e "${RED}✗ Frontend failed to start. Check logs: $FRONTEND_LOG${NC}"
        rm -f "$FRONTEND_PID"
        exit 1
    fi
}

# Main execution
echo -e "${YELLOW}Starting all services...${NC}"
echo ""

start_backend
start_frontend

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  All Services Started Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Service URLs:${NC}"
echo "  • Frontend:  http://localhost:5173"
echo "  • Backend:   http://localhost:8000"
echo "  • API Docs:  http://localhost:8000/docs"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo "  • Backend:   $BACKEND_LOG"
echo "  • Frontend:  $FRONTEND_LOG"
echo ""
echo -e "${BLUE}To stop all services:${NC}"
echo "  ./scripts/stop-all.sh"
echo ""
echo -e "${BLUE}To view logs:${NC}"
echo "  tail -f $BACKEND_LOG"
echo "  tail -f $FRONTEND_LOG"
echo ""
