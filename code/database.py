import duckdb
import json
from pathlib import Path
import os
import sys
import pandas as pd
from difflib import SequenceMatcher

# ============= SETUP FUNCTIONS FROM ORIGINAL SCRIPT =============

def setup_database(db_path: str = "../duckdb/vaers_analysis.db"):
    """Initialize DuckDB connection and create tables from JSON files."""
    # Create duckdb directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = duckdb.connect(db_path)
    
    # Create tables with proper schema based on actual data structure
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fda_reports (
            filename VARCHAR,
            vax_type VARCHAR,
            vax_name VARCHAR,
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

def check_file_exists(filepath: str) -> bool:
    """Check if file exists and print helpful message if not."""
    if not os.path.exists(filepath):
        print(f"ERROR: Could not find file: {filepath}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for: {os.path.abspath(filepath)}")
        return False
    return True

def load_fda_reports(conn: duckdb.DuckDBPyConnection, filepath: str):
    """Load FDA reports data, normalizing the structure."""
    print("Loading FDA reports...")
    
    # Construct full path
    full_path = os.path.join("..", "json_data", filepath)
    
    if not check_file_exists(full_path):
        return False
    
    try:
        # First, load the JSON file into a temporary table
        conn.execute(f"""
            CREATE OR REPLACE TABLE temp_fda AS 
            SELECT * FROM read_json_auto('{full_path}')
        """)
        
        # Check the structure
        columns = conn.execute("DESCRIBE temp_fda").fetchall()
        print(f"FDA reports columns: {[col[0] for col in columns]}")
        
        # Clear existing data
        conn.execute("DELETE FROM fda_reports")
        
        # Unnest the adverse_events array and insert into normalized table
        conn.execute("""
            INSERT INTO fda_reports
            SELECT 
                vax_name,
                vax_manu,
                vax_type,
                filename,
                UNNEST(adverse_events) as adverse_event
            FROM temp_fda
            WHERE adverse_events IS NOT NULL
        """)
        
        # Drop temporary table
        conn.execute("DROP TABLE temp_fda")
        
        count = conn.execute("SELECT COUNT(DISTINCT vax_name) FROM fda_reports").fetchone()[0]
        print(f"Loaded {count} vaccines from FDA reports")
        return True
        
    except Exception as e:
        print(f"Error loading FDA reports: {e}")
        return False

def load_vaers_subset(conn: duckdb.DuckDBPyConnection, filepath: str):
    """Load VAERS subset data, normalizing the structure."""
    print("Loading VAERS subset...")
    
    # Construct full path
    full_path = os.path.join("..", "json_data", filepath)
    
    if not check_file_exists(full_path):
        return False
    
    try:
        # Load JSON into temporary table
        conn.execute(f"""
            CREATE OR REPLACE TABLE temp_vaers AS 
            SELECT * FROM read_json_auto('{full_path}')
        """)
        
        # Check the structure
        columns = conn.execute("DESCRIBE temp_vaers").fetchall()
        print(f"VAERS columns: {[col[0] for col in columns]}")
        
        # Clear existing data
        conn.execute("DELETE FROM vaers_subset")
        
        # Unnest both VAX_NAME_list and symptom_list arrays
        conn.execute("""
            INSERT INTO vaers_subset
            SELECT 
                VAERS_ID,
                AGE_YRS,
                SEX,
                UNNEST(VAX_NAME_list) as vax_name,
                UNNEST(symptom_list) as symptom
            FROM temp_vaers
            WHERE VAX_NAME_list IS NOT NULL AND symptom_list IS NOT NULL
        """)
        
        conn.execute("DROP TABLE temp_vaers")
        
        count = conn.execute("SELECT COUNT(DISTINCT VAERS_ID) FROM vaers_subset").fetchone()[0]
        print(f"Loaded {count} VAERS reports")
        return True
        
    except Exception as e:
        print(f"Error loading VAERS subset: {e}")
        return False

def load_symptom_mappings(conn: duckdb.DuckDBPyConnection, filepath: str):
    """Load symptom mappings data, normalizing the structure."""
    print("Loading symptom mappings...")
    
    # Construct full path
    full_path = os.path.join("..", "json_data", filepath)
    
    if not check_file_exists(full_path):
        return False
    
    try:
        # Load JSON into temporary table
        conn.execute(f"""
            CREATE OR REPLACE TABLE temp_mappings AS 
            SELECT * FROM read_json_auto('{full_path}')
        """)
        
        # Check the structure
        columns = conn.execute("DESCRIBE temp_mappings").fetchall()
        print(f"Symptom mappings columns: {[col[0] for col in columns]}")
        
        # Clear existing data
        conn.execute("DELETE FROM symptom_mappings")
        
        # Unnest the fda_adverse_events array
        conn.execute("""
            INSERT INTO symptom_mappings
            SELECT 
                vaers_symptom,
                UNNEST(fda_adverse_events) as fda_adverse_event
            FROM temp_mappings
            WHERE fda_adverse_events IS NOT NULL AND ARRAY_LENGTH(fda_adverse_events) > 0
        """)
        
        conn.execute("DROP TABLE temp_mappings")
        
        count = conn.execute("SELECT COUNT(DISTINCT vaers_symptom) FROM symptom_mappings").fetchone()[0]
        print(f"Loaded {count} symptom mappings")
        return True
        
    except Exception as e:
        print(f"Error loading symptom mappings: {e}")
        return False

def load_all_data(conn: duckdb.DuckDBPyConnection):
    """Load all data files if tables are empty."""
    # Check if data is already loaded
    try:
        vaers_count = conn.execute("SELECT COUNT(*) FROM vaers_subset").fetchone()[0]
        if vaers_count > 0:
            print("Data already loaded, skipping data loading step.")
            return True
    except:
        pass
    
    print("Loading data files...")
    success = True
    success &= load_fda_reports(conn, "fda_reports_cleaned.json")
    success &= load_vaers_subset(conn, "vaers_subset.json") 
    success &= load_symptom_mappings(conn, "symptom_mappings.json")
    
    if success:
        # Create indexes for better performance
        print("\nCreating indexes...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_vaers_id ON vaers_subset(VAERS_ID)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_vaers_symptom ON symptom_mappings(vaers_symptom)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_fda_vaccine ON fda_reports(vax_name)")
    
    return success

# ============= VACCINE MAPPING ANALYSIS FUNCTIONS =============

def analyze_vaccine_name_matching(conn: duckdb.DuckDBPyConnection):
    """Analyze how well VAERS vaccine names match FDA vaccine names."""
    
    print("\n=== Vaccine Name Matching Analysis ===\n")
    
    # Get unique vaccines from both sources
    vaers_vaccines = conn.execute("""
        SELECT DISTINCT vax_name, COUNT(DISTINCT VAERS_ID) as report_count
        FROM vaers_subset
        WHERE vax_name IS NOT NULL
        GROUP BY vax_name
        ORDER BY report_count DESC
    """).fetchdf()
    
    fda_vaccines = conn.execute("""
        SELECT DISTINCT vax_name, vax_manu, COUNT(DISTINCT adverse_event) as ae_count
        FROM fda_reports
        WHERE vax_name IS NOT NULL
        GROUP BY vax_name, vax_manu
        ORDER BY ae_count DESC
    """).fetchdf()
    
    print(f"Total unique vaccines in VAERS: {len(vaers_vaccines)}")
    print(f"Total unique vaccines in FDA: {len(fda_vaccines)}")
    
    # Check exact matches (case-insensitive)
    print("\n=== Exact Matches (case-insensitive) ===")
    exact_matches = conn.execute("""
        WITH vaers_vax AS (
            SELECT DISTINCT UPPER(TRIM(vax_name)) as vax_upper, vax_name, COUNT(DISTINCT VAERS_ID) as vaers_count
            FROM vaers_subset
            WHERE vax_name IS NOT NULL
            GROUP BY vax_name
        ),
        fda_vax AS (
            SELECT DISTINCT UPPER(TRIM(vax_name)) as vax_upper, vax_name, vax_manu
            FROM fda_reports
            WHERE vax_name IS NOT NULL
        )
        SELECT 
            v.vax_name as vaers_name,
            f.vax_name as fda_name,
            f.vax_manu as fda_manufacturer,
            v.vaers_count
        FROM vaers_vax v
        INNER JOIN fda_vax f ON v.vax_upper = f.vax_upper
        ORDER BY v.vaers_count DESC
    """).fetchdf()
    
    print(f"Found {len(exact_matches)} exact matches")
    if len(exact_matches) > 0:
        print("\nTop 10 exact matches:")
        print(exact_matches.head(10).to_string(index=False))
    
    # Find VAERS vaccines with no exact match
    print("\n=== Top VAERS Vaccines with NO Exact Match in FDA ===")
    no_match_vaers = conn.execute("""
        WITH vaers_vax AS (
            SELECT DISTINCT vax_name, COUNT(DISTINCT VAERS_ID) as report_count
            FROM vaers_subset
            WHERE vax_name IS NOT NULL
            GROUP BY vax_name
        ),
        fda_vax AS (
            SELECT DISTINCT UPPER(TRIM(vax_name)) as vax_upper
            FROM fda_reports
            WHERE vax_name IS NOT NULL
        )
        SELECT v.vax_name, v.report_count
        FROM vaers_vax v
        WHERE UPPER(TRIM(v.vax_name)) NOT IN (SELECT vax_upper FROM fda_vax)
        ORDER BY v.report_count DESC
        LIMIT 20
    """).fetchdf()
    
    print(f"Total VAERS vaccines with no FDA match: {len(conn.execute("""
        WITH vaers_vax AS (
            SELECT DISTINCT vax_name
            FROM vaers_subset
            WHERE vax_name IS NOT NULL
        ),
        fda_vax AS (
            SELECT DISTINCT UPPER(TRIM(vax_name)) as vax_upper
            FROM fda_reports
            WHERE vax_name IS NOT NULL
        )
        SELECT v.vax_name
        FROM vaers_vax v
        WHERE UPPER(TRIM(v.vax_name)) NOT IN (SELECT vax_upper FROM fda_vax)
    """).fetchdf())}")
    print("\nTop unmatched VAERS vaccines:")
    print(no_match_vaers.to_string(index=False))
    
    return exact_matches, no_match_vaers, fda_vaccines

def create_vaccine_mapping_table(conn: duckdb.DuckDBPyConnection):
    """Create a mapping table for vaccine name variations."""
    
    print("\n=== Creating Vaccine Mapping Table ===")
    
    # Create mapping table
    conn.execute("""
        CREATE OR REPLACE TABLE vaccine_name_mappings (
            vaers_name VARCHAR,
            fda_name VARCHAR,
            mapping_type VARCHAR,  -- 'exact', 'contains', 'manual'
            confidence DOUBLE
        )
    """)
    
    # Insert exact matches first
    conn.execute("""
        INSERT INTO vaccine_name_mappings
        WITH vaers_vax AS (
            SELECT DISTINCT vax_name
            FROM vaers_subset
            WHERE vax_name IS NOT NULL
        ),
        fda_vax AS (
            SELECT DISTINCT vax_name
            FROM fda_reports
            WHERE vax_name IS NOT NULL
        )
        SELECT 
            v.vax_name as vaers_name,
            f.vax_name as fda_name,
            'exact' as mapping_type,
            1.0 as confidence
        FROM vaers_vax v
        INNER JOIN fda_vax f ON UPPER(TRIM(v.vax_name)) = UPPER(TRIM(f.vax_name))
    """)
    
    exact_count = conn.execute("SELECT COUNT(*) FROM vaccine_name_mappings WHERE mapping_type = 'exact'").fetchone()[0]
    print(f"Added {exact_count} exact matches")
    
    # Add common patterns (COVID vaccines) - expanded list
    covid_mappings = [
        # Moderna COVID vaccines
        ('COVID19 (COVID19 (MODERNA))', 'COVID-19 VACCINE (MRNA)', 'manual', 0.95),
        ('COVID19 (COVID19 (MODERNA))', 'SPIKEVAX (COVID-19 VACCINE MRNA)', 'manual', 0.9),
        
        # Pfizer COVID vaccines
        ('COVID19 (COVID19 (PFIZER-BIONTECH))', 'COVID-19 VACCINE (MRNA)', 'manual', 0.95),
        ('COVID19 (COVID19 (PFIZER-BIONTECH))', 'COMIRNATY (COVID-19 VACCINE MRNA)', 'manual', 0.9),
        
        # Janssen/J&J COVID vaccines
        ('COVID19 (COVID19 (JANSSEN))', 'COVID-19 VACCINE (AD26.COV2.S)', 'manual', 0.95),
        ('COVID19 (COVID19 (JANSSEN))', 'JANSSEN COVID-19 VACCINE', 'manual', 0.9),
        
        # Unknown COVID vaccines
        ('COVID19 (COVID19 (UNKNOWN))', 'COVID-19 VACCINE (MRNA)', 'manual', 0.7),
        ('COVID19 (COVID19 (UNKNOWN))', 'COVID-19 VACCINE (AD26.COV2.S)', 'manual', 0.6),
        
        # Generic COVID mappings
        ('COVID19', 'COVID-19 VACCINE (MRNA)', 'manual', 0.8),
        ('COVID19', 'COVID-19 VACCINE (AD26.COV2.S)', 'manual', 0.7),
    ]
    
    # Clear any existing manual mappings first
    conn.execute("DELETE FROM vaccine_name_mappings WHERE mapping_type = 'manual'")
    
    for vaers, fda, mtype, conf in covid_mappings:
        # Check if this FDA vaccine exists
        exists = conn.execute("SELECT COUNT(*) FROM fda_reports WHERE vax_name = ?", [fda]).fetchone()[0]
        if exists > 0:
            conn.execute("""
                INSERT INTO vaccine_name_mappings 
                VALUES (?, ?, ?, ?)
            """, [vaers, fda, mtype, conf])
    
    manual_count = conn.execute("SELECT COUNT(*) FROM vaccine_name_mappings WHERE mapping_type = 'manual'").fetchone()[0]
    print(f"Added {manual_count} manual COVID vaccine mappings")
    
    # Check mapping coverage
    coverage = conn.execute("""
        WITH mapped_vaers AS (
            SELECT COUNT(DISTINCT v.vax_name) as mapped_count
            FROM vaers_subset v
            WHERE EXISTS (
                SELECT 1 FROM vaccine_name_mappings m 
                WHERE m.vaers_name = v.vax_name
            )
        ),
        total_vaers AS (
            SELECT COUNT(DISTINCT vax_name) as total_count
            FROM vaers_subset
            WHERE vax_name IS NOT NULL
        )
        SELECT 
            m.mapped_count,
            t.total_count,
            ROUND(100.0 * m.mapped_count / t.total_count, 2) as coverage_pct
        FROM mapped_vaers m, total_vaers t
    """).fetchone()
    
    print(f"\nMapping coverage: {coverage[0]}/{coverage[1]} ({coverage[2]}%)")
    
    return coverage

def test_mapping_with_new_table(conn: duckdb.DuckDBPyConnection):
    """Test if using the mapping table improves our results."""
    
    print("\n=== Testing with Vaccine Name Mappings ===")
    
    # Create the original mapping view first
    conn.execute("""
        CREATE OR REPLACE VIEW vaers_fda_mapping AS
        SELECT DISTINCT
            v.VAERS_ID,
            v.vax_name as vaers_vaccine,
            v.symptom as vaers_symptom,
            sm.fda_adverse_event,
            f.vax_name as fda_vaccine,
            f.adverse_event as fda_documented_event
        FROM vaers_subset v
        LEFT JOIN symptom_mappings sm ON v.symptom = sm.vaers_symptom
        LEFT JOIN fda_reports f ON 
            UPPER(TRIM(v.vax_name)) = UPPER(TRIM(f.vax_name)) 
            AND sm.fda_adverse_event = f.adverse_event
    """)
    
    # Get original stats
    original_stats = conn.execute("""
        WITH report_stats AS (
            SELECT 
                VAERS_ID,
                COUNT(DISTINCT vaers_symptom) as total_symptoms,
                COUNT(DISTINCT CASE WHEN fda_documented_event IS NOT NULL THEN vaers_symptom END) as mapped_symptoms
            FROM vaers_fda_mapping
            GROUP BY VAERS_ID
        )
        SELECT 
            COUNT(*) as total_reports,
            COUNT(CASE WHEN mapped_symptoms > 0 THEN 1 END) as reports_with_mappings,
            COUNT(CASE WHEN mapped_symptoms = total_symptoms AND total_symptoms > 0 THEN 1 END) as fully_mapped_reports
        FROM report_stats
    """).fetchone()
    
    print(f"\nOriginal approach (without mapping table):")
    print(f"  Reports with at least one FDA mapping: {original_stats[1]:,} / {original_stats[0]:,}")
    print(f"  Fully mapped reports: {original_stats[2]:,}")
    
    # Create an improved mapping view
    conn.execute("""
        CREATE OR REPLACE VIEW vaers_fda_mapping_improved AS
        SELECT DISTINCT
            v.VAERS_ID,
            v.vax_name as vaers_vaccine_original,
            COALESCE(vm.fda_name, v.vax_name) as vaers_vaccine_mapped,
            v.symptom as vaers_symptom,
            sm.fda_adverse_event,
            f.vax_name as fda_vaccine,
            f.adverse_event as fda_documented_event
        FROM vaers_subset v
        LEFT JOIN vaccine_name_mappings vm ON v.vax_name = vm.vaers_name
        LEFT JOIN symptom_mappings sm ON v.symptom = sm.vaers_symptom
        LEFT JOIN fda_reports f ON 
            UPPER(TRIM(COALESCE(vm.fda_name, v.vax_name))) = UPPER(TRIM(f.vax_name)) 
            AND sm.fda_adverse_event = f.adverse_event
    """)
    
    # Check how many reports now have at least one FDA match
    improved_stats = conn.execute("""
        WITH report_stats AS (
            SELECT 
                VAERS_ID,
                vaers_vaccine_original,
                COUNT(DISTINCT vaers_symptom) as total_symptoms,
                COUNT(DISTINCT CASE WHEN fda_documented_event IS NOT NULL THEN vaers_symptom END) as mapped_symptoms
            FROM vaers_fda_mapping_improved
            GROUP BY VAERS_ID, vaers_vaccine_original
        )
        SELECT 
            COUNT(*) as total_reports,
            COUNT(CASE WHEN mapped_symptoms > 0 THEN 1 END) as reports_with_mappings,
            COUNT(CASE WHEN mapped_symptoms = total_symptoms AND total_symptoms > 0 THEN 1 END) as fully_mapped_reports,
            ROUND(100.0 * COUNT(CASE WHEN mapped_symptoms > 0 THEN 1 END) / COUNT(*), 2) as pct_with_mappings
        FROM report_stats
    """).fetchone()
    
    print(f"\nImproved approach (with mapping table):")
    print(f"  Reports with at least one FDA mapping: {improved_stats[1]:,} / {improved_stats[0]:,} ({improved_stats[3]}%)")
    print(f"  Fully mapped reports: {improved_stats[2]:,}")
    print(f"  Improvement: +{improved_stats[1] - original_stats[1]:,} reports with mappings")
    
    # Show some examples of improved mappings
    print("\n=== Sample Improved Mappings ===")
    samples = conn.execute("""
        SELECT DISTINCT
            vaers_vaccine_original,
            vaers_vaccine_mapped,
            fda_vaccine,
            COUNT(DISTINCT VAERS_ID) as report_count
        FROM vaers_fda_mapping_improved
        WHERE fda_documented_event IS NOT NULL
            AND vaers_vaccine_original != vaers_vaccine_mapped
        GROUP BY vaers_vaccine_original, vaers_vaccine_mapped, fda_vaccine
        ORDER BY report_count DESC
        LIMIT 10
    """).fetchdf()
    
    if not samples.empty:
        print(samples.to_string(index=False))

def show_fully_mapped_examples(conn: duckdb.DuckDBPyConnection):
    """Show examples of fully mapped reports."""
    print("\n=== Examples of Fully Mapped Reports ===")
    
    # Find reports where ALL symptoms are fully mapped
    fully_mapped = conn.execute("""
        WITH report_symptom_counts AS (
            SELECT 
                VAERS_ID,
                vaers_vaccine_original,
                COUNT(DISTINCT vaers_symptom) as total_symptoms
            FROM vaers_fda_mapping_improved
            GROUP BY VAERS_ID, vaers_vaccine_original
        ),
        mapped_symptom_counts AS (
            SELECT 
                VAERS_ID,
                vaers_vaccine_original,
                COUNT(DISTINCT vaers_symptom) as mapped_symptoms
            FROM vaers_fda_mapping_improved
            WHERE fda_documented_event IS NOT NULL
            GROUP BY VAERS_ID, vaers_vaccine_original
        )
        SELECT 
            r.VAERS_ID,
            r.vaers_vaccine_original as vaccine,
            r.total_symptoms,
            COALESCE(m.mapped_symptoms, 0) as mapped_symptoms
        FROM report_symptom_counts r
        LEFT JOIN mapped_symptom_counts m ON 
            r.VAERS_ID = m.VAERS_ID AND 
            r.vaers_vaccine_original = m.vaers_vaccine_original
        WHERE r.total_symptoms = COALESCE(m.mapped_symptoms, 0) AND r.total_symptoms > 0
        ORDER BY r.total_symptoms DESC
        LIMIT 10
    """).fetchdf()
    
    if not fully_mapped.empty:
        print(f"Found {len(fully_mapped)} fully mapped reports. Here are some examples:")
        print(fully_mapped.to_string(index=False))
        
        # Show details for one example
        if len(fully_mapped) > 0:
            example_id = fully_mapped.iloc[0]['VAERS_ID']
            example_vaccine = fully_mapped.iloc[0]['vaccine']
            
            print(f"\nDetailed mapping for VAERS ID {example_id}:")
            details = conn.execute("""
                SELECT 
                    vaers_symptom,
                    fda_adverse_event,
                    fda_documented_event
                FROM vaers_fda_mapping_improved
                WHERE VAERS_ID = ? AND vaers_vaccine_original = ?
                ORDER BY vaers_symptom
            """, [example_id, example_vaccine]).fetchdf()
            
            print(details.to_string(index=False))
    else:
        print("No fully mapped reports found yet.")

def main():
    # Initialize database
    conn = setup_database()
    
    # Load data if needed
    if not load_all_data(conn):
        print("\nERROR: Failed to load data files. Please ensure JSON files are in ../json_data/")
        return
    
    # Analyze vaccine name matching
    exact_matches, no_match_vaers, fda_vaccines = analyze_vaccine_name_matching(conn)
    
    # Create mapping table
    coverage = create_vaccine_mapping_table(conn)
    
    # Test with improved mappings
    test_mapping_with_new_table(conn)
    
    # Show examples of fully mapped reports
    show_fully_mapped_examples(conn)
    
    # Show unmatched high-volume VAERS vaccines that might need manual mapping
    print("\n=== High-Volume VAERS Vaccines Still Unmatched ===")
    still_unmatched = conn.execute("""
        WITH mapped AS (
            SELECT DISTINCT vaers_name FROM vaccine_name_mappings
        )
        SELECT 
            v.vax_name,
            COUNT(DISTINCT v.VAERS_ID) as report_count
        FROM vaers_subset v
        WHERE v.vax_name NOT IN (SELECT vaers_name FROM mapped)
            AND v.vax_name IS NOT NULL
        GROUP BY v.vax_name
        HAVING COUNT(DISTINCT v.VAERS_ID) > 100
        ORDER BY report_count DESC
        LIMIT 20
    """).fetchdf()
    
    if not still_unmatched.empty:
        print("These vaccines have many VAERS reports but no FDA mapping:")
        print(still_unmatched.to_string(index=False))
    
    print("\n=== Next Steps ===")
    print("1. Review the high-volume unmatched vaccines above")
    print("2. Check FDA vaccines list to find corresponding names")
    print("3. Add more manual mappings to improve coverage")
    print("4. Consider fuzzy matching for vaccines with similar names")
    
    conn.close()

if __name__ == "__main__":
    main()