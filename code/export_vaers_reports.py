#!/usr/bin/env python3

import duckdb
import json
from pathlib import Path

def export_vaers_reports():
    """Export individual VAERS reports to JSON"""
    
    print("=== EXPORTING VAERS REPORTS TO JSON ===")
    
    # Connect to unified database
    unified_db = "../duckdb_data/unified_vaers_analysis.duckdb"
    json_output_dir = Path("../json_data")
    json_output_dir.mkdir(exist_ok=True)
    
    conn = duckdb.connect(unified_db)
    
    # Get total count
    total_reports = conn.execute("SELECT COUNT(*) FROM vaers_reports").fetchone()[0]
    print(f"Total VAERS reports in database: {total_reports:,}")
    
    # Export samples of different sizes
    print("\nExporting report samples...")
    
    # 1. Small sample (1,000 reports) - like the sample file
    print("  - Creating 1K sample...")
    sample_1k = conn.execute("""
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
        json_array_length(r.symptoms) as total_symptoms_count
    FROM vaers_reports r
    JOIN vaccines v ON r.vaccine_id = v.vaccine_id
    ORDER BY RANDOM()
    LIMIT 1000
    """).fetchdf()
    
    # Convert JSON strings to actual lists
    sample_1k['symptoms'] = sample_1k['symptoms'].apply(json.loads)
    
    sample_1k.to_json(
        json_output_dir / "vaers_reports_sample_1k.json",
        orient='records',
        indent=2
    )
    
    # 2. Medium sample (10,000 reports)
    print("  - Creating 10K sample...")
    sample_10k = conn.execute("""
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
        json_array_length(r.symptoms) as total_symptoms_count
    FROM vaers_reports r
    JOIN vaccines v ON r.vaccine_id = v.vaccine_id
    ORDER BY RANDOM()
    LIMIT 10000
    """).fetchdf()
    
    sample_10k['symptoms'] = sample_10k['symptoms'].apply(json.loads)
    
    sample_10k.to_json(
        json_output_dir / "vaers_reports_sample_10k.json",
        orient='records',
        indent=2
    )
    
    # 3. Large sample (100,000 reports)
    print("  - Creating 100K sample...")
    sample_100k = conn.execute("""
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
        json_array_length(r.symptoms) as total_symptoms_count
    FROM vaers_reports r
    JOIN vaccines v ON r.vaccine_id = v.vaccine_id
    ORDER BY RANDOM()
    LIMIT 100000
    """).fetchdf()
    
    sample_100k['symptoms'] = sample_100k['symptoms'].apply(json.loads)
    
    sample_100k.to_json(
        json_output_dir / "vaers_reports_sample_100k.json",
        orient='records',
        indent=2
    )
    print(f"    Exported {len(sample_100k):,} reports")
    
    
    # 4. Create a summary of what's available
    summary = {
        "total_reports_in_database": total_reports,
        "exported_files": {
            "vaers_reports_sample_1k.json": {
                "description": "Random sample of 1,000 VAERS reports",
                "count": len(sample_1k)
            },
            "vaers_reports_sample_10k.json": {
                "description": "Random sample of 10,000 VAERS reports",
                "count": len(sample_10k)
            },
            "vaers_reports_sample_100k.json": {
                "description": "Random sample of 100,000 VAERS reports",
                "count": len(sample_100k)
            }
        },
        "note": "Each report includes vaccine names that can be linked to vaccines.json for PDF adverse events"
    }
    
    with open(json_output_dir / "vaers_reports_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    conn.close()
    
    print(f"\nExport complete! Files saved to: {json_output_dir}")
    print(f"\nFile sizes:")
    for file in ["vaers_reports_sample_1k.json", "vaers_reports_sample_10k.json", 
                 "vaers_reports_sample_100k.json"]:
        file_path = json_output_dir / file
        if file_path.exists():
            size_mb = file_path.stat().st_size / 1024 / 1024
            print(f"  {file:<35} {size_mb:>6.1f} MB")

if __name__ == "__main__":
    export_vaers_reports()