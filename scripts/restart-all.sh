#!/bin/bash

# Credit Card Statement Parser - Restart All Services
# This script restarts both backend and frontend services

set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Restarting all services...${NC}"
echo ""

# Stop all services
"$SCRIPT_DIR/stop-all.sh"

echo ""
echo "Waiting 2 seconds before starting..."
sleep 2
echo ""

# Start all services
"$SCRIPT_DIR/start-all.sh"
