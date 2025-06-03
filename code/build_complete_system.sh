#!/bin/bash

echo "=== BUILDING COMPLETE VAERS ANALYSIS SYSTEM ==="
echo "This will take about 10-15 minutes total"
echo ""

# 1. Create comparison database (vaccines + VAERS symptom counts + PDF adverse events)
echo "Step 1: Creating vaccine comparison database..."
python create_comparison_database.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create comparison database"
    exit 1
fi
echo "✓ Comparison database created"
echo ""

# 2. Run strict symptom classification (20 random symptoms per vaccine)
echo "Step 2: Running strict symptom classification with PDF quotes..."
echo "This will take about 3-4 minutes (320 API calls)..."
python compare_symptoms_strict.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to run strict symptom classification"
    exit 1
fi
echo "✓ Strict symptom classification completed"
echo ""

# 3. Build unified VAERS analysis database
echo "Step 3: Building unified VAERS analysis database..."
python build_unified_database.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to build unified database"
    exit 1
fi
echo "✓ Unified database created"
echo ""

# 4. Create symptom mapping tables
echo "Step 4: Creating symptom mapping lookup tables..."
python create_symptom_mappings.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create symptom mappings"
    exit 1
fi
echo "✓ Symptom mappings created"
echo ""

echo "=== SYSTEM BUILD COMPLETE ==="
echo ""
echo "Created databases:"
echo "  - vaccine_comparison.duckdb (vaccine data + symptom counts)"
echo "  - strict_symptom_classifications.duckdb (validated symptom classifications)"
echo "  - unified_vaers_analysis.duckdb (complete system with all tables)"
echo ""
echo "Available tables in unified database:"
echo "  - vaccines (16 crosswalked vaccines)"
echo "  - vaers_reports (1.3M individual reports)"
echo "  - symptom_classifications (validated classifications)"
echo "  - symptom_mappings (VAERS symptom -> PDF adverse event mappings)"
echo "  - canonical_symptoms (normalized symptom lookup)"
echo ""

# 5. Export VAERS reports to JSON
echo "Step 5: Exporting VAERS reports to JSON..."
python export_vaers_reports.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to export VAERS reports"
    exit 1
fi
echo "✓ VAERS reports exported"
echo ""

echo "=== ALL DATA GENERATED ==="
echo ""
echo "DuckDB databases in ../duckdb_data/:"
echo "  - vaccine_comparison.duckdb"
echo "  - strict_symptom_classifications.duckdb"
echo "  - unified_vaers_analysis.duckdb"
echo ""
echo "JSON files in ../json_data/:"
echo "  - All vaccine and symptom data"
echo "  - VAERS report samples (1K, 10K, COVID, non-COVID)"
echo "  - Complete documentation"
echo ""
echo "Ready for hackathon demo!"
echo ""
echo "Test the system:"
echo "  python -c \"import duckdb; conn=duckdb.connect('../duckdb_data/unified_vaers_analysis.duckdb'); print(conn.execute('SELECT COUNT(*) FROM vaers_reports').fetchone())\""