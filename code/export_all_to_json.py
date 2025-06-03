#!/usr/bin/env python3

import duckdb
import json
from pathlib import Path

def export_all_to_json():
    """Export all DuckDB tables to JSON format for frontend"""
    
    print("=== EXPORTING ALL DATA TO JSON FORMAT ===")
    
    # Connect to main database
    unified_db = "../intermediate_results/unified_vaers_analysis.duckdb"
    conn = duckdb.connect(unified_db)
    
    output_dir = Path("../intermediate_results/json_export")
    output_dir.mkdir(exist_ok=True)
    
    # 1. Export vaccines table
    print("\n1. Exporting vaccines table...")
    vaccines = conn.execute("""
    SELECT * FROM vaccines
    ORDER BY vaccine_id
    """).fetchdf()
    
    # Convert JSON columns from string to actual JSON
    vaccines['pdf_adverse_events'] = vaccines['pdf_adverse_events'].apply(json.loads)
    
    vaccines.to_json(
        output_dir / "vaccines.json",
        orient='records',
        indent=2
    )
    print(f"  ✓ Exported {len(vaccines)} vaccines")
    
    # 2. Export symptom mappings
    print("\n2. Exporting symptom mappings...")
    symptom_mappings = conn.execute("""
    SELECT * FROM symptom_mappings
    ORDER BY vaers_count DESC
    """).fetchdf()
    
    symptom_mappings.to_json(
        output_dir / "symptom_mappings.json",
        orient='records',
        indent=2
    )
    print(f"  ✓ Exported {len(symptom_mappings)} symptom mappings")
    
    # 3. Export canonical symptoms
    print("\n3. Exporting canonical symptoms...")
    canonical = conn.execute("""
    SELECT * FROM canonical_symptoms
    ORDER BY total_vaers_reports DESC
    """).fetchdf()
    
    # Convert JSON columns
    canonical['example_vaccines'] = canonical['example_vaccines'].apply(json.loads)
    
    canonical.to_json(
        output_dir / "canonical_symptoms.json",
        orient='records',
        indent=2
    )
    print(f"  ✓ Exported {len(canonical)} canonical symptoms")
    
    # 4. Export symptom classifications
    print("\n4. Exporting symptom classifications...")
    classifications = conn.execute("""
    SELECT 
        sc.*,
        v.vaers_name as vaccine_name
    FROM symptom_classifications sc
    JOIN vaccines v ON sc.vaccine_id = v.vaccine_id
    ORDER BY vaccine_id, vaers_count DESC
    """).fetchdf()
    
    classifications.to_json(
        output_dir / "symptom_classifications.json",
        orient='records',
        indent=2
    )
    print(f"  ✓ Exported {len(classifications)} classifications")
    
    # 5. Export VAERS reports (sample for size)
    print("\n5. Exporting VAERS reports...")
    
    # Full export would be huge, so create different samples
    # a) Random sample across all vaccines
    print("  - Creating random sample (10K reports)...")
    random_sample = conn.execute("""
    SELECT 
        r.*,
        v.vaers_name as vaccine_name,
        v.pdf_name as pdf_vaccine_name
    FROM vaers_reports r
    JOIN vaccines v ON r.vaccine_id = v.vaccine_id
    ORDER BY RANDOM()
    LIMIT 10000
    """).fetchdf()
    
    # Convert JSON columns
    random_sample['symptoms'] = random_sample['symptoms'].apply(json.loads)
    
    random_sample.to_json(
        output_dir / "vaers_reports_sample_10k.json",
        orient='records',
        indent=2
    )
    
    # b) All reports for specific vaccines (smaller vaccines)
    print("  - Exporting all reports for smaller vaccines...")
    small_vaccine_reports = conn.execute("""
    SELECT 
        r.*,
        v.vaers_name as vaccine_name,
        v.pdf_name as pdf_vaccine_name
    FROM vaers_reports r
    JOIN vaccines v ON r.vaccine_id = v.vaccine_id
    WHERE v.vaccine_id >= 10  -- Non-COVID vaccines
    """).fetchdf()
    
    small_vaccine_reports['symptoms'] = small_vaccine_reports['symptoms'].apply(json.loads)
    
    small_vaccine_reports.to_json(
        output_dir / "vaers_reports_non_covid.json",
        orient='records',
        indent=2
    )
    print(f"  ✓ Exported {len(small_vaccine_reports)} non-COVID reports")
    
    # c) Summary statistics by vaccine
    print("\n6. Creating summary statistics...")
    summary_stats = conn.execute("""
    SELECT 
        v.vaccine_id,
        v.vaers_name,
        v.pdf_name,
        COUNT(r.vaers_id) as total_reports,
        COUNT(CASE WHEN r.died = 'Y' THEN 1 END) as deaths,
        COUNT(CASE WHEN r.hospital = 'Y' THEN 1 END) as hospitalizations,
        COUNT(CASE WHEN r.er_visit = 'Y' THEN 1 END) as er_visits,
        AVG(r.age_yrs) as avg_age,
        COUNT(CASE WHEN r.sex = 'F' THEN 1 END) as female_count,
        COUNT(CASE WHEN r.sex = 'M' THEN 1 END) as male_count
    FROM vaccines v
    LEFT JOIN vaers_reports r ON v.vaccine_id = r.vaccine_id
    GROUP BY v.vaccine_id, v.vaers_name, v.pdf_name
    ORDER BY total_reports DESC
    """).fetchdf()
    
    summary_stats.to_json(
        output_dir / "vaccine_summary_statistics.json",
        orient='records',
        indent=2
    )
    
    # 7. Create metadata file
    print("\n7. Creating metadata file...")
    metadata = {
        "description": "VAERS Adverse Event Analysis System - JSON Export",
        "export_date": "2025-06-03",
        "total_vaccines": len(vaccines),
        "total_reports_in_db": conn.execute("SELECT COUNT(*) FROM vaers_reports").fetchone()[0],
        "total_symptom_mappings": len(symptom_mappings),
        "total_canonical_symptoms": len(canonical),
        "files": {
            "vaccines.json": "All 16 crosswalked vaccines with PDF adverse events",
            "symptom_mappings.json": "VAERS symptoms mapped to PDF adverse events",
            "canonical_symptoms.json": "Normalized symptom names across vaccines",
            "symptom_classifications.json": "LLM-validated symptom classifications",
            "vaers_reports_sample_10k.json": "Random sample of 10,000 VAERS reports",
            "vaers_reports_non_covid.json": "All reports for non-COVID vaccines",
            "vaccine_summary_statistics.json": "Summary statistics by vaccine"
        }
    }
    
    with open(output_dir / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    conn.close()
    
    # Clean up old mixed-format files
    print("\n8. Cleaning up old files...")
    old_files = [
        "../intermediate_results/complete_vaers_analysis.parquet",
        "../intermediate_results/covid_demo_reports.json",
        "../intermediate_results/symptom_lookup.json",
        "../intermediate_results/vaers_analysis_sample.json"
    ]
    
    for old_file in old_files:
        if Path(old_file).exists():
            Path(old_file).rename(Path("../old_code") / Path(old_file).name)
            print(f"  ✓ Moved {Path(old_file).name} to old_code")
    
    print("\n=== EXPORT COMPLETE ===")
    print(f"\nAll JSON files exported to: {output_dir}")
    print("\nFiles created:")
    for file in sorted(output_dir.glob("*.json")):
        size_mb = file.stat().st_size / 1024 / 1024
        print(f"  - {file.name:<40} {size_mb:>6.1f} MB")

if __name__ == "__main__":
    export_all_to_json()