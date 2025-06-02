import duckdb
from pathlib import Path


def create_vaccine_mappings(db_path: str = "../intermediate_results/vaers_database.duckdb"):
    """Create comprehensive vaccine mappings between VAERS and PDF data"""
    
    conn = duckdb.connect(db_path)
    
    # Check if required tables exist
    tables = conn.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name IN ('all_vax', 'pdf_vaccine_extractions')
    """).fetchall()
    
    table_names = [t[0] for t in tables]
    
    if 'all_vax' not in table_names:
        print("✗ Error: all_vax table not found. Run vaers_parser.py first.")
        return
    
    if 'pdf_vaccine_extractions' not in table_names:
        print("✗ Error: pdf_vaccine_extractions table not found. Run pdf_vaccine_extractor.py first.")
        return
    
    print("✓ Found required tables. Creating vaccine mappings...")
    
    # Create comprehensive mapping view
    conn.execute("""
    CREATE OR REPLACE VIEW vaccine_pdf_mapping AS
    SELECT DISTINCT
        v.VAX_NAME as vaers_vax_name,
        v.VAX_TYPE as vaers_vax_type,
        p.vax_name as pdf_vax_name,
        p.vax_type as pdf_vax_type,
        p.filename as pdf_filename,
        p.vax_manu as pdf_manufacturer,
        CASE 
            WHEN UPPER(TRIM(v.VAX_NAME)) = UPPER(TRIM(p.vax_name)) THEN 'exact_name'
            WHEN UPPER(TRIM(v.VAX_TYPE)) = UPPER(TRIM(p.vax_type)) THEN 'type_match'
            WHEN UPPER(p.vax_name) LIKE '%' || UPPER(v.VAX_TYPE) || '%' THEN 'partial_match'
            ELSE 'no_match'
        END as match_type
    FROM all_vax v
    LEFT JOIN pdf_vaccine_extractions p 
        ON UPPER(TRIM(v.VAX_NAME)) = UPPER(TRIM(p.vax_name))
        OR UPPER(TRIM(v.VAX_TYPE)) = UPPER(TRIM(p.vax_type))
        OR UPPER(p.vax_name) LIKE '%' || UPPER(v.VAX_TYPE) || '%'
    WHERE v.VAX_NAME IS NOT NULL
        AND p.success = true
    ORDER BY v.VAX_NAME
    """)
    print("✓ Created vaccine_pdf_mapping view")
    
    # Create a summary table of mappings
    conn.execute("""
    CREATE OR REPLACE TABLE vaccine_mapping_summary AS
    SELECT 
        vaers_vax_type,
        vaers_vax_name,
        COUNT(DISTINCT pdf_filename) as pdf_count,
        STRING_AGG(DISTINCT pdf_filename, '; ') as pdf_files,
        STRING_AGG(DISTINCT pdf_vax_name, '; ') as pdf_vaccine_names,
        MIN(match_type) as best_match_type
    FROM vaccine_pdf_mapping
    WHERE pdf_filename IS NOT NULL
    GROUP BY vaers_vax_type, vaers_vax_name
    ORDER BY pdf_count DESC, vaers_vax_name
    """)
    print("✓ Created vaccine_mapping_summary table")
    
    # Get statistics
    stats = conn.execute("""
    SELECT 
        COUNT(DISTINCT vaers_vax_name) as total_vaers_vaccines,
        COUNT(DISTINCT CASE WHEN pdf_filename IS NOT NULL THEN vaers_vax_name END) as mapped_vaccines,
        COUNT(DISTINCT pdf_filename) as total_pdfs
    FROM vaccine_pdf_mapping
    """).fetchone()
    
    print(f"\nMapping Statistics:")
    print(f"  Total VAERS vaccines: {stats[0]}")
    print(f"  Vaccines with PDF mappings: {stats[1]}")
    print(f"  Coverage: {stats[1]/stats[0]*100:.1f}%")
    print(f"  Total PDFs mapped: {stats[2]}")
    
    # Show sample mappings
    print("\nSample vaccine mappings:")
    samples = conn.execute("""
    SELECT vaers_vax_name, pdf_vaccine_names, pdf_files
    FROM vaccine_mapping_summary
    WHERE pdf_count > 0
    LIMIT 10
    """).fetchall()
    
    for vaers_name, pdf_names, pdf_files in samples:
        print(f"\nVAERS: {vaers_name}")
        print(f"  PDF Names: {pdf_names}")
        print(f"  Files: {pdf_files}")
    
    # Create a view for vaccines without mappings
    conn.execute("""
    CREATE OR REPLACE VIEW unmapped_vaccines AS
    SELECT DISTINCT 
        VAX_TYPE, 
        VAX_NAME,
        COUNT(*) as vaers_record_count
    FROM all_vax
    WHERE VAX_NAME NOT IN (
        SELECT DISTINCT vaers_vax_name 
        FROM vaccine_pdf_mapping 
        WHERE pdf_filename IS NOT NULL
    )
    GROUP BY VAX_TYPE, VAX_NAME
    ORDER BY vaers_record_count DESC
    """)
    
    print("\nTop unmapped vaccines (no PDF found):")
    unmapped = conn.execute("""
    SELECT VAX_TYPE, VAX_NAME, vaers_record_count
    FROM unmapped_vaccines
    LIMIT 10
    """).fetchall()
    
    for vax_type, vax_name, count in unmapped:
        print(f"  {vax_type}: {vax_name} ({count} VAERS records)")
    
    conn.close()
    print("\n✓ Vaccine mapping complete!")


if __name__ == "__main__":
    create_vaccine_mappings()