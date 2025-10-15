#!/bin/bash

# Credit Card Statement Parser - Stop All Services
# This script stops both backend and frontend services

set -e

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
echo -e "${BLUE}  CC Statement Parser - Stop Services${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to stop a service
stop_service() {
    local pid_file=$1
    local service_name=$2

    if [ ! -f "$pid_file" ]; then
        echo -e "${YELLOW}⚠ $service_name PID file not found${NC}"
        return 0
    fi

    local pid=$(cat "$pid_file")

    if ps -p "$pid" > /dev/null 2>&1; then
        echo -e "${BLUE}Stopping $service_name (PID: $pid)...${NC}"
        kill "$pid" 2>/dev/null || true

        # Wait for process to stop (max 10 seconds)
        local count=0
        while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done

        # Force kill if still running
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}  → Force killing $service_name...${NC}"
            kill -9 "$pid" 2>/dev/null || true
        fi

        echo -e "${GREEN}✓ $service_name stopped${NC}"
    else
        echo -e "${YELLOW}⚠ $service_name is not running${NC}"
    fi

    rm -f "$pid_file"
}

# Stop services
stop_service "$FRONTEND_PID" "Frontend"
stop_service "$BACKEND_PID" "Backend"

# Also kill any remaining processes by port
echo ""
echo -e "${BLUE}Cleaning up any remaining processes...${NC}"

# Kill any process on port 8000 (backend)
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "  → Killing process on port 8000..."
    lsof -Pi :8000 -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
fi

# Kill any process on port 5173 (frontend)
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "  → Killing process on port 5173..."
    lsof -Pi :5173 -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
fi

# Kill any remaining uvicorn processes
pkill -f "uvicorn.*main:app" 2>/dev/null || true

# Kill any remaining npm/vite processes from this project
pkill -f "vite.*--port 5173" 2>/dev/null || true

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  All Services Stopped${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
