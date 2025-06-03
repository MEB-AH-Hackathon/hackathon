#!/usr/bin/env python3
"""
Get random samples of VAERS data in three categories:
1. Fully matched - symptoms are documented in FDA adverse events for same vaccine
2. Mapped but not matched - symptoms were processed but don't match FDA events
3. Not mapped - symptoms haven't been processed yet
"""

import duckdb
import json
import random

def get_samples():
    # Connect to the database we already created
    conn = duckdb.connect('duckdb/vaers_analysis.db')
    
    print("=== VAERS Data Sample Analysis ===\n")
    
    # 1. FULLY MATCHED - symptoms that ARE in FDA adverse events for the same vaccine
    print("1. FULLY MATCHED (symptoms documented in FDA package insert):")
    print("-" * 60)
    
    fully_matched = conn.execute("""
        WITH matched_reports AS (
            SELECT DISTINCT
                v.VAERS_ID,
                v.vax_name as vaccine,
                v.symptom as vaers_symptom,
                sm.fda_adverse_event,
                f.adverse_event as fda_documented
            FROM vaers_subset v
            INNER JOIN symptom_mappings sm ON v.symptom = sm.vaers_symptom
            INNER JOIN fda_reports f ON 
                v.vax_name = f.vaccine_name 
                AND sm.fda_adverse_event = f.adverse_event
        )
        SELECT 
            VAERS_ID,
            vaccine,
            STRING_AGG(DISTINCT vaers_symptom, ', ') as symptoms,
            STRING_AGG(DISTINCT fda_adverse_event, ', ') as fda_matches
        FROM matched_reports
        GROUP BY VAERS_ID, vaccine
        ORDER BY RANDOM()
        LIMIT 5
    """).fetchall()
    
    for vaers_id, vaccine, symptoms, fda_matches in fully_matched:
        print(f"VAERS ID: {vaers_id}")
        print(f"Vaccine: {vaccine}")
        print(f"Symptoms: {symptoms}")
        print(f"FDA Matches: {fda_matches}")
        print()
    
    # 2. MAPPED BUT NOT MATCHED - symptoms mapped but not in FDA list for that vaccine
    print("\n2. MAPPED BUT NOT MATCHED (processed but not in FDA list):")
    print("-" * 60)
    
    mapped_not_matched = conn.execute("""
        WITH mapped_unmatched AS (
            SELECT DISTINCT
                v.VAERS_ID,
                v.vax_name as vaccine,
                v.symptom as vaers_symptom,
                sm.fda_adverse_event
            FROM vaers_subset v
            INNER JOIN symptom_mappings sm ON v.symptom = sm.vaers_symptom
            WHERE NOT EXISTS (
                SELECT 1 FROM fda_reports f 
                WHERE f.vaccine_name = v.vax_name 
                AND f.adverse_event = sm.fda_adverse_event
            )
        )
        SELECT 
            VAERS_ID,
            vaccine,
            STRING_AGG(DISTINCT vaers_symptom, ', ') as symptoms,
            STRING_AGG(DISTINCT fda_adverse_event, ', ') as mapped_to
        FROM mapped_unmatched
        GROUP BY VAERS_ID, vaccine
        HAVING COUNT(DISTINCT vaers_symptom) <= 5  -- Keep it readable
        ORDER BY RANDOM()
        LIMIT 5
    """).fetchall()
    
    for vaers_id, vaccine, symptoms, mapped_to in mapped_not_matched:
        print(f"VAERS ID: {vaers_id}")
        print(f"Vaccine: {vaccine}")
        print(f"Symptoms: {symptoms}")
        print(f"Mapped to FDA terms: {mapped_to}")
        print("Status: These FDA terms are NOT in the package insert for this vaccine")
        print()
    
    # 3. NOT MAPPED - symptoms we haven't processed yet
    print("\n3. NOT MAPPED (symptoms not processed yet):")
    print("-" * 60)
    
    not_mapped = conn.execute("""
        WITH unmapped AS (
            SELECT DISTINCT
                v.VAERS_ID,
                v.vax_name as vaccine,
                v.symptom as vaers_symptom
            FROM vaers_subset v
            WHERE NOT EXISTS (
                SELECT 1 FROM symptom_mappings sm 
                WHERE sm.vaers_symptom = v.symptom
            )
        )
        SELECT 
            VAERS_ID,
            vaccine,
            STRING_AGG(DISTINCT vaers_symptom, ', ') as symptoms
        FROM unmapped
        GROUP BY VAERS_ID, vaccine
        HAVING COUNT(DISTINCT vaers_symptom) BETWEEN 2 AND 5  -- Interesting but readable
        ORDER BY RANDOM()
        LIMIT 5
    """).fetchall()
    
    for vaers_id, vaccine, symptoms in not_mapped:
        print(f"VAERS ID: {vaers_id}")
        print(f"Vaccine: {vaccine}")
        print(f"Symptoms: {symptoms}")
        print("Status: No mapping exists for these symptoms yet")
        print()
    
    # Summary statistics
    print("\n=== SUMMARY STATISTICS ===")
    stats = conn.execute("""
        WITH categorized AS (
            SELECT 
                v.VAERS_ID,
                v.symptom,
                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM symptom_mappings sm 
                        INNER JOIN fda_reports f ON f.adverse_event = sm.fda_adverse_event
                        WHERE sm.vaers_symptom = v.symptom 
                        AND f.vaccine_name = v.vax_name
                    ) THEN 'Fully Matched'
                    WHEN EXISTS (
                        SELECT 1 FROM symptom_mappings sm 
                        WHERE sm.vaers_symptom = v.symptom
                    ) THEN 'Mapped Not Matched'
                    ELSE 'Not Mapped'
                END as category
            FROM vaers_subset v
        )
        SELECT 
            category,
            COUNT(DISTINCT VAERS_ID) as unique_reports,
            COUNT(*) as symptom_instances
        FROM categorized
        GROUP BY category
    """).fetchall()
    
    total_reports = sum(r[1] for r in stats)
    total_symptoms = sum(r[2] for r in stats)
    
    print(f"Total unique reports: {total_reports:,}")
    print(f"Total symptom instances: {total_symptoms:,}")
    print()
    
    for category, reports, symptoms in stats:
        print(f"{category}:")
        print(f"  Reports: {reports:,} ({100*reports/total_reports:.1f}%)")
        print(f"  Symptoms: {symptoms:,} ({100*symptoms/total_symptoms:.1f}%)")
    
    conn.close()

if __name__ == "__main__":
    # Redirect output to file
    import sys
    original_stdout = sys.stdout
    with open('intermediate_results/vaers_sample_analysis.txt', 'w') as f:
        sys.stdout = f
        get_samples()
    sys.stdout = original_stdout
    print("Sample analysis saved to intermediate_results/vaers_sample_analysis.txt")