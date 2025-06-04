#!/usr/bin/env python3

import json
import re
from pathlib import Path

def extract_vaccine_name_from_filename(filename):
    """Extract vaccine name from PDF filename"""
    # Remove file extension
    name = filename.replace('.pdf', '').replace('Package-Insert-', '')
    
    # Common patterns in filenames
    # Some have (1), (2) etc. at the end
    name = re.sub(r'\s*\(\d+\)$', '', name)
    
    # Convert to uppercase to match VAERS format
    return name.upper()

def add_vaccine_names_to_json():
    """Add vax_name field to PDF extraction results based on filename"""
    
    json_path = Path("../json_data/pdf_extraction_results.json")
    
    # Read existing JSON
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Process successful extractions
    for item in data.get('successful', []):
        filename = item.get('filename', '')
        vax_name = extract_vaccine_name_from_filename(filename)
        
        # Add vax_name to the data object
        if 'data' in item:
            item['data']['vax_name'] = vax_name
        
        print(f"Filename: {filename} -> Vaccine: {vax_name}")
    
    # Process failed extractions too (if any)
    for item in data.get('failed', []):
        filename = item.get('filename', '')
        vax_name = extract_vaccine_name_from_filename(filename)
        item['vax_name'] = vax_name
    
    # Save updated JSON
    output_path = Path("../json_data/pdf_extraction_results_with_names.json")
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nUpdated JSON saved to: {output_path}")
    
    # Also create a simple list of all vaccine names
    vaccine_list = []
    for item in data.get('successful', []):
        if 'data' in item and 'vax_name' in item['data']:
            vaccine_list.append({
                'filename': item['filename'],
                'vax_name': item['data']['vax_name']
            })
    
    with open("../json_data/pdf_vaccine_list.json", 'w') as f:
        json.dump(vaccine_list, f, indent=2)
    
    print(f"Vaccine list saved to: ../json_data/pdf_vaccine_list.json")
    print(f"Total vaccines: {len(vaccine_list)}")

if __name__ == "__main__":
    add_vaccine_names_to_json()