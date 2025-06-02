import pandas as pd
import numpy as np
from pathlib import Path
import json


def merge_vaers_year(year: int = 2024, data_dir: str = "../vaers_data/vaers_data", sample_size: int = 100):
    """Merge VAERS data for a single year into one row per report"""
    
    print(f"Processing VAERS data for year {year}...")
    data_path = Path(data_dir)
    
    # Define file paths
    data_file = data_path / f"{year}VAERSDATA.csv"
    vax_file = data_path / f"{year}VAERSVAX.csv"
    symptoms_file = data_path / f"{year}VAERSSYMPTOMS.csv"
    
    # Check if files exist
    for file in [data_file, vax_file, symptoms_file]:
        if not file.exists():
            print(f"Error: {file} not found!")
            return None
    
    # First, get a random sample of VAERS_IDs from the DATA file
    print(f"Getting random sample of {sample_size} VAERS IDs...")
    try:
        # Read just the VAERS_ID column first
        id_df = pd.read_csv(data_file, encoding='utf-8', usecols=['VAERS_ID'])
    except UnicodeDecodeError:
        id_df = pd.read_csv(data_file, encoding='latin-1', usecols=['VAERS_ID'])
    
    # Random sample of IDs
    total_records = len(id_df)
    print(f"  Total records in {year}: {total_records}")
    
    # Sample random IDs
    if total_records > sample_size:
        sampled_ids = id_df['VAERS_ID'].sample(n=sample_size, random_state=42).tolist()
    else:
        sampled_ids = id_df['VAERS_ID'].tolist()
    
    print(f"  Selected {len(sampled_ids)} random VAERS IDs")
    
    # Now read the full data but only for sampled IDs
    print(f"Reading {data_file.name} for sampled IDs...")
    try:
        data_df = pd.read_csv(data_file, encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        data_df = pd.read_csv(data_file, encoding='latin-1', low_memory=False)
    
    # Filter to only sampled IDs
    data_df = data_df[data_df['VAERS_ID'].isin(sampled_ids)]
    print(f"  Found {len(data_df)} reports")
    
    # Select key columns from DATA
    data_columns = ['VAERS_ID', 'RECVDATE', 'STATE', 'AGE_YRS', 'SEX', 
                    'SYMPTOM_TEXT', 'DIED', 'L_THREAT', 'ER_VISIT', 'HOSPITAL',
                    'DISABLE', 'RECOVD', 'VAX_DATE', 'ONSET_DATE', 'NUMDAYS']
    data_cols_available = [col for col in data_columns if col in data_df.columns]
    data_df = data_df[data_cols_available]
    
    # Read VAX file (vaccine information)
    print(f"Reading {vax_file.name} for sampled IDs...")
    try:
        vax_df = pd.read_csv(vax_file, encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        vax_df = pd.read_csv(vax_file, encoding='latin-1', low_memory=False)
    
    # Filter to only sampled IDs
    vax_df = vax_df[vax_df['VAERS_ID'].isin(sampled_ids)]
    print(f"  Found {len(vax_df)} vaccine records")
    
    # Select key columns from VAX
    vax_columns = ['VAERS_ID', 'VAX_TYPE', 'VAX_MANU', 'VAX_NAME', 
                   'VAX_DOSE_SERIES', 'VAX_ROUTE', 'VAX_SITE']
    vax_cols_available = [col for col in vax_columns if col in vax_df.columns]
    vax_df = vax_df[vax_cols_available]
    
    # Read SYMPTOMS file
    print(f"Reading {symptoms_file.name} for sampled IDs...")
    try:
        symptoms_df = pd.read_csv(symptoms_file, encoding='utf-8', low_memory=False, on_bad_lines='skip')
    except UnicodeDecodeError:
        try:
            symptoms_df = pd.read_csv(symptoms_file, encoding='latin-1', low_memory=False, on_bad_lines='skip')
        except Exception as e:
            print(f"  Warning: Error reading symptoms file: {e}")
            print("  Creating empty symptoms dataframe")
            symptoms_df = pd.DataFrame({'VAERS_ID': sampled_ids, 'symptom_list': [[] for _ in sampled_ids]})
    
    # Filter to only sampled IDs
    if 'VAERS_ID' in symptoms_df.columns:
        symptoms_df = symptoms_df[symptoms_df['VAERS_ID'].isin(sampled_ids)]
    print(f"  Found {len(symptoms_df)} symptom records")
    
    # Process symptoms - convert from wide to list format
    print("Processing symptoms...")
    # Only get SYMPTOM columns, not SYMPTOMVERSION columns
    symptom_cols = [col for col in symptoms_df.columns if col.startswith('SYMPTOM') and not col.startswith('SYMPTOMVERSION')]
    # Filter to only include SYMPTOM1, SYMPTOM2, etc. (not SYMPTOM1VERSION, etc.)
    symptom_cols = [col for col in symptom_cols if col[-1].isdigit()]
    print(f"  Found symptom columns: {symptom_cols[:5]}...")
    
    def get_symptom_list(row):
        """Extract non-null symptoms into a list"""
        symptoms = []
        for col in symptom_cols:
            if pd.notna(row[col]) and str(row[col]).strip():
                symptoms.append(str(row[col]).strip())
        return symptoms
    
    # Create symptoms list for each VAERS_ID
    symptoms_df['symptom_list'] = symptoms_df.apply(get_symptom_list, axis=1)
    symptoms_summary = symptoms_df[['VAERS_ID', 'symptom_list']]
    
    # Handle multiple vaccines per report
    print("Handling multiple vaccines per report...")
    # Group vaccines by VAERS_ID and aggregate
    vax_grouped = vax_df.groupby('VAERS_ID').agg({
        'VAX_TYPE': lambda x: list(x),
        'VAX_MANU': lambda x: list(x),
        'VAX_NAME': lambda x: list(x),
        'VAX_DOSE_SERIES': lambda x: list(x) if 'VAX_DOSE_SERIES' in vax_df.columns else None,
        'VAX_ROUTE': lambda x: list(x) if 'VAX_ROUTE' in vax_df.columns else None,
        'VAX_SITE': lambda x: list(x) if 'VAX_SITE' in vax_df.columns else None
    }).reset_index()
    
    # Rename columns to indicate they are lists
    vax_grouped.columns = ['VAERS_ID'] + [f'{col}_list' if col != 'VAERS_ID' else col for col in vax_grouped.columns[1:]]
    
    # Merge all data
    print("Merging all data...")
    # Start with DATA
    merged_df = data_df.copy()
    
    # Merge with grouped vaccines
    merged_df = merged_df.merge(vax_grouped, on='VAERS_ID', how='left')
    
    # Merge with symptoms
    merged_df = merged_df.merge(symptoms_summary, on='VAERS_ID', how='left')
    
    # Fill NaN symptom lists with empty lists
    merged_df['symptom_list'] = merged_df['symptom_list'].apply(lambda x: x if isinstance(x, list) else [])
    
    print(f"\nFinal merged data: {len(merged_df)} reports")
    print(f"Columns: {list(merged_df.columns)}")
    
    # Display sample
    print("\nSample of merged data:")
    sample = merged_df.head(3)
    for idx, row in sample.iterrows():
        print(f"\nReport {idx + 1}:")
        print(f"  VAERS_ID: {row['VAERS_ID']}")
        print(f"  Age: {row.get('AGE_YRS', 'N/A')}, Sex: {row.get('SEX', 'N/A')}")
        print(f"  Vaccines: {row.get('VAX_NAME_list', [])}")
        print(f"  Symptoms: {row.get('symptom_list', [])[:5]}{'...' if len(row.get('symptom_list', [])) > 5 else ''}")
        print(f"  Serious: Died={row.get('DIED', 'N/A')}, Hospital={row.get('HOSPITAL', 'N/A')}")
    
    return merged_df


def save_merged_data(merged_df, output_path: str = "../intermediate_results/vaers_2024_merged.csv"):
    """Save merged data to CSV and JSON formats"""
    # Save as CSV
    csv_path = output_path
    merged_df.to_csv(csv_path, index=False)
    print(f"\nSaved to CSV: {csv_path}")
    
    # Save as JSON (first 100 records as sample)
    json_path = output_path.replace('.csv', '.json')
    sample_df = merged_df.head(100)
    
    # Convert to JSON-serializable format
    records = []
    for _, row in sample_df.iterrows():
        record = row.to_dict()
        # Ensure lists are properly formatted
        for key, value in record.items():
            if isinstance(value, (list, np.ndarray)):
                record[key] = list(value)
            elif isinstance(value, float) and pd.isna(value):
                record[key] = None
            elif pd.api.types.is_scalar(value) and pd.isna(value):
                record[key] = None
        records.append(record)
    
    with open(json_path, 'w') as f:
        json.dump(records, f, indent=2)
    print(f"Saved sample (100 records) to JSON: {json_path}")
    
    # Create summary statistics
    print("\nSummary Statistics:")
    print(f"  Total reports: {len(merged_df)}")
    print(f"  Reports with symptoms: {sum(merged_df['symptom_list'].apply(len) > 0)}")
    print(f"  Average symptoms per report: {merged_df['symptom_list'].apply(len).mean():.1f}")
    print(f"  Reports with multiple vaccines: {sum(merged_df['VAX_NAME_list'].apply(lambda x: len(x) if isinstance(x, list) else 0) > 1)}")
    
    # Most common vaccines
    all_vaccines = []
    for vax_list in merged_df['VAX_NAME_list']:
        if isinstance(vax_list, list):
            all_vaccines.extend(vax_list)
    
    if all_vaccines:
        vaccine_counts = pd.Series(all_vaccines).value_counts().head(10)
        print("\nTop 10 vaccines:")
        for vax, count in vaccine_counts.items():
            print(f"  {vax}: {count}")
    
    # Most common symptoms
    all_symptoms = []
    for symptom_list in merged_df['symptom_list']:
        if isinstance(symptom_list, list):
            all_symptoms.extend(symptom_list)
    
    if all_symptoms:
        symptom_counts = pd.Series(all_symptoms).value_counts().head(10)
        print("\nTop 10 symptoms:")
        for symptom, count in symptom_counts.items():
            print(f"  {symptom}: {count}")


def main():
    # Process 2024 data with a random sample of 100 records
    merged_df = merge_vaers_year(2024, sample_size=100)
    
    if merged_df is not None:
        save_merged_data(merged_df, "../intermediate_results/vaers_2024_sample100.csv")


if __name__ == "__main__":
    main()