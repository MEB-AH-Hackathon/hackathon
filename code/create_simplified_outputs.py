#!/usr/bin/env python3
"""
Create simplified JSON outputs:
1. fda_reports.json - merge PDF extraction + vaccine names
2. vaers_subset.json - VAERS data for 14 crosswalked vaccines
3. symptom_mappings.json - general symptom deduplication
"""

import json
import pandas as pd
import duckdb
from pathlib import Path

def load_vaccine_mappings():
    """Load the 14 vaccine crosswalk mappings"""
    try:
        from vaccine_mappings import VACCINE_MAPPINGS
        return VACCINE_MAPPINGS
    except ImportError:
        print("Error: Could not import vaccine_mappings.py")
        return []

def create_fda_reports():
    """Merge PDF extraction results and vaccine names into one file"""
    print("Creating fda_reports.json...")
    
    # Load both FDA files
    with open('../json_data/pdf_extraction_results.json', 'r') as f:
        extraction_results = json.load(f)
    
    with open('../json_data/pdf_vaccine_names_only.json', 'r') as f:
        vaccine_names = json.load(f)
    
    # Create mapping of filename to vaccine info
    filename_to_vaccine = {item['filename']: item for item in vaccine_names}
    
    # Merge the data
    fda_reports = []
    for result in extraction_results.get('successful', []):
        filename = result['filename']
        vaccine_info = filename_to_vaccine.get(filename, {})
        
        merged_entry = {
            'filename': filename,
            'vax_type': vaccine_info.get('vax_type', 'UNKNOWN'),
            'vax_name': vaccine_info.get('vax_name', 'UNKNOWN'),
            'vax_manu': vaccine_info.get('vax_manu', 'UNKNOWN'),
            'extraction_success': result['success'],
            'adverse_events': result['data']['symptoms_list'],
            'study_type': result['data']['study_type'],
            'source_section': result['data']['source_section'],
            'controlled_trial_text': result['data']['controlled_trial_text']
        }
        fda_reports.append(merged_entry)
    
    # Save merged file
    with open('../json_data/fda_reports.json', 'w') as f:
        json.dump(fda_reports, f, indent=2)
    
    print(f"Created fda_reports.json with {len(fda_reports)} FDA reports")

def create_vaers_subset():
    """Create VAERS subset for the 14 crosswalked vaccines"""
    print("Creating vaers_subset.json...")
    
    mappings = load_vaccine_mappings()
    if not mappings:
        print("No vaccine mappings found!")
        return
    
    # Get list of VAERS vaccine names
    vaers_vaccines = [m['vaers_vaccine'] for m in mappings]
    print(f"Looking for these VAERS vaccines: {vaers_vaccines}")
    
    # Connect to unified database
    try:
        conn = duckdb.connect('../duckdb_data/unified_vaers_analysis.duckdb')
        
        # Build SQL query for the 14 vaccines
        vaccine_filter = "'" + "', '".join(vaers_vaccines) + "'"
        
        query = f"""
        SELECT v.vaers_id, v.age_yrs, v.sex, v.state, v.died, v.hospital, v.er_visit,
               v.vax_date, v.onset_date, v.year, v.symptoms,
               vac.vaers_name as vaccine_name, vac.pdf_name as pdf_vaccine_name
        FROM vaers_reports v
        JOIN vaccines vac ON v.vaccine_id = vac.vaccine_id
        WHERE vac.vaers_name IN ({vaccine_filter})
        LIMIT 50000
        """
        
        result = conn.execute(query).fetchdf()
        print(f"Found {len(result)} VAERS reports for crosswalked vaccines")
        
        # Convert to JSON format
        vaers_data = []
        for _, row in result.iterrows():
            try:
                symptoms = json.loads(row['symptoms']) if row['symptoms'] else []
            except:
                symptoms = []
            
            record = {
                'vaers_id': int(row['vaers_id']),
                'age_yrs': float(row['age_yrs']) if pd.notna(row['age_yrs']) else None,
                'sex': row['sex'],
                'state': row['state'],
                'died': row['died'],
                'hospital': row['hospital'],
                'er_visit': row['er_visit'],
                'vax_date': row['vax_date'],
                'onset_date': row['onset_date'],
                'year': int(row['year']),
                'vaccine_name': row['vaccine_name'],
                'pdf_vaccine_name': row['pdf_vaccine_name'],
                'symptoms': symptoms,
                'total_symptoms_count': len(symptoms)
            }
            vaers_data.append(record)
        
        # Save VAERS subset
        with open('../json_data/vaers_subset.json', 'w') as f:
            json.dump(vaers_data, f, indent=2)
        
        print(f"Created vaers_subset.json with {len(vaers_data)} reports")
        return vaers_data
        
    except Exception as e:
        print(f"Error accessing database: {e}")
        return []

def create_symptom_mappings(vaers_data):
    """Create general symptom deduplication/mapping table"""
    print("Creating symptom_mappings.json...")
    
    if not vaers_data:
        print("No VAERS data available for symptom mapping")
        return
    
    # Collect all symptoms
    all_symptoms = set()
    symptom_counts = {}
    
    for record in vaers_data:
        for symptom in record.get('symptoms', []):
            all_symptoms.add(symptom)
            symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
    
    print(f"Found {len(all_symptoms)} unique symptoms")
    
    # Create basic mappings (this is simplified - could use LLM for better mapping)
    symptom_mappings = []
    
    for symptom in sorted(all_symptoms):
        mapping = {
            'original_symptom': symptom,
            'canonical_symptom': symptom.lower().strip(),
            'frequency': symptom_counts[symptom],
            'mapping_type': 'exact'  # Could be 'synonym', 'related', etc.
        }
        symptom_mappings.append(mapping)
    
    # Save symptom mappings
    with open('../json_data/symptom_mappings.json', 'w') as f:
        json.dump(symptom_mappings, f, indent=2)
    
    print(f"Created symptom_mappings.json with {len(symptom_mappings)} symptom mappings")

def main():
    """Create all simplified outputs"""
    print("Creating simplified JSON outputs...")
    
    # Create output directory if needed
    Path('../json_data').mkdir(exist_ok=True)
    
    # Create the three main files
    create_fda_reports()
    vaers_data = create_vaers_subset()
    create_symptom_mappings(vaers_data)
    
    print("\nCompleted creating simplified outputs!")
    print("Files created:")
    print("- fda_reports.json")
    print("- vaers_subset.json") 
    print("- symptom_mappings.json")

if __name__ == "__main__":
    main()