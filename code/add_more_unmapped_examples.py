#!/usr/bin/env python3
"""
Add more unmapped symptom examples to the existing file
"""

import duckdb
import json

def add_more_examples():
    # Connect to the database
    conn = duckdb.connect('duckdb/vaers_analysis.db')
    
    # Read the existing file
    with open('json_data/unmapped_symptom_examples.json', 'r') as f:
        data = json.load(f)
    
    # Get existing symptoms to avoid duplicates
    existing_symptoms = set()
    for example in data['examples']:
        key = f"{example['unmapped_symptom']}_{example['vaccine']}"
        existing_symptoms.add(key)
    
    print(f"Found {len(existing_symptoms)} existing examples, getting more...")
    
    # Get more unmapped symptoms (excluding administrative ones and existing ones)
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
        LIMIT 50
    """).fetchall()
    
    # Read the VAERS subset to get SYMPTOM_TEXT
    print("Loading VAERS subset data...")
    with open('json_data/vaers_subset.json', 'r') as f:
        vaers_data = json.load(f)
    
    # Create a lookup dictionary by VAERS_ID
    vaers_lookup = {}
    for record in vaers_data:
        vaers_id = str(record.get('VAERS_ID', ''))
        if vaers_id and 'SYMPTOM_TEXT' in record:
            vaers_lookup[vaers_id] = record['SYMPTOM_TEXT']
    
    new_examples = []
    
    for symptom, frequency, vaccine in symptom_results:
        # Skip if we already have this symptom-vaccine combo
        key = f"{symptom}_{vaccine}"
        if key in existing_symptoms:
            continue
            
        # Get a sample VAERS ID for this symptom
        vaers_id_result = conn.execute("""
            SELECT VAERS_ID FROM vaers_subset 
            WHERE symptom = ? AND vax_name = ?
            LIMIT 1
        """, [symptom, vaccine]).fetchone()
        
        vaers_id = vaers_id_result[0] if vaers_id_result else None
        if not vaers_id:
            continue
        
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
        
        # Get symptom text
        symptom_text = vaers_lookup.get(str(vaers_id), "No symptom text available")
        
        example = {
            "VAERS_ID": str(vaers_id),
            "vaccine": vaccine,
            "unmapped_symptom": symptom,
            "symptom_frequency": frequency,
            "fda_adverse_events_for_vaccine": fda_adverse_events,
            "potential_matches": [],
            "should_find": None,  # To be filled manually
            "notes": f"Symptom appears {frequency} times and may match one of the FDA adverse events",
            "symptom_text": symptom_text
        }
        
        new_examples.append(example)
        print(f"Added: {symptom} (appears {frequency} times) - {vaccine}")
        
        # Stop when we have 12 new examples
        if len(new_examples) >= 12:
            break
    
    # Add new examples to existing data
    data['examples'].extend(new_examples)
    
    # Update metadata
    data['metadata']['description'] = f"Top unmapped VAERS symptoms that need manual mapping review - {len(data['examples'])} examples"
    
    # Save updated file
    with open('json_data/unmapped_symptom_examples.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nAdded {len(new_examples)} new examples")
    print(f"Total examples now: {len(data['examples'])}")
    print("Updated unmapped_symptom_examples.json")
    
    conn.close()

if __name__ == "__main__":
    add_more_examples()