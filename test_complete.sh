#!/bin/bash

echo "=== Testing Complete PDF Processing Flow ==="
echo ""

# Test HDFC
echo "1. Uploading HDFC PDF..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/parse -F "file=@/home/ghost/cc-statement-parser/HDFCCCSAMPLE.pdf")
JOBID=$(echo $RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
echo "   Job ID: $JOBID"

echo "2. Waiting for processing..."
sleep 10

echo "3. Fetching results..."
curl -s "http://localhost:8000/api/v1/jobs/$JOBID" | python -m json.tool

echo ""
echo "=== Test Complete ==="
