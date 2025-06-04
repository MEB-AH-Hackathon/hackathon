#!/usr/bin/env python3
"""
Add SYMPTOM_TEXT field to unmapped_symptom_examples.json
"""

import json

def add_symptom_text():
    # Read the existing unmapped examples file
    with open('json_data/unmapped_symptom_examples.json', 'r') as f:
        data = json.load(f)
    
    # Read the VAERS subset to get SYMPTOM_TEXT
    print("Loading VAERS subset data...")
    with open('json_data/vaers_subset.json', 'r') as f:
        vaers_data = json.load(f)
    
    # Create a lookup dictionary by VAERS_ID
    print("Creating VAERS_ID lookup...")
    vaers_lookup = {}
    for record in vaers_data:
        vaers_id = str(record.get('VAERS_ID', ''))
        if vaers_id and 'SYMPTOM_TEXT' in record:
            vaers_lookup[vaers_id] = record['SYMPTOM_TEXT']
    
    print("Adding SYMPTOM_TEXT for each VAERS_ID...")
    
    # For each example, get the SYMPTOM_TEXT
    for example in data['examples']:
        vaers_id = str(example['VAERS_ID'])
        
        symptom_text = vaers_lookup.get(vaers_id, "No symptom text available")
        example['symptom_text'] = symptom_text
        
        # Show preview
        preview = symptom_text[:100] if symptom_text else "No text"
        print(f"VAERS_ID {vaers_id}: {preview}...")
    
    # Save updated file
    with open('json_data/unmapped_symptom_examples.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("\nUpdated unmapped_symptom_examples.json with symptom_text field")

if __name__ == "__main__":
    add_symptom_text()