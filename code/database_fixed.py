import duckdb
import json
from pathlib import Path
import os
import sys
import pandas as pd

# ============= SETUP FUNCTIONS =============

def setup_database(db_path: str = "duckdb/vaers_analysis.db"):
    """Initialize DuckDB connection and create tables from JSON files."""
    # Create duckdb directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = duckdb.connect(db_path)
    
    # Create tables with proper schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fda_reports (
            vaccine_name VARCHAR,  -- The VAERS-compatible name
            vax_name VARCHAR,      -- Original FDA name
            vax_manu VARCHAR,
            adverse_event VARCHAR
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vaers_subset (
            VAERS_ID VARCHAR,
            AGE_YRS DOUBLE,
            SEX VARCHAR,
            vax_name VARCHAR,
            symptom VARCHAR
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS symptom_mappings (
            vaers_symptom VARCHAR,
            fda_adverse_event VARCHAR
        )
    """)
    
    return conn

def load_fda_reports(conn: duckdb.DuckDBPyConnection, filepath: str):
    """Load FDA reports data."""
    print("Loading FDA reports...")
    
    full_path = os.path.join("json_data", filepath)
    
    if not os.path.exists(full_path):
        print(f"ERROR: Could not find file: {full_path}")
        return False
    
    try:
        # Load JSON
        with open(full_path, 'r') as f:
            data = json.load(f)
        
        # Clear existing data
        conn.execute("DELETE FROM fda_reports")
        
        # Insert data
        for report in data:
            vaccine_name = report.get('vaccine_name', '')  # VAERS-compatible name
            vax_name = report.get('vax_name', '')  # Original FDA name
            vax_manu = report.get('vax_manu', '')
            
            for ae in report.get('adverse_events', []):
                conn.execute("""
                    INSERT INTO fda_reports (vaccine_name, vax_name, vax_manu, adverse_event)
                    VALUES (?, ?, ?, ?)
                """, [vaccine_name, vax_name, vax_manu, ae])
        
        count = conn.execute("SELECT COUNT(DISTINCT vaccine_name) FROM fda_reports").fetchone()[0]
        print(f"Loaded {count} vaccines from FDA reports")
        
        # Show sample
        print("\nSample FDA vaccines:")
        samples = conn.execute("""
            SELECT DISTINCT vaccine_name, vax_manu, COUNT(*) as ae_count
            FROM fda_reports
            GROUP BY vaccine_name, vax_manu
            ORDER BY vaccine_name
            LIMIT 5
        """).fetchdf()
        print(samples.to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"Error loading FDA reports: {e}")
        return False

def load_vaers_subset(conn: duckdb.DuckDBPyConnection, filepath: str):
    """Load VAERS subset data."""
    print("\nLoading VAERS subset...")
    
    full_path = os.path.join("json_data", filepath)
    
    if not os.path.exists(full_path):
        print(f"ERROR: Could not find file: {full_path}")
        return False
    
    try:
        # Load JSON - this might be large, so we'll process in chunks
        with open(full_path, 'r') as f:
            data = json.load(f)
        
        # Clear existing data
        conn.execute("DELETE FROM vaers_subset")
        
        # Process records
        insert_count = 0
        for record in data:
            vaers_id = record.get('VAERS_ID')
            age = record.get('AGE_YRS')
            sex = record.get('SEX')
            vax_names = record.get('VAX_NAME_list', [])
            symptoms = record.get('symptom_list', [])
            
            # Create a record for each vaccine-symptom combination
            for vax in vax_names:
                for symptom in symptoms:
                    conn.execute("""
                        INSERT INTO vaers_subset (VAERS_ID, AGE_YRS, SEX, vax_name, symptom)
                        VALUES (?, ?, ?, ?, ?)
                    """, [vaers_id, age, sex, vax, symptom])
                    insert_count += 1
        
        report_count = conn.execute("SELECT COUNT(DISTINCT VAERS_ID) FROM vaers_subset").fetchone()[0]
        vaccine_count = conn.execute("SELECT COUNT(DISTINCT vax_name) FROM vaers_subset").fetchone()[0]
        
        print(f"Loaded {report_count} VAERS reports with {vaccine_count} unique vaccines")
        print(f"Total vaccine-symptom records: {insert_count}")
        
        # Show sample
        print("\nTop VAERS vaccines by report count:")
        samples = conn.execute("""
            SELECT vax_name, COUNT(DISTINCT VAERS_ID) as report_count
            FROM vaers_subset
            GROUP BY vax_name
            ORDER BY report_count DESC
            LIMIT 5
        """).fetchdf()
        print(samples.to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"Error loading VAERS subset: {e}")
        return False

def load_symptom_mappings(conn: duckdb.DuckDBPyConnection, filepath: str):
    """Load symptom mappings data."""
    print("\nLoading symptom mappings...")
    
    full_path = os.path.join("json_data", filepath)
    
    if not os.path.exists(full_path):
        print(f"ERROR: Could not find file: {full_path}")
        return False
    
    try:
        # Load JSON
        with open(full_path, 'r') as f:
            data = json.load(f)
        
        # Clear existing data
        conn.execute("DELETE FROM symptom_mappings")
        
        # Insert data
        for mapping in data:
            vaers_symptom = mapping.get('vaers_symptom', '')
            fda_events = mapping.get('fda_adverse_events', [])
            
            for fda_event in fda_events:
                conn.execute("""
                    INSERT INTO symptom_mappings (vaers_symptom, fda_adverse_event)
                    VALUES (?, ?)
                """, [vaers_symptom, fda_event])
        
        count = conn.execute("SELECT COUNT(DISTINCT vaers_symptom) FROM symptom_mappings").fetchone()[0]
        print(f"Loaded {count} symptom mappings")
        
        return True
        
    except Exception as e:
        print(f"Error loading symptom mappings: {e}")
        return False

def analyze_matches(conn: duckdb.DuckDBPyConnection):
    """Analyze vaccine and symptom matches."""
    
    print("\n=== MATCHING ANALYSIS ===")
    
    # Check exact vaccine name matches
    print("\n1. Checking vaccine name matches...")
    vaccine_matches = conn.execute("""
        WITH vaers_vaccines AS (
            SELECT DISTINCT vax_name FROM vaers_subset
        ),
        fda_vaccines AS (
            SELECT DISTINCT vaccine_name FROM fda_reports
        )
        SELECT 
            COUNT(DISTINCT v.vax_name) as vaers_count,
            COUNT(DISTINCT f.vaccine_name) as fda_count,
            COUNT(DISTINCT CASE WHEN v.vax_name = f.vaccine_name THEN v.vax_name END) as exact_matches
        FROM vaers_vaccines v
        FULL OUTER JOIN fda_vaccines f ON v.vax_name = f.vaccine_name
    """).fetchone()
    
    print(f"VAERS vaccines: {vaccine_matches[0]}")
    print(f"FDA vaccines: {vaccine_matches[1]}")
    print(f"Exact matches: {vaccine_matches[2]}")
    
    # Show matched vaccines
    print("\nMatched vaccines:")
    matched = conn.execute("""
        SELECT DISTINCT 
            v.vax_name as vaccine,
            COUNT(DISTINCT v.VAERS_ID) as vaers_reports,
            COUNT(DISTINCT f.adverse_event) as fda_adverse_events
        FROM vaers_subset v
        INNER JOIN fda_reports f ON v.vax_name = f.vaccine_name
        GROUP BY v.vax_name
        ORDER BY vaers_reports DESC
    """).fetchdf()
    print(matched.to_string(index=False))
    
    # Analyze symptom matching
    print("\n2. Analyzing symptom matching...")
    
    # Create the main analysis view
    conn.execute("""
        CREATE OR REPLACE VIEW vaers_fda_analysis AS
        SELECT 
            v.VAERS_ID,
            v.vax_name as vaccine,
            v.symptom as vaers_symptom,
            sm.fda_adverse_event as mapped_fda_symptom,
            CASE 
                WHEN f.adverse_event IS NOT NULL THEN 'FDA Documented'
                WHEN sm.fda_adverse_event IS NOT NULL THEN 'Mapped but not in FDA'
                ELSE 'Not mapped'
            END as status
        FROM vaers_subset v
        LEFT JOIN symptom_mappings sm ON v.symptom = sm.vaers_symptom
        LEFT JOIN fda_reports f ON 
            v.vax_name = f.vaccine_name 
            AND sm.fda_adverse_event = f.adverse_event
    """)
    
    # Get overall statistics
    stats = conn.execute("""
        SELECT 
            COUNT(DISTINCT VAERS_ID) as total_reports,
            COUNT(DISTINCT vaccine) as total_vaccines,
            COUNT(*) as total_symptom_instances,
            COUNT(CASE WHEN status = 'FDA Documented' THEN 1 END) as fda_documented,
            COUNT(CASE WHEN status = 'Mapped but not in FDA' THEN 1 END) as mapped_not_fda,
            COUNT(CASE WHEN status = 'Not mapped' THEN 1 END) as not_mapped
        FROM vaers_fda_analysis
    """).fetchone()
    
    print(f"\nTotal VAERS reports: {stats[0]:,}")
    print(f"Total vaccines: {stats[1]}")
    print(f"Total symptom instances: {stats[2]:,}")
    print(f"FDA documented symptoms: {stats[3]:,} ({100*stats[3]/stats[2]:.1f}%)")
    print(f"Mapped but not in FDA list: {stats[4]:,} ({100*stats[4]/stats[2]:.1f}%)")
    print(f"Not mapped: {stats[5]:,} ({100*stats[5]/stats[2]:.1f}%)")
    
    # Show reports with high FDA match rate
    print("\n3. Reports with high FDA documentation rate:")
    high_match_reports = conn.execute("""
        WITH report_stats AS (
            SELECT 
                VAERS_ID,
                vaccine,
                COUNT(*) as total_symptoms,
                COUNT(CASE WHEN status = 'FDA Documented' THEN 1 END) as fda_documented,
                ROUND(100.0 * COUNT(CASE WHEN status = 'FDA Documented' THEN 1 END) / COUNT(*), 1) as match_rate
            FROM vaers_fda_analysis
            GROUP BY VAERS_ID, vaccine
            HAVING COUNT(*) >= 3  -- At least 3 symptoms
        )
        SELECT * FROM report_stats
        WHERE match_rate >= 50  -- At least 50% FDA documented
        ORDER BY match_rate DESC, total_symptoms DESC
        LIMIT 10
    """).fetchdf()
    
    if not high_match_reports.empty:
        print(high_match_reports.to_string(index=False))
    else:
        print("No reports found with high FDA match rate")
    
    # Show example of a well-matched report
    if not high_match_reports.empty:
        example_id = high_match_reports.iloc[0]['VAERS_ID']
        print(f"\n4. Example report details (VAERS_ID: {example_id}):")
        
        details = conn.execute("""
            SELECT 
                vaers_symptom,
                mapped_fda_symptom,
                status
            FROM vaers_fda_analysis
            WHERE VAERS_ID = ?
            ORDER BY status, vaers_symptom
        """, [example_id]).fetchdf()
        
        print(details.to_string(index=False))

def main():
    # Initialize database
    conn = setup_database()
    
    # Load data
    success = True
    success &= load_fda_reports(conn, "fda_reports.json")
    success &= load_vaers_subset(conn, "vaers_subset.json")
    success &= load_symptom_mappings(conn, "symptom_mappings.json")
    
    if not success:
        print("\nERROR: Failed to load all data files")
        return
    
    # Create indexes for better performance
    print("\nCreating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_vaers_vax ON vaers_subset(vax_name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_fda_vax ON fda_reports(vaccine_name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_symptom_map ON symptom_mappings(vaers_symptom)")
    
    # Analyze matches
    analyze_matches(conn)
    
    conn.close()

if __name__ == "__main__":
    main()