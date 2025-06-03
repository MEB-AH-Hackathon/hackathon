#!/usr/bin/env python3

import duckdb
import pandas as pd
import json
from collections import defaultdict
from pathlib import Path

def create_symptom_mappings():
    """Create symptom mapping/normalization tables from strict classifications"""
    
    print("=== CREATING SYMPTOM MAPPING TABLES ===")
    
    # Input and output databases
    strict_db = "../duckdb_data/strict_symptom_classifications.duckdb"
    unified_db = "../duckdb_data/unified_vaers_analysis.duckdb"
    json_output_dir = Path("../json_data")
    json_output_dir.mkdir(exist_ok=True)
    
    # Connect to databases
    strict_conn = duckdb.connect(strict_db)
    unified_conn = duckdb.connect(unified_db)
    
    # Create symptom mapping table in unified database
    print("Creating symptom_mappings table...")
    unified_conn.execute("""
    CREATE TABLE IF NOT EXISTS symptom_mappings (
        canonical_symptom VARCHAR,  -- standardized symptom name (PDF adverse event)
        vaers_symptom VARCHAR,      -- original VAERS symptom
        vaccine_name VARCHAR,       -- which vaccine this mapping is from
        vaers_count INTEGER,        -- how many times this VAERS symptom was reported
        mapping_confidence VARCHAR, -- 'exact_match', 'synonym', 'related'
        PRIMARY KEY (canonical_symptom, vaers_symptom, vaccine_name)
    )
    """)
    
    # Create cross-vaccine symptom lookup table
    unified_conn.execute("""
    CREATE TABLE IF NOT EXISTS canonical_symptoms (
        canonical_symptom VARCHAR PRIMARY KEY,
        total_vaers_reports INTEGER,        -- total reports across all vaccines
        vaccine_count INTEGER,              -- how many vaccines report this symptom
        most_common_vaers_form VARCHAR,     -- most common way it's reported in VAERS
        example_vaccines JSON               -- example vaccines that report this
    )
    """)
    
    # Clear existing data
    unified_conn.execute("DELETE FROM symptom_mappings")
    unified_conn.execute("DELETE FROM canonical_symptoms")
    
    # Get confirmed classifications from strict database
    print("Loading strict classifications...")
    classifications = strict_conn.execute("""
    SELECT vaccine_name, symptom, matched_pdf_event, vaers_count
    FROM strict_symptom_classifications 
    WHERE classification = 'confirmed'
    AND matched_pdf_event != 'none'
    ORDER BY vaers_count DESC
    """).fetchall()
    
    print(f"Found {len(classifications)} confirmed symptom mappings")
    
    # Create individual mappings
    mapping_records = []
    canonical_symptom_data = defaultdict(lambda: {
        'total_reports': 0,
        'vaccines': set(),
        'vaers_forms': defaultdict(int)
    })
    
    for vaccine_name, vaers_symptom, canonical_symptom, vaers_count in classifications:
        
        # Determine mapping confidence
        if vaers_symptom.lower() == canonical_symptom.lower():
            confidence = 'exact_match'
        elif any(word in vaers_symptom.lower() for word in canonical_symptom.lower().split()):
            confidence = 'synonym'
        else:
            confidence = 'related'
        
        # Add to mapping records
        mapping_records.append({
            'canonical_symptom': canonical_symptom,
            'vaers_symptom': vaers_symptom,
            'vaccine_name': vaccine_name,
            'vaers_count': vaers_count,
            'mapping_confidence': confidence
        })
        
        # Accumulate canonical symptom data
        canonical_symptom_data[canonical_symptom]['total_reports'] += vaers_count
        canonical_symptom_data[canonical_symptom]['vaccines'].add(vaccine_name)
        canonical_symptom_data[canonical_symptom]['vaers_forms'][vaers_symptom] += vaers_count
    
    # Insert mapping records
    if mapping_records:
        mappings_df = pd.DataFrame(mapping_records)
        unified_conn.execute("INSERT INTO symptom_mappings SELECT * FROM mappings_df")
        print(f"Inserted {len(mapping_records)} symptom mappings")
    
    # Create canonical symptom records
    canonical_records = []
    for canonical_symptom, data in canonical_symptom_data.items():
        
        # Find most common VAERS form
        most_common_vaers = max(data['vaers_forms'].items(), key=lambda x: x[1])[0]
        
        # Create example vaccines list (up to 5)
        example_vaccines = list(data['vaccines'])[:5]
        
        canonical_records.append({
            'canonical_symptom': canonical_symptom,
            'total_vaers_reports': data['total_reports'],
            'vaccine_count': len(data['vaccines']),
            'most_common_vaers_form': most_common_vaers,
            'example_vaccines': json.dumps(example_vaccines)
        })
    
    # Insert canonical symptom records
    if canonical_records:
        canonical_df = pd.DataFrame(canonical_records)
        unified_conn.execute("INSERT INTO canonical_symptoms SELECT * FROM canonical_df")
        print(f"Inserted {len(canonical_records)} canonical symptoms")
    
    # Create indexes for lookups
    print("Creating indexes...")
    unified_conn.execute("CREATE INDEX IF NOT EXISTS idx_symptom_mappings_vaers ON symptom_mappings(vaers_symptom)")
    unified_conn.execute("CREATE INDEX IF NOT EXISTS idx_symptom_mappings_canonical ON symptom_mappings(canonical_symptom)")
    unified_conn.execute("CREATE INDEX IF NOT EXISTS idx_canonical_symptoms_name ON canonical_symptoms(canonical_symptom)")
    
    # Show summary and examples
    print("\n=== SYMPTOM MAPPING SUMMARY ===")
    
    total_mappings = unified_conn.execute("SELECT COUNT(*) FROM symptom_mappings").fetchone()[0]
    total_canonical = unified_conn.execute("SELECT COUNT(*) FROM canonical_symptoms").fetchone()[0]
    
    print(f"Total symptom mappings: {total_mappings}")
    print(f"Total canonical symptoms: {total_canonical}")
    
    # Show top canonical symptoms by report count
    print(f"\nTop canonical symptoms by total VAERS reports:")
    top_symptoms = unified_conn.execute("""
    SELECT canonical_symptom, total_vaers_reports, vaccine_count, most_common_vaers_form
    FROM canonical_symptoms
    ORDER BY total_vaers_reports DESC
    LIMIT 10
    """).fetchall()
    
    for symptom, reports, vax_count, common_form in top_symptoms:
        print(f"  '{symptom}': {reports:,} reports across {vax_count} vaccines")
        print(f"    Most common VAERS form: '{common_form}'")
    
    # Show example mapping usage
    print(f"\n=== EXAMPLE LOOKUP USAGE ===")
    print("To find all VAERS symptoms that map to 'headache':")
    headache_mappings = unified_conn.execute("""
    SELECT vaers_symptom, vaccine_name, vaers_count, mapping_confidence
    FROM symptom_mappings 
    WHERE canonical_symptom = 'headache'
    ORDER BY vaers_count DESC
    """).fetchall()
    
    if headache_mappings:
        print(f"Found {len(headache_mappings)} different ways 'headache' is reported:")
        for vaers_form, vaccine, count, confidence in headache_mappings[:5]:
            print(f"  '{vaers_form}' ({vaccine}): {count:,} reports [{confidence}]")
    
    # Export to JSON before closing
    print("\nExporting to JSON...")
    
    # Export symptom mappings
    mappings_df = unified_conn.execute("SELECT * FROM symptom_mappings ORDER BY vaers_count DESC").fetchdf()
    mappings_json = mappings_df.to_dict('records')
    
    with open(json_output_dir / "symptom_mappings_final.json", 'w') as f:
        json.dump(mappings_json, f, indent=2)
    
    # Export canonical symptoms
    canonical_df = unified_conn.execute("SELECT * FROM canonical_symptoms ORDER BY total_vaers_reports DESC").fetchdf()
    canonical_df['example_vaccines'] = canonical_df['example_vaccines'].apply(json.loads)
    canonical_json = canonical_df.to_dict('records')
    
    with open(json_output_dir / "canonical_symptoms.json", 'w') as f:
        json.dump(canonical_json, f, indent=2)
    
    print(f"JSON files saved to: {json_output_dir}")
    
    strict_conn.close()
    unified_conn.close()
    
    print(f"\nSymptom mappings added to: {unified_db}")

if __name__ == "__main__":
    create_symptom_mappings()