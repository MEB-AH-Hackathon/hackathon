#!/usr/bin/env python3
"""
Find top unmapped VAERS symptoms that could potentially match FDA adverse events.
Creates examples for manual mapping review.
"""

import duckdb
import json

def find_unmapped_symptom_examples():
    # Connect to the database
    conn = duckdb.connect('duckdb/vaers_analysis.db')
    
    print("Finding top unmapped symptoms for manual mapping review...")
    
    # Get top unmapped symptoms (excluding administrative ones)
    symptom_results = conn.execute("""
        SELECT 
            v.symptom,
            COUNT(*) as frequency,
            v.vax_name as vaccine
        FROM vaers_subset v
        WHERE NOT EXISTS (
            SELECT 1 FROM symptom_mappings sm 
            WHERE sm.vaers_symptom = v.symptom
        )
        AND v.symptom NOT IN (
            'Product storage error', 'Expired product administered', 'No adverse event',
            'Product preparation issue', 'Product preparation error', 'Vaccination failure',
            'Product quality issue', 'Product contamination suspected', 'Fatigue'
        )
        GROUP BY v.symptom, v.vax_name
        HAVING COUNT(*) >= 5
        ORDER BY frequency DESC
        LIMIT 15
    """).fetchall()
    
    examples = []
    
    for symptom, frequency, vaccine in symptom_results:
        # Get a sample VAERS ID for this symptom
        vaers_id_result = conn.execute("""
            SELECT VAERS_ID FROM vaers_subset 
            WHERE symptom = ? AND vax_name = ?
            LIMIT 1
        """, [symptom, vaccine]).fetchone()
        
        vaers_id = vaers_id_result[0] if vaers_id_result else None
        
        # Get FDA adverse events for this vaccine
        fda_events_result = conn.execute("""
            SELECT DISTINCT adverse_event 
            FROM fda_reports 
            WHERE vaccine_name = ?
            ORDER BY adverse_event
        """, [vaccine]).fetchall()
        
        fda_adverse_events = [event[0] for event in fda_events_result]
        
        # Check if this symptom is an exact match (case-insensitive)
        symptom_lower = symptom.lower()
        fda_events_lower = [ae.lower() for ae in fda_adverse_events]
        
        if symptom_lower in fda_events_lower:
            continue  # Skip exact matches
        
        example = {
            "VAERS_ID": vaers_id,
            "vaccine": vaccine,
            "unmapped_symptom": symptom,
            "symptom_frequency": frequency,
            "fda_adverse_events_for_vaccine": fda_adverse_events,
            "needs_manual_review": True,
            "potential_matches": [],  # To be filled manually
            "notes": f"Symptom appears {frequency} times and may match one of the FDA adverse events"
        }
        
        examples.append(example)
        
        # Stop at 10 examples for manual review
        if len(examples) >= 10:
            break
    
    # Create output structure
    output = {
        "metadata": {
            "description": "Top unmapped VAERS symptoms that need manual mapping review",
            "purpose": "Find symptoms that could match FDA adverse events but haven't been mapped yet",
            "criteria": "Symptoms appearing ≥5 times, not exact matches to FDA adverse events, excluding administrative symptoms",
            "generated_date": "2025-06-03"
        },
        "examples": examples
    }
    
    # Save to JSON
    with open('json_data/unmapped_symptom_examples.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nFound {len(examples)} unmapped symptoms for manual review")
    print("Top unmapped symptoms:")
    for i, example in enumerate(examples, 1):
        print(f"{i:2d}. {example['unmapped_symptom']} (appears {example['symptom_frequency']} times)")
        print(f"     Vaccine: {example['vaccine']}")
        print(f"     FDA adverse events available: {len(example['fda_adverse_events_for_vaccine'])}")
        print(f"     VAERS_ID example: {example['VAERS_ID']}")
        print()
    
    print("Saved to json_data/unmapped_symptom_examples.json")
    print("\nNext step: Manually review these and add potential_matches for each symptom")
    
    conn.close()

if __name__ == "__main__":
    find_unmapped_symptom_examples()