#!/bin/bash
# Quick script to generate all bank statements

echo "======================================"
echo "  CC Statement Generator - Batch Run"
echo "======================================"
echo ""

python3 main_generator.py --all

echo ""
echo "======================================"
echo "Check output/ directory for PDFs"
echo "======================================"
