#!/usr/bin/env python3
"""
Create proper VAERS subset from raw CSV files
Each row = ONE VAERS report with basic fields + symptom list
"""

import json
import pandas as pd
import glob
from pathlib import Path

def create_proper_vaers_subset():
    """Create VAERS subset from raw CSV files"""
    print("Creating VAERS subset from raw CSV files...")
    
    try:
        # Load recent VAERS data (2023-2024)
        data_files = glob.glob("../vaers_data/vaers_data/202[34]VAERSDATA.csv")
        symptom_files = glob.glob("../vaers_data/vaers_data/202[34]VAERSSYMPTOMS.csv")
        vax_files = glob.glob("../vaers_data/vaers_data/202[34]VAERSVAX.csv")
        
        print(f"Found {len(data_files)} data files, {len(symptom_files)} symptom files, {len(vax_files)} vaccine files")
        
        # Load and combine data files
        all_data = []
        for file in data_files:
            print(f"Loading {file}...")
            try:
                df = pd.read_csv(file, encoding='latin-1', low_memory=False, on_bad_lines='skip')
                all_data.append(df)
                print(f"  Loaded {len(df)} records")
            except Exception as e:
                print(f"  Error loading {file}: {e}")
                continue
        
        if not all_data:
            raise Exception("No VAERS data files found")
            
        main_data = pd.concat(all_data, ignore_index=True)
        print(f"Loaded {len(main_data)} total reports")
        
        # Load and combine symptom files
        all_symptoms = []
        for file in symptom_files:
            print(f"Loading {file}...")
            try:
                df = pd.read_csv(file, encoding='latin-1', low_memory=False, on_bad_lines='skip')
                all_symptoms.append(df)
                print(f"  Loaded {len(df)} symptom records")
            except Exception as e:
                print(f"  Error loading {file}: {e}")
                continue
        
        symptoms_data = pd.concat(all_symptoms, ignore_index=True) if all_symptoms else pd.DataFrame()
        print(f"Total symptom records: {len(symptoms_data)}")
        
        # Load and combine vaccine files
        all_vax = []
        for file in vax_files:
            print(f"Loading {file}...")
            try:
                df = pd.read_csv(file, encoding='latin-1', low_memory=False, on_bad_lines='skip')
                all_vax.append(df)
                print(f"  Loaded {len(df)} vaccine records")
            except Exception as e:
                print(f"  Error loading {file}: {e}")
                continue
        
        vax_data = pd.concat(all_vax, ignore_index=True) if all_vax else pd.DataFrame()
        print(f"Total vaccine records: {len(vax_data)}")
        
        # Sample 100K reports
        target_size = min(100000, len(main_data))
        sampled_data = main_data.sample(n=target_size, random_state=42)
        print(f"Sampled {len(sampled_data)} reports")
        
        # Get symptoms for sampled reports
        sampled_ids = set(sampled_data['VAERS_ID'])
        relevant_symptoms = symptoms_data[symptoms_data['VAERS_ID'].isin(sampled_ids)]
        
        # Group symptoms by VAERS_ID
        symptom_groups = relevant_symptoms.groupby('VAERS_ID')['SYMPTOM1'].apply(list).to_dict()
        
        # Get vaccines for sampled reports  
        relevant_vax = vax_data[vax_data['VAERS_ID'].isin(sampled_ids)]
        
        # Group vaccine info by VAERS_ID
        vax_groups = relevant_vax.groupby('VAERS_ID').agg({
            'VAX_TYPE': list,
            'VAX_MANU': list, 
            'VAX_NAME': list,
            'VAX_DOSE_SERIES': list,
            'VAX_ROUTE': list,
            'VAX_SITE': list
        }).to_dict('index')
        
        # Create final dataset
        result_data = []
        for _, row in sampled_data.iterrows():
            vaers_id = row['VAERS_ID']
            
            # Get symptoms (remove empty/null values)
            symptoms = symptom_groups.get(vaers_id, [])
            symptoms = [s for s in symptoms if pd.notna(s) and s.strip()]
            
            # Get vaccine info
            vax_info = vax_groups.get(vaers_id, {})
            
            record = {
                "VAERS_ID": int(vaers_id),
                "RECVDATE": row.get('RECVDATE'),
                "STATE": row.get('STATE'),
                "AGE_YRS": float(row['AGE_YRS']) if pd.notna(row.get('AGE_YRS')) else None,
                "SEX": row.get('SEX'),
                "SYMPTOM_TEXT": row.get('SYMPTOM_TEXT'),
                "DIED": row.get('DIED'),
                "L_THREAT": row.get('L_THREAT'),
                "ER_VISIT": row.get('ER_VISIT'),
                "HOSPITAL": row.get('HOSPITAL'),
                "DISABLE": row.get('DISABLE'),
                "RECOVD": row.get('RECOVD'),
                "VAX_DATE": row.get('VAX_DATE'),
                "ONSET_DATE": row.get('ONSET_DATE'),
                "NUMDAYS": float(row['NUMDAYS']) if pd.notna(row.get('NUMDAYS')) else None,
                "VAX_TYPE_list": vax_info.get('VAX_TYPE', []),
                "VAX_MANU_list": vax_info.get('VAX_MANU', []),
                "VAX_NAME_list": vax_info.get('VAX_NAME', []),
                "VAX_DOSE_SERIES_list": vax_info.get('VAX_DOSE_SERIES', []),
                "VAX_ROUTE_list": vax_info.get('VAX_ROUTE', []),
                "VAX_SITE_list": vax_info.get('VAX_SITE', []),
                "symptom_list": symptoms
            }
            result_data.append(record)
        
        print(f"Created {len(result_data)} complete records")
        
        # Save to JSON 
        output_file = "../json_data/vaers_subset.json"
        with open(output_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"Created vaers_subset.json with {len(result_data):,} records")
        
        # Sample stats
        ages = [r['AGE_YRS'] for r in result_data if r['AGE_YRS'] is not None]
        dates = [r['RECVDATE'] for r in result_data if r['RECVDATE']]
        sexes = [r['SEX'] for r in result_data if r['SEX']]
        
        print(f"\nSample statistics:")
        if dates:
            print(f"  Date range: {min(dates)} to {max(dates)}")
        if ages:
            print(f"  Age range: {min(ages):.1f} to {max(ages):.1f} years")
        if sexes:
            from collections import Counter
            sex_counts = Counter(sexes)
            print(f"  Sex distribution: {dict(sex_counts)}")
        
        print(f"\nVAERS subset saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Error creating VAERS subset: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_proper_vaers_subset()