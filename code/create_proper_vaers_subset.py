#!/usr/bin/env python3
"""
Create proper VAERS subset matching the format of vaers_2024_sample100.json
Only includes reports for vaccines found in FDA reports
"""

import json
import pandas as pd
from pathlib import Path
import os

def load_fda_vaccine_names():
    """Load the VAERS vaccine names from FDA reports"""
    with open('json_data/fda_reports.json', 'r') as f:
        fda_reports = json.load(f)
    
    # Collect all VAERS vaccine names from FDA reports
    vaers_names = set()
    for report in fda_reports:
        if report.get('vaers_vaccine_names'):
            vaers_names.update(report['vaers_vaccine_names'])
    
    return list(vaers_names)

def create_proper_vaers_subset():
    """Create VAERS subset with proper format matching sample structure"""
    print("Creating proper VAERS subset (100K records) for vaccines in FDA reports...")
    
    # Load FDA vaccine names
    fda_vaccine_names = load_fda_vaccine_names()
    print(f"Found {len(fda_vaccine_names)} vaccine names from FDA reports:")
    for name in sorted(fda_vaccine_names):
        print(f"  - {name}")
    
    # Define years to process
    years = ['2023', '2024']
    
    all_records = []
    
    for year in years:
        print(f"\nProcessing {year} VAERS data...")
        
        # File paths
        data_file = f'vaers_data/vaers_data/{year}VAERSDATA.csv'
        symptoms_file = f'vaers_data/vaers_data/{year}VAERSSYMPTOMS.csv'
        vax_file = f'vaers_data/vaers_data/{year}VAERSVAX.csv'
        
        # Check if files exist
        if not all(os.path.exists(f) for f in [data_file, symptoms_file, vax_file]):
            print(f"  Skipping {year} - files not found")
            continue
        
        # Load data files with error handling
        print(f"  Loading {year}VAERSDATA.csv...")
        data_df = pd.read_csv(data_file, encoding='latin-1', low_memory=False, on_bad_lines='skip')
        
        print(f"  Loading {year}VAERSSYMPTOMS.csv...")
        symptoms_df = pd.read_csv(symptoms_file, encoding='latin-1', low_memory=False, on_bad_lines='skip')
        
        print(f"  Loading {year}VAERSVAX.csv...")
        vax_df = pd.read_csv(vax_file, encoding='latin-1', low_memory=False, on_bad_lines='skip')
        
        # Filter vaccines for our FDA list
        vax_filtered = vax_df[vax_df['VAX_NAME'].isin(fda_vaccine_names)]
        print(f"  Found {len(vax_filtered)} vaccine records matching FDA vaccines")
        
        # Get unique VAERS_IDs for reports that ONLY contain FDA vaccines
        # First, find reports with non-FDA vaccines
        non_fda_vax = vax_df[~vax_df['VAX_NAME'].isin(fda_vaccine_names)]
        reports_with_non_fda = set(non_fda_vax['VAERS_ID'].unique())
        
        # Get reports that only have FDA vaccines
        all_reports_with_fda = set(vax_filtered['VAERS_ID'].unique())
        vaers_ids = list(all_reports_with_fda - reports_with_non_fda)
        print(f"  Found {len(vaers_ids)} unique VAERS reports with ONLY FDA vaccines")
        
        # Filter other dataframes
        data_filtered = data_df[data_df['VAERS_ID'].isin(vaers_ids)]
        symptoms_filtered = symptoms_df[symptoms_df['VAERS_ID'].isin(vaers_ids)]
        vax_filtered = vax_df[vax_df['VAERS_ID'].isin(vaers_ids)]  # Get all vaccines for these reports
        
        # Group symptoms by VAERS_ID
        symptoms_grouped = symptoms_filtered.groupby('VAERS_ID').agg({
            'SYMPTOM1': lambda x: list(x.dropna()),
            'SYMPTOM2': lambda x: list(x.dropna()),
            'SYMPTOM3': lambda x: list(x.dropna()),
            'SYMPTOM4': lambda x: list(x.dropna()),
            'SYMPTOM5': lambda x: list(x.dropna())
        }).reset_index()
        
        # Combine symptom columns into a single list
        symptoms_grouped['symptom_list'] = symptoms_grouped.apply(
            lambda row: list(set(row['SYMPTOM1'] + row['SYMPTOM2'] + row['SYMPTOM3'] + 
                                row['SYMPTOM4'] + row['SYMPTOM5'])), axis=1
        )
        
        # Group vaccines by VAERS_ID
        vax_grouped = vax_filtered.groupby('VAERS_ID').agg({
            'VAX_TYPE': lambda x: list(x.dropna()),
            'VAX_MANU': lambda x: list(x.dropna()),
            'VAX_NAME': lambda x: list(x.dropna()),
            'VAX_DOSE_SERIES': lambda x: [str(v) for v in x.dropna()],
            'VAX_ROUTE': lambda x: list(x.dropna()),
            'VAX_SITE': lambda x: list(x.dropna())
        }).reset_index()
        
        # Merge all data
        merged = data_filtered.merge(symptoms_grouped[['VAERS_ID', 'symptom_list']], 
                                    on='VAERS_ID', how='left')
        merged = merged.merge(vax_grouped, on='VAERS_ID', how='left')
        
        # Define value mappers
        sex_map = {'M': 'male', 'F': 'female', 'U': 'unknown'}
        
        # Convert to proper format
        for _, row in merged.iterrows():
            # Helper function to convert Y/null to boolean
            def map_yes_null_to_bool(value):
                if pd.isna(value) or value is None:
                    return False
                return value == 'Y'
            
            # Helper function for Y/N/U fields (keep as strings)
            def map_yes_no_unknown(value):
                if pd.isna(value) or value is None:
                    return None
                if value == 'Y':
                    return 'yes'
                elif value == 'N':
                    return 'no'
                elif value == 'U':
                    return 'unknown'
                else:
                    return None
            
            record = {
                "VAERS_ID": int(row['VAERS_ID']) if pd.notna(row['VAERS_ID']) else None,
                "RECVDATE": row['RECVDATE'] if pd.notna(row['RECVDATE']) else None,
                "STATE": row['STATE'] if pd.notna(row['STATE']) else None,
                "AGE_YRS": float(row['AGE_YRS']) if pd.notna(row['AGE_YRS']) else None,
                "SEX": sex_map.get(row['SEX'], None) if pd.notna(row['SEX']) else None,
                "SYMPTOM_TEXT": row['SYMPTOM_TEXT'] if pd.notna(row['SYMPTOM_TEXT']) else None,
                "DIED": map_yes_null_to_bool(row['DIED']),  # Boolean
                "L_THREAT": map_yes_null_to_bool(row['L_THREAT']),  # Boolean
                "ER_VISIT": map_yes_null_to_bool(row['ER_VISIT']),  # Boolean
                "HOSPITAL": map_yes_null_to_bool(row['HOSPITAL']),  # Boolean
                "DISABLE": map_yes_null_to_bool(row['DISABLE']),  # Boolean
                "RECOVD": map_yes_no_unknown(row['RECOVD']),  # String: yes/no/unknown
                "VAX_DATE": row['VAX_DATE'] if pd.notna(row['VAX_DATE']) else None,
                "ONSET_DATE": row['ONSET_DATE'] if pd.notna(row['ONSET_DATE']) else None,
                "NUMDAYS": float(row['NUMDAYS']) if pd.notna(row['NUMDAYS']) else None,
                "VAX_TYPE_list": row['VAX_TYPE'] if isinstance(row['VAX_TYPE'], list) else [],
                "VAX_MANU_list": row['VAX_MANU'] if isinstance(row['VAX_MANU'], list) else [],
                "VAX_NAME_list": row['VAX_NAME'] if isinstance(row['VAX_NAME'], list) else [],
                "VAX_DOSE_SERIES_list": row['VAX_DOSE_SERIES'] if isinstance(row['VAX_DOSE_SERIES'], list) else [],
                "VAX_ROUTE_list": row['VAX_ROUTE'] if isinstance(row['VAX_ROUTE'], list) else [],
                "VAX_SITE_list": row['VAX_SITE'] if isinstance(row['VAX_SITE'], list) else [],
                "symptom_list": row['symptom_list'] if isinstance(row['symptom_list'], list) else []
            }
            all_records.append(record)
    
    print(f"\nTotal records collected: {len(all_records)}")
    
    # Sample to 100K records if we have more
    if len(all_records) > 100000:
        import random
        random.seed(42)  # For reproducibility
        all_records = random.sample(all_records, 100000)
        print(f"Sampled down to 100,000 records")
    
    # Save the results
    Path('json_data').mkdir(parents=True, exist_ok=True)
    with open('json_data/vaers_subset.json', 'w') as f:
        json.dump(all_records, f, indent=2)
    
    print(f"\n✓ Created vaers_subset.json with {len(all_records)} reports")
    
    # Show summary of vaccines in the subset
    vaccine_counts = {}
    for record in all_records:
        for vax in record.get('VAX_NAME_list', []):
            vaccine_counts[vax] = vaccine_counts.get(vax, 0) + 1
    
    print("\nVaccine distribution in subset:")
    for vax, count in sorted(vaccine_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {vax}: {count:,} reports")

if __name__ == "__main__":
    create_proper_vaers_subset()