import csv
import duckdb
import pandas as pd
from pathlib import Path
from collections import Counter


def extract_vaers_vaccines(vaers_data_dir: str = "../vaers_data/vaers_data"):
    """Extract top unique vaccines from VAERSVAX CSV files"""
    print("Extracting vaccines from VAERS VAX files...")
    
    # Track unique vaccines
    all_vaccines = Counter()
    vaers_dir = Path(vaers_data_dir)
    
    # Process each VAERSVAX file
    vax_files = list(vaers_dir.glob("*VAERSVAX.csv"))
    
    for vax_file in vax_files[:5]:  # Process first 5 files for speed
        print(f"  Processing {vax_file.name}...")
        try:
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(vax_file, 'r', encoding=encoding) as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row.get('VAX_NAME'):
                                key = (
                                    row.get('VAX_TYPE', '').strip(),
                                    row.get('VAX_NAME', '').strip(),
                                    row.get('VAX_MANU', '').strip()
                                )
                                all_vaccines[key] += 1
                    break
                except UnicodeDecodeError:
                    continue
        except Exception as e:
            print(f"    Error: {e}")
    
    # Convert to list, sorted by frequency
    vaccine_list = []
    for (vax_type, vax_name, vax_manu), count in all_vaccines.most_common(50):
        if vax_name:  # Skip empty names
            vaccine_list.append({
                'vaers_vax_type': vax_type,
                'vaers_vax_name': vax_name,
                'vaers_vax_manu': vax_manu,
                'vaers_record_count': count
            })
    
    return vaccine_list


def get_pdf_vaccines(db_path: str = "../intermediate_results/vaers_database.duckdb"):
    """Get vaccines from PDF extractions"""
    conn = duckdb.connect(db_path)
    result = conn.execute("""
    SELECT vax_type, vax_name, vax_manu, filename
    FROM pdf_vaccine_extractions
    WHERE success = true AND vax_name IS NOT NULL
    """).fetchall()
    
    pdf_vaccines = []
    for row in result:
        pdf_vaccines.append({
            'pdf_vax_type': row[0],
            'pdf_vax_name': row[1],
            'pdf_vax_manu': row[2],
            'pdf_filename': row[3]
        })
    
    conn.close()
    return pdf_vaccines


def create_mapping_table():
    """Create a simple mapping table for manual review"""
    # Get data from both sources
    vaers_vaccines = extract_vaers_vaccines()
    pdf_vaccines = get_pdf_vaccines()
    
    print(f"\nFound {len(vaers_vaccines)} top VAERS vaccines")
    print(f"Found {len(pdf_vaccines)} PDF vaccines")
    
    # Create mapping dataframes
    vaers_df = pd.DataFrame(vaers_vaccines)
    pdf_df = pd.DataFrame(pdf_vaccines)
    
    # Save to Excel with multiple sheets
    output_path = "../intermediate_results/vaccine_mapping_reference.xlsx"
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sheet 1: Top VAERS vaccines
        vaers_df.to_excel(writer, sheet_name='Top VAERS Vaccines', index=False)
        
        # Sheet 2: PDF vaccines
        pdf_df.to_excel(writer, sheet_name='PDF Vaccines', index=False)
        
        # Sheet 3: Empty mapping template
        mapping_template = pd.DataFrame({
            'vaers_vax_type': vaers_df['vaers_vax_type'],
            'vaers_vax_name': vaers_df['vaers_vax_name'],
            'vaers_vax_manu': vaers_df['vaers_vax_manu'],
            'vaers_record_count': vaers_df['vaers_record_count'],
            'pdf_vax_type': '',
            'pdf_vax_name': 'NO MATCH',
            'pdf_vax_manu': '',
            'pdf_filename': '',
            'match_notes': ''
        })
        mapping_template.to_excel(writer, sheet_name='Mapping Template', index=False)
    
    print(f"\nCreated reference file: {output_path}")
    print("\nVAERS vaccines preview:")
    for i, row in vaers_df.head(10).iterrows():
        print(f"  {row['vaers_vax_name']} ({row['vaers_vax_type']}) - {row['vaers_record_count']} records")
    
    print("\nPDF vaccines:")
    for i, row in pdf_df.iterrows():
        print(f"  {row['pdf_vax_name']} ({row['pdf_vax_type']})")
    
    # Create a simple mapping based on type codes
    print("\nChecking for potential matches by vaccine type...")
    vaers_types = set(vaers_df['vaers_vax_type'].unique())
    pdf_types = set(pdf_df['pdf_vax_type'].unique())
    
    common_types = vaers_types.intersection(pdf_types)
    if common_types:
        print(f"Found common vaccine types: {common_types}")
    else:
        print("No common vaccine type codes found between VAERS and PDFs")
        print(f"  VAERS types: {list(vaers_types)[:10]}...")
        print(f"  PDF types: {pdf_types}")


if __name__ == "__main__":
    create_mapping_table()