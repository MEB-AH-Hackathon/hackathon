#!/bin/bash

echo "=== BUILDING SIMPLIFIED 3-TABLE JSON SYSTEM ==="
echo "Creating 3 JSON files: fda_reports.json, vaers_subset.json, symptom_mappings.json"
echo ""

# Check if we have the VAERS data (from any source)
if [ ! -d "../vaers_data" ] && [ ! -d "../sample_data" ]; then
    echo "ERROR: No VAERS data found in ../vaers_data or ../sample_data"
    echo "Please ensure you have VAERS data available"
    exit 1
fi

# 1. Create VAERS subset (100K records)
echo "Step 1: Creating VAERS subset (100K records)..."
python create_proper_vaers_subset.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create VAERS subset"
    exit 1
fi
echo "✓ VAERS subset created"
echo ""

# 2. Create symptom mappings using Claude
echo "Step 2: Creating symptom mappings with Claude API..."
echo "This will take a few minutes for API calls..."
python create_real_symptom_mappings.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create symptom mappings"
    exit 1
fi
echo "✓ Symptom mappings created"
echo ""

echo "=== SIMPLIFIED SYSTEM COMPLETE ==="
echo ""
echo "Created 3 JSON files in ../json_data/:"
echo "  - fda_reports.json (FDA adverse events for 14 vaccines)"
echo "  - vaers_subset.json (100K VAERS reports with symptoms)"
echo "  - symptom_mappings.json (VAERS symptoms mapped to FDA events)"
echo ""
echo "Ready for hackathon demo!"
echo ""
echo "File sizes:"
ls -lh ../json_data/*.json | awk '{print "  " $9 ": " $5}'