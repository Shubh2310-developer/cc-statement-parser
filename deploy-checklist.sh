#!/bin/bash

# Deployment Pre-flight Checklist Script
# Run this before deploying to ensure everything is ready

echo "🚀 Credit Card Statement Parser - Deployment Checklist"
echo "======================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Check function
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1"
        ((FAILED++))
    fi
}

echo "1. Checking Backend..."
echo "----------------------"

# Check if backend directory exists
cd backend 2>/dev/null
check "Backend directory exists"

# Check requirements.txt
test -f requirements.txt
check "requirements.txt exists"

# Check main.py
test -f app/main.py
check "app/main.py exists"

# Check config
test -f app/config.py
check "app/config.py exists"

# Check all parsers
test -f app/core/parsers/sbi_parser.py
check "SBI parser exists"
test -f app/core/parsers/hdfc_parser.py
check "HDFC parser exists"
test -f app/core/parsers/icici_parser.py
check "ICICI parser exists"
test -f app/core/parsers/axis_parser.py
check "Axis parser exists"
test -f app/core/parsers/amex_parser.py
check "Amex parser exists"

cd ..

echo ""
echo "2. Checking Frontend..."
echo "----------------------"

cd frontend 2>/dev/null
check "Frontend directory exists"

# Check package.json
test -f package.json
check "package.json exists"

# Check if node_modules exists
test -d node_modules
check "node_modules installed (npm install)"

# Check main files
test -f src/main.jsx
check "src/main.jsx exists"

test -f src/services/api.js
check "API service configured"

test -f .env.example
check ".env.example created"

cd ..

echo ""
echo "3. Checking Git Repository..."
echo "----------------------------"

# Check if git initialized
git rev-parse --git-dir > /dev/null 2>&1
check "Git repository initialized"

# Check if remote exists
git remote -v | grep -q origin
check "Git remote 'origin' configured"

# Check for uncommitted changes
if [[ -z $(git status -s) ]]; then
    echo -e "${GREEN}✓${NC} No uncommitted changes"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Uncommitted changes detected (commit before deploy)"
    ((FAILED++))
fi

echo ""
echo "4. Checking Configuration Files..."
echo "---------------------------------"

test -f backend/render.yaml
check "Backend render.yaml exists"

test -f backend/.env.production
check "Backend .env.production exists"

test -f DEPLOYMENT.md
check "DEPLOYMENT.md guide exists"

test -f README.md
check "README.md exists"

echo ""
echo "5. Checking Python Dependencies..."
echo "---------------------------------"

# Check Python version
python3 --version | grep -q "3.10"
check "Python 3.10+ installed"

# Check if backend dependencies can be imported
cd backend
python3 -c "import fastapi" 2>/dev/null
check "FastAPI installed"

python3 -c "import pdfplumber" 2>/dev/null
check "pdfplumber installed"

cd ..

echo ""
echo "======================================================"
echo "Summary:"
echo "--------"
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
else
    echo -e "${GREEN}Failed: $FAILED${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Ready to deploy.${NC}"
    echo ""
    echo "Next Steps:"
    echo "1. Push to GitHub: git push origin main"
    echo "2. Deploy backend: Follow DEPLOYMENT.md Part 1"
    echo "3. Deploy frontend: Follow DEPLOYMENT.md Part 2"
    echo "4. Read full guide: cat DEPLOYMENT.md"
else
    echo -e "${RED}✗ Some checks failed. Fix issues before deploying.${NC}"
    echo ""
    echo "Common fixes:"
    echo "- Run: cd frontend && npm install"
    echo "- Run: git init && git add . && git commit -m 'Initial commit'"
    echo "- Run: git remote add origin YOUR_GITHUB_URL"
fi

echo ""
