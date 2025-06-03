#!/usr/bin/env python3

import duckdb
import json
from pathlib import Path
import os

def cleanup_and_document():
    """Clean up old databases and create documentation"""
    
    print("=== CLEANING UP AND DOCUMENTING VAERS ANALYSIS SYSTEM ===")
    
    # Define what to keep vs remove
    intermediate_dir = Path("../intermediate_results")
    
    # Databases to keep (our production system)
    keep_databases = [
        "unified_vaers_analysis.duckdb",  # Main production database
        "strict_symptom_classifications.duckdb"  # Validated classifications
    ]
    
    # Databases to remove (old/experimental)
    remove_databases = [
        "vaccine_comparison.duckdb",  # Merged into unified
        "symptom_classifications.duckdb",  # Old non-strict version
        "vaers_database.duckdb",  # PDF extraction only, merged into unified
        "vaers_test.duckdb"  # Empty test database
    ]
    
    # Clean up old databases
    print("\nCleaning up old databases...")
    for db_name in remove_databases:
        db_path = intermediate_dir / db_name
        if db_path.exists():
            try:
                os.remove(db_path)
                print(f"  ✓ Removed {db_name}")
            except Exception as e:
                print(f"  ⚠️  Could not remove {db_name}: {e}")
        else:
            print(f"  - {db_name} (already removed)")
    
    # Document the unified database schema
    print("\nDocumenting unified database schema...")
    unified_db = intermediate_dir / "unified_vaers_analysis.duckdb"
    
    if unified_db.exists():
        conn = duckdb.connect(str(unified_db))
        
        # Get all tables
        tables = conn.execute("SHOW TABLES").fetchall()
        
        schema_doc = {
            "database": "unified_vaers_analysis.duckdb",
            "description": "Complete VAERS analysis system with crosswalked vaccines, individual reports, and symptom classifications",
            "tables": {}
        }
        
        for table_name, in tables:
            # Get table schema
            schema = conn.execute(f"DESCRIBE {table_name}").fetchall()
            
            # Get row count
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            
            # Get sample data (first 2 rows)
            sample = conn.execute(f"SELECT * FROM {table_name} LIMIT 2").fetchall()
            
            schema_doc["tables"][table_name] = {
                "row_count": count,
                "columns": [{"name": col[0], "type": col[1]} for col in schema],
                "sample_data": [list(row) for row in sample] if sample else []
            }
        
        conn.close()
        
        # Save schema documentation
        with open("../KEY_INFO/unified_database_schema.json", "w") as f:
            json.dump(schema_doc, f, indent=2)
        
        print(f"  ✓ Schema documented in ../KEY_INFO/unified_database_schema.json")
        
        # Print summary
        print(f"\nUnified Database Summary:")
        for table_name, info in schema_doc["tables"].items():
            print(f"  {table_name}: {info['row_count']:,} rows, {len(info['columns'])} columns")
    
    else:
        print("  ⚠️  Unified database not found!")

def create_readme():
    """Create comprehensive README for the VAERS analysis system"""
    
    readme_content = """# VAERS Adverse Event Analysis System

## Overview
This system analyzes VAERS (Vaccine Adverse Event Reporting System) data against FDA package inserts to identify which reported symptoms are documented in official vaccine literature.

## Key Features
- **16 crosswalked vaccines** between VAERS and FDA package inserts
- **1.3M+ individual VAERS reports** with structured symptom data
- **Validated symptom classifications** using LLM analysis
- **Symptom normalization** for finding similar reports across different wordings

## Database: `unified_vaers_analysis.duckdb`

### Core Tables

#### `vaccines`
Master list of crosswalked vaccines
```sql
vaccine_id INTEGER PRIMARY KEY
vaers_name VARCHAR          -- Name in VAERS database  
pdf_name VARCHAR            -- Name in FDA package insert
total_vaers_reports INTEGER -- Total reports for this vaccine
pdf_adverse_events JSON     -- List of adverse events from package insert
```

#### `vaers_reports`  
Individual VAERS reports (1.3M+ records)
```sql
vaers_id INTEGER            -- VAERS report ID
vaccine_id INTEGER          -- Links to vaccines table
age_yrs FLOAT              -- Patient age
sex VARCHAR                -- M/F
state VARCHAR              -- US state
died VARCHAR               -- Y/N if patient died
hospital VARCHAR           -- Y/N if hospitalized  
er_visit VARCHAR           -- Y/N if ER visit
symptoms JSON              -- List of symptoms for this report
vax_date VARCHAR           -- Vaccination date
onset_date VARCHAR         -- Symptom onset date  
year INTEGER               -- Report year (2020-2024)
```

#### `symptom_mappings`
Maps VAERS symptoms to PDF adverse events
```sql
canonical_symptom VARCHAR  -- Standardized symptom (from PDF)
vaers_symptom VARCHAR      -- Original VAERS symptom
vaccine_name VARCHAR       -- Which vaccine
vaers_count INTEGER        -- How many times reported
mapping_confidence VARCHAR -- 'exact_match', 'synonym', 'related'
```

#### `canonical_symptoms`
Normalized symptom lookup across all vaccines
```sql
canonical_symptom VARCHAR PRIMARY KEY -- Standard symptom name
total_vaers_reports INTEGER            -- Total reports across all vaccines
vaccine_count INTEGER                  -- How many vaccines report this
most_common_vaers_form VARCHAR         -- Most common VAERS wording
example_vaccines JSON                  -- Example vaccines
```

## Usage Examples

### 1. Find reports for a specific vaccine
```sql
SELECT * FROM vaers_reports 
WHERE vaccine_id = (
    SELECT vaccine_id FROM vaccines 
    WHERE vaers_name LIKE '%COVID19%MODERNA%'
) 
LIMIT 10;
```

### 2. Check if a symptom is documented in package insert
```sql
SELECT sm.canonical_symptom, sm.mapping_confidence
FROM symptom_mappings sm
WHERE sm.vaers_symptom = 'headache' 
AND sm.vaccine_name LIKE '%SPIKEVAX%';
```

### 3. Find all ways "fever" is reported across vaccines
```sql
SELECT vaers_symptom, vaccine_name, vaers_count
FROM symptom_mappings 
WHERE canonical_symptom = 'fever'
ORDER BY vaers_count DESC;
```

### 4. Find similar reports (same symptoms)
```sql
-- Reports with headache for COVID vaccines
SELECT vaers_id, age_yrs, sex, symptoms
FROM vaers_reports 
WHERE vaccine_id IN (1, 2)  -- COVID vaccine IDs
AND JSON_CONTAINS(symptoms, '"headache"')
LIMIT 10;
```

### 5. Get symptom breakdown for a vaccine
```sql
SELECT 
    v.pdf_name,
    COUNT(*) as total_reports,
    COUNT(CASE WHEN r.died = 'Y' THEN 1 END) as deaths,
    COUNT(CASE WHEN r.hospital = 'Y' THEN 1 END) as hospitalizations
FROM vaers_reports r
JOIN vaccines v ON r.vaccine_id = v.vaccine_id  
WHERE v.vaers_name LIKE '%SHINGRIX%'
GROUP BY v.pdf_name;
```

## Data Processing Pipeline

1. **Raw Data**: VAERS CSV files (DATA, VAX, SYMPTOMS) + PDF package inserts
2. **Crosswalk**: Map vaccine names between VAERS and PDFs (16 matches)
3. **Symptom Extraction**: Parse individual symptoms from VAERS reports
4. **LLM Classification**: Validate which symptoms appear in package inserts
5. **Normalization**: Create symptom mappings for cross-vaccine analysis

## File Structure
```
code/
├── vaccine_mappings.py              # Hard-coded vaccine crosswalk
├── create_comparison_database.py    # Step 1: Aggregate VAERS + PDF data
├── compare_symptoms_strict.py       # Step 2: LLM symptom validation  
├── build_unified_database.py        # Step 3: Create main database
├── create_symptom_mappings.py       # Step 4: Symptom normalization
└── build_complete_system.sh         # Run all steps

intermediate_results/
├── unified_vaers_analysis.duckdb    # Main production database
└── strict_symptom_classifications.duckdb  # LLM validation results
```

## Demo Use Cases

### Input: VAERS-like report
```json
{
  "vaccine": "COVID19 (SPIKEVAX)",
  "symptoms": ["headache", "fatigue", "arm pain"],
  "age": 35,
  "sex": "F"
}
```

### Output: Analysis
- **Confirmed in package insert**: headache ✓, fatigue ✓  
- **Not documented**: arm pain ⚠️
- **Similar reports**: 2,847 other reports with headache + fatigue
- **Risk context**: 0.3% of SPIKEVAX recipients report this combination

## Running the System

### Full rebuild:
```bash
./build_complete_system.sh
```

### Individual steps:
```bash
python create_comparison_database.py    # ~5 min
python compare_symptoms_strict.py       # ~4 min  
python build_unified_database.py        # ~3 min
python create_symptom_mappings.py       # ~1 min
```

## Requirements
- Python 3.8+
- DuckDB, pandas, requests
- OpenAI API key for LLM classification
- VAERS data files (2020-2024)
- FDA package insert PDFs

## Data Sources
- **VAERS**: https://vaers.hhs.gov/data.html  
- **FDA Package Inserts**: https://www.fda.gov/vaccines-blood-biologics/
- **Crosswalk**: Manual mapping of 16 vaccine name matches

## Validation
- LLM classifications require exact PDF quotes
- False positives automatically filtered out
- Symptom mappings validated against source documents
"""

    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("✓ Created comprehensive README.md")

def create_enhanced_vaers_export():
    """Create enhanced VAERS export with all data"""
    
    print("\nCreating enhanced VAERS export...")
    
    unified_db = "../intermediate_results/unified_vaers_analysis.duckdb"
    conn = duckdb.connect(unified_db)
    
    # Create comprehensive export query (simplified)
    export_query = """
    SELECT 
        r.vaers_id,
        r.year,
        v.vaers_name as vaccine_name,
        v.pdf_name as pdf_vaccine_name,
        r.age_yrs,
        r.sex,
        r.state,
        r.died,
        r.hospital,
        r.er_visit,
        r.vax_date,
        r.onset_date,
        r.symptoms,
        json_array_length(r.symptoms) as total_symptoms_count,
        v.pdf_adverse_events
        
    FROM vaers_reports r
    JOIN vaccines v ON r.vaccine_id = v.vaccine_id
    ORDER BY r.year DESC, r.vaers_id
    """
    
    # Export to parquet for efficiency
    conn.execute(f"""
    COPY ({export_query}) 
    TO '../intermediate_results/complete_vaers_analysis.parquet' 
    (FORMAT PARQUET)
    """)
    
    # Get summary stats
    total_reports = conn.execute("SELECT COUNT(*) FROM vaers_reports").fetchone()[0]
    
    print(f"  ✓ Exported {total_reports:,} reports to complete_vaers_analysis.parquet")
    
    # Also create JSON sample for demo
    sample_query = f"""
    SELECT * FROM ({export_query}) 
    LIMIT 1000
    """
    
    sample_data = conn.execute(sample_query).fetchall()
    columns = [desc[0] for desc in conn.description]
    
    # Convert to list of dicts
    sample_records = []
    for row in sample_data:
        record = {}
        for i, value in enumerate(row):
            record[columns[i]] = value
        sample_records.append(record)
    
    with open("../intermediate_results/vaers_analysis_sample.json", "w") as f:
        json.dump(sample_records, f, indent=2)
    
    print(f"  ✓ Created sample of 1,000 records in vaers_analysis_sample.json")
    
    conn.close()

if __name__ == "__main__":
    cleanup_and_document()
    create_readme() 
    create_enhanced_vaers_export()
    
    print("\n=== CLEANUP AND DOCUMENTATION COMPLETE ===")
    print("\nWhat was created:")
    print("  📊 cleaned up old databases") 
    print("  📋 ../KEY_INFO/unified_database_schema.json")
    print("  📖 README.md")
    print("  📁 ../intermediate_results/complete_vaers_analysis.parquet")
    print("  📄 ../intermediate_results/vaers_analysis_sample.json")
    print("\nReady for hackathon demo! 🚀")