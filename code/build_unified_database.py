#!/usr/bin/env python3

import duckdb
import pandas as pd
import json
from pathlib import Path
from collections import defaultdict
from vaccine_mappings import VACCINE_MAPPINGS

def build_unified_database():
    """Build a unified database for VAERS report analysis"""
    
    print("=== BUILDING UNIFIED VAERS ANALYSIS DATABASE ===")
    
    # Paths
    comparison_db = "../duckdb_data/vaccine_comparison.duckdb"
    classifications_db = "../duckdb_data/strict_symptom_classifications.duckdb"
    output_db = "../duckdb_data/unified_vaers_analysis.duckdb"
    json_output_dir = Path("../json_data")
    json_output_dir.mkdir(exist_ok=True)
    vaers_data_dir = Path("../vaers_data/vaers_data")
    
    # Connect to output database
    conn = duckdb.connect(output_db)
    
    # 1. Create vaccines table
    print("Creating vaccines table...")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS vaccines (
        vaccine_id INTEGER PRIMARY KEY,
        vaers_name VARCHAR,
        pdf_name VARCHAR,
        total_vaers_reports INTEGER,
        pdf_adverse_events JSON
    )
    """)
    
    # 2. Create symptom classifications table
    print("Creating symptom_classifications table...")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS symptom_classifications (
        vaccine_id INTEGER,
        symptom VARCHAR,
        classification VARCHAR,  -- 'confirmed' or 'not_confirmed'
        vaers_count INTEGER,
        FOREIGN KEY (vaccine_id) REFERENCES vaccines(vaccine_id)
    )
    """)
    
    # 3. Create individual VAERS reports table
    print("Creating vaers_reports table...")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS vaers_reports (
        vaers_id INTEGER,
        vaccine_id INTEGER,
        age_yrs FLOAT,
        sex VARCHAR,
        state VARCHAR,
        died VARCHAR,
        hospital VARCHAR,
        er_visit VARCHAR,
        symptoms JSON,  -- List of symptoms for this report
        vax_date VARCHAR,
        onset_date VARCHAR,
        year INTEGER,
        FOREIGN KEY (vaccine_id) REFERENCES vaccines(vaccine_id)
    )
    """)
    
    # Clear existing data
    conn.execute("DELETE FROM vaers_reports")
    conn.execute("DELETE FROM symptom_classifications") 
    conn.execute("DELETE FROM vaccines")
    
    # Load vaccine mappings
    vaccine_mappings = {m["vaers_vaccine"]: m["pdf_vaccine"] for m in VACCINE_MAPPINGS}
    
    # Get comparison data
    print("Loading vaccine comparison data...")
    comp_conn = duckdb.connect(comparison_db)
    vaccine_data = comp_conn.execute("""
    SELECT vaccine_name, vaers_name, total_vaers_reports, pdf_adverse_events
    FROM vaccine_comparisons
    """).fetchall()
    comp_conn.close()
    
    # Insert vaccines
    vaccine_id_map = {}
    for i, (pdf_name, vaers_name, total_reports, pdf_events) in enumerate(vaccine_data):
        vaccine_id = i + 1
        vaccine_id_map[vaers_name] = vaccine_id
        
        conn.execute("""
        INSERT INTO vaccines VALUES (?, ?, ?, ?, ?)
        """, [vaccine_id, vaers_name, pdf_name, total_reports, pdf_events])
    
    print(f"Inserted {len(vaccine_data)} vaccines")
    
    # Load symptom classifications if available
    try:
        print("Loading symptom classifications...")
        class_conn = duckdb.connect(classifications_db)
        classifications = class_conn.execute("""
        SELECT vaccine_name, symptom, classification, vaers_count
        FROM symptom_classifications
        """).fetchall()
        class_conn.close()
        
        # Insert classifications
        for vaers_name, symptom, classification, vaers_count in classifications:
            if vaers_name in vaccine_id_map:
                vaccine_id = vaccine_id_map[vaers_name]
                conn.execute("""
                INSERT INTO symptom_classifications VALUES (?, ?, ?, ?)
                """, [vaccine_id, symptom, classification, vaers_count])
        
        print(f"Inserted {len(classifications)} symptom classifications")
        
    except Exception as e:
        print(f"Warning: Could not load symptom classifications: {e}")
        print("You'll need to run compare_symptoms_llm.py first")
    
    # Load individual VAERS reports for crosswalked vaccines
    print("Loading individual VAERS reports...")
    years = [2020, 2021, 2022, 2023, 2024]
    total_reports = 0
    
    for year in years:
        print(f"  Processing {year}...")
        
        # File paths
        data_file = vaers_data_dir / f"{year}VAERSDATA.csv"
        vax_file = vaers_data_dir / f"{year}VAERSVAX.csv"
        symptoms_file = vaers_data_dir / f"{year}VAERSSYMPTOMS.csv"
        
        # Check if files exist
        if not all(f.exists() for f in [data_file, vax_file, symptoms_file]):
            print(f"    Skipping {year} - files not found")
            continue
        
        # Read VAX file to get vaccine-report mapping
        try:
            vax_df = pd.read_csv(vax_file, encoding='utf-8', low_memory=False)
        except UnicodeDecodeError:
            vax_df = pd.read_csv(vax_file, encoding='latin-1', low_memory=False)
        
        # Filter to crosswalked vaccines only
        crosswalked_vax = vax_df[vax_df['VAX_NAME'].isin(vaccine_mappings.keys())]
        if len(crosswalked_vax) == 0:
            continue
            
        vaers_ids = set(crosswalked_vax['VAERS_ID'].tolist())
        print(f"    Found {len(vaers_ids)} reports for crosswalked vaccines")
        
        # Read DATA file
        try:
            data_df = pd.read_csv(data_file, encoding='utf-8', low_memory=False)
        except UnicodeDecodeError:
            data_df = pd.read_csv(data_file, encoding='latin-1', low_memory=False)
        
        # Filter to our VAERS IDs
        data_df = data_df[data_df['VAERS_ID'].isin(vaers_ids)]
        
        # Read SYMPTOMS file  
        try:
            symptoms_df = pd.read_csv(symptoms_file, encoding='utf-8', low_memory=False, on_bad_lines='skip')
        except UnicodeDecodeError:
            try:
                symptoms_df = pd.read_csv(symptoms_file, encoding='latin-1', low_memory=False, on_bad_lines='skip')
            except Exception as e:
                print(f"    Warning: Could not read symptoms file: {e}")
                continue
        
        # Filter symptoms to our VAERS IDs
        symptoms_df = symptoms_df[symptoms_df['VAERS_ID'].isin(vaers_ids)]
        
        # Process symptoms into lists
        symptom_cols = [col for col in symptoms_df.columns if col.startswith('SYMPTOM') and not col.startswith('SYMPTOMVERSION')]
        symptom_cols = [col for col in symptom_cols if col[-1].isdigit()]
        
        def get_symptom_list(row):
            symptoms = []
            for col in symptom_cols:
                if pd.notna(row[col]) and str(row[col]).strip():
                    symptoms.append(str(row[col]).strip())
            return symptoms
        
        symptoms_df['symptom_list'] = symptoms_df.apply(get_symptom_list, axis=1)
        symptoms_summary = symptoms_df[['VAERS_ID', 'symptom_list']]
        
        # Create vaccine mapping for each report
        vax_mapping = {}
        for _, row in crosswalked_vax.iterrows():
            vaers_id = row['VAERS_ID']
            vax_name = row['VAX_NAME']
            if vax_name in vaccine_id_map:
                if vaers_id not in vax_mapping:
                    vax_mapping[vaers_id] = []
                vax_mapping[vaers_id].append(vaccine_id_map[vax_name])
        
        # Insert reports
        year_reports = 0
        for _, data_row in data_df.iterrows():
            vaers_id = data_row['VAERS_ID']
            
            # Get vaccine IDs for this report
            vaccine_ids = vax_mapping.get(vaers_id, [])
            if not vaccine_ids:
                continue
            
            # Get symptoms for this report
            symptoms_row = symptoms_summary[symptoms_summary['VAERS_ID'] == vaers_id]
            if len(symptoms_row) > 0:
                symptoms = symptoms_row.iloc[0]['symptom_list']
            else:
                symptoms = []
            
            # Insert one record per vaccine (some reports have multiple vaccines)
            for vaccine_id in vaccine_ids:
                conn.execute("""
                INSERT INTO vaers_reports VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    int(vaers_id),
                    vaccine_id,
                    data_row.get('AGE_YRS'),
                    data_row.get('SEX'),
                    data_row.get('STATE'),
                    data_row.get('DIED'),
                    data_row.get('HOSPITAL'),
                    data_row.get('ER_VISIT'),
                    json.dumps(symptoms),
                    data_row.get('VAX_DATE'),
                    data_row.get('ONSET_DATE'),
                    year
                ])
                year_reports += 1
        
        print(f"    Inserted {year_reports} report records")
        total_reports += year_reports
    
    # Create indexes for better performance
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_vaers_reports_vaccine_id ON vaers_reports(vaccine_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_vaers_reports_vaers_id ON vaers_reports(vaers_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_symptom_classifications_vaccine_id ON symptom_classifications(vaccine_id)")
    
    # Print summary
    print("\n=== DATABASE SUMMARY ===")
    
    vaccines_count = conn.execute("SELECT COUNT(*) FROM vaccines").fetchone()[0]
    classifications_count = conn.execute("SELECT COUNT(*) FROM symptom_classifications").fetchone()[0] 
    reports_count = conn.execute("SELECT COUNT(*) FROM vaers_reports").fetchone()[0]
    
    print(f"Vaccines: {vaccines_count}")
    print(f"Symptom classifications: {classifications_count}")
    print(f"VAERS reports: {reports_count:,}")
    
    # Show sample data
    print("\n=== SAMPLE QUERIES ===")
    
    # Sample vaccine
    sample_vaccine = conn.execute("""
    SELECT vaccine_id, vaers_name, pdf_name, total_vaers_reports
    FROM vaccines LIMIT 1
    """).fetchone()
    
    if sample_vaccine:
        vaccine_id, vaers_name, pdf_name, total_reports = sample_vaccine
        print(f"\nSample vaccine: {vaers_name}")
        print(f"  PDF name: {pdf_name}")
        print(f"  Total reports: {total_reports:,}")
        
        # Sample classifications
        classifications = conn.execute("""
        SELECT symptom, classification, vaers_count
        FROM symptom_classifications 
        WHERE vaccine_id = ?
        ORDER BY vaers_count DESC
        LIMIT 5
        """, [vaccine_id]).fetchall()
        
        if classifications:
            print(f"  Top classified symptoms:")
            for symptom, classification, count in classifications:
                print(f"    {symptom} ({count:,} reports): {classification}")
        
        # Sample reports
        reports = conn.execute("""
        SELECT vaers_id, age_yrs, sex, symptoms
        FROM vaers_reports 
        WHERE vaccine_id = ?
        LIMIT 3
        """, [vaccine_id]).fetchall()
        
        print(f"  Sample reports:")
        for vaers_id, age, sex, symptoms_json in reports:
            symptoms = json.loads(symptoms_json) if symptoms_json else []
            print(f"    Report {vaers_id}: Age {age}, Sex {sex}")
            print(f"      Symptoms: {symptoms[:3]}{'...' if len(symptoms) > 3 else ''}")
    
    # Export key tables to JSON before closing
    print("\nExporting to JSON...")
    
    # Export vaccines table
    vaccines_df = conn.execute("SELECT * FROM vaccines ORDER BY vaccine_id").fetchdf()
    vaccines_df['pdf_adverse_events'] = vaccines_df['pdf_adverse_events'].apply(json.loads)
    vaccines_json = vaccines_df.to_dict('records')
    
    with open(json_output_dir / "vaccines.json", 'w') as f:
        json.dump(vaccines_json, f, indent=2)
    
    # Export symptom classifications
    classifications_df = conn.execute("""
    SELECT sc.*, v.vaers_name as vaccine_name, v.pdf_name
    FROM symptom_classifications sc
    JOIN vaccines v ON sc.vaccine_id = v.vaccine_id
    ORDER BY vaccine_id, vaers_count DESC
    """).fetchdf()
    
    classifications_json = classifications_df.to_dict('records')
    
    with open(json_output_dir / "symptom_classifications_full.json", 'w') as f:
        json.dump(classifications_json, f, indent=2)
    
    # Export summary statistics
    summary_stats = {
        "total_vaccines": vaccines_count,
        "total_classifications": classifications_count,
        "total_reports": reports_count,
        "metadata": {
            "created_date": "2025-06-03",
            "description": "Unified VAERS analysis database with individual reports"
        }
    }
    
    with open(json_output_dir / "database_summary.json", 'w') as f:
        json.dump(summary_stats, f, indent=2)
    
    print(f"JSON files saved to: {json_output_dir}")
    
    conn.close()
    print(f"\nUnified database created: {output_db}")

if __name__ == "__main__":
    build_unified_database()