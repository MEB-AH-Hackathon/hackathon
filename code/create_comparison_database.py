#!/usr/bin/env python3

import duckdb
import pandas as pd
import json
from pathlib import Path
from collections import Counter, defaultdict
from vaccine_mappings import VACCINE_MAPPINGS

class ComparisonDatabaseCreator:
    def __init__(self, 
                 vaers_data_dir="../vaers_data/vaers_data",
                 pdf_json_path="../json_data/pdf_extraction_results.json",
                 pdf_names_path="../json_data/pdf_vaccine_names_only.json",
                 output_db_path="../duckdb_data/vaccine_comparison.duckdb",
                 json_output_dir="../json_data"):
        self.vaers_data_dir = Path(vaers_data_dir)
        self.pdf_json_path = Path(pdf_json_path)
        self.pdf_names_path = Path(pdf_names_path)
        self.output_db_path = output_db_path
        self.json_output_dir = Path(json_output_dir)
        self.json_output_dir.mkdir(exist_ok=True)
        
        # Get our crosswalked vaccines
        self.vaccine_mappings = {m["vaers_vaccine"]: m["pdf_vaccine"] for m in VACCINE_MAPPINGS}
        print(f"Processing {len(self.vaccine_mappings)} crosswalked vaccines")
    
    def get_pdf_adverse_events(self):
        """Extract adverse events from PDF JSON files for crosswalked vaccines"""
        print("Getting PDF adverse events from JSON files...")
        
        # Read PDF extraction results (has filename and adverse events)
        with open(self.pdf_json_path, 'r') as f:
            pdf_extraction_data = json.load(f)
        
        # Read PDF vaccine names (has filename and vax_name)
        with open(self.pdf_names_path, 'r') as f:
            pdf_names_data = json.load(f)
        
        print(f"Loaded {len(pdf_extraction_data.get('successful', []))} PDF extractions")
        print(f"Loaded {len(pdf_names_data)} PDF vaccine name mappings")
        
        # Create mapping from filename to vax_name
        filename_to_vax_name = {}
        for item in pdf_names_data:
            filename_to_vax_name[item['filename']] = item['vax_name']
        
        # Get all PDF vaccine names we care about (from our crosswalk)
        pdf_vaccine_names = set(self.vaccine_mappings.values())
        
        # Process the results
        pdf_results = {}
        found_count = 0
        
        # Go through successful PDF extractions
        for item in pdf_extraction_data.get('successful', []):
            filename = item.get('filename', '')
            
            # Get the vax_name for this filename
            vax_name = filename_to_vax_name.get(filename, '')
            
            # Check if this is one of our crosswalked vaccines
            if vax_name in pdf_vaccine_names:
                # Get symptoms list from the data object
                data = item.get('data', {})
                symptoms = data.get('symptoms_list', [])
                if isinstance(symptoms, str):
                    try:
                        symptoms = json.loads(symptoms)
                    except:
                        symptoms = []
                elif symptoms is None:
                    symptoms = []
                
                pdf_results[vax_name] = {
                    'adverse_events': symptoms,
                    'controlled_trial_text': data.get('controlled_trial_text', '')
                }
                found_count += 1
                print(f"  Found: {filename} -> {vax_name}")
        
        print(f"\nFound PDF data for {found_count} crosswalked vaccines")
        
        # Check for any missing vaccines
        missing_vaccines = pdf_vaccine_names - set(pdf_results.keys())
        if missing_vaccines:
            print(f"WARNING: No PDF data found for: {missing_vaccines}")
        
        return pdf_results
    
    def process_vaers_symptoms_for_vaccines(self, years=None):
        """Process VAERS data to count symptoms for crosswalked vaccines"""
        if years is None:
            years = [2020, 2021, 2022, 2023, 2024]  # Recent years
        
        print(f"Processing VAERS data for years: {years}")
        
        # We'll accumulate symptom counts for each vaccine
        vaccine_symptom_counts = defaultdict(lambda: Counter())
        vaccine_report_counts = defaultdict(int)
        
        for year in years:
            print(f"\nProcessing year {year}...")
            
            # Check if files exist
            vax_file = self.vaers_data_dir / f"{year}VAERSVAX.csv"
            symptoms_file = self.vaers_data_dir / f"{year}VAERSSYMPTOMS.csv"
            
            if not vax_file.exists() or not symptoms_file.exists():
                print(f"  Skipping {year} - files not found")
                continue
            
            # Read VAX file to get vaccine-to-VAERS_ID mapping
            print(f"  Reading {vax_file.name}...")
            try:
                vax_df = pd.read_csv(vax_file, encoding='utf-8', low_memory=False)
            except UnicodeDecodeError:
                vax_df = pd.read_csv(vax_file, encoding='latin-1', low_memory=False)
            
            # Filter to only crosswalked vaccines
            crosswalked_vax_df = vax_df[vax_df['VAX_NAME'].isin(self.vaccine_mappings.keys())]
            print(f"  Found {len(crosswalked_vax_df)} records for crosswalked vaccines")
            
            if len(crosswalked_vax_df) == 0:
                continue
            
            # Get VAERS_IDs for these vaccines
            vaers_ids_for_vaccines = defaultdict(set)
            for _, row in crosswalked_vax_df.iterrows():
                vax_name = row['VAX_NAME']
                vaers_id = row['VAERS_ID']
                vaers_ids_for_vaccines[vax_name].add(vaers_id)
            
            # Read SYMPTOMS file
            print(f"  Reading {symptoms_file.name}...")
            try:
                symptoms_df = pd.read_csv(symptoms_file, encoding='utf-8', low_memory=False, on_bad_lines='skip')
            except UnicodeDecodeError:
                try:
                    symptoms_df = pd.read_csv(symptoms_file, encoding='latin-1', low_memory=False, on_bad_lines='skip')
                except Exception as e:
                    print(f"    Warning: Error reading symptoms file: {e}")
                    continue
            
            # Get symptom columns (SYMPTOM1, SYMPTOM2, etc., not SYMPTOMVERSION)
            symptom_cols = [col for col in symptoms_df.columns if col.startswith('SYMPTOM') and not col.startswith('SYMPTOMVERSION')]
            symptom_cols = [col for col in symptom_cols if col[-1].isdigit()]
            
            print(f"  Processing symptoms for {len(symptom_cols)} symptom columns...")
            
            # Process symptoms for each vaccine
            for vax_name, vaers_ids in vaers_ids_for_vaccines.items():
                # Filter symptoms to only reports for this vaccine
                vax_symptoms_df = symptoms_df[symptoms_df['VAERS_ID'].isin(vaers_ids)]
                
                # Count symptoms
                for _, row in vax_symptoms_df.iterrows():
                    vaccine_report_counts[vax_name] += 1
                    
                    for col in symptom_cols:
                        symptom = row[col]
                        if pd.notna(symptom) and str(symptom).strip():
                            symptom_clean = str(symptom).strip()
                            vaccine_symptom_counts[vax_name][symptom_clean] += 1
                
                print(f"    {vax_name}: {len(vax_symptoms_df)} reports")
        
        return dict(vaccine_symptom_counts), dict(vaccine_report_counts)
    
    def create_comparison_database(self):
        """Create the final comparison database"""
        print("\n=== Creating Vaccine Comparison Database ===")
        
        # Get PDF adverse events
        pdf_data = self.get_pdf_adverse_events()
        
        # Process VAERS symptoms
        vaers_symptom_counts, vaers_report_counts = self.process_vaers_symptoms_for_vaccines()
        
        # Create output database
        conn = duckdb.connect(self.output_db_path)
        
        # Create table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS vaccine_comparisons (
            vaccine_name VARCHAR,           -- PDF vaccine name
            vaers_name VARCHAR,             -- VAERS vaccine name  
            pdf_name VARCHAR,               -- PDF vaccine name (same as vaccine_name)
            vaers_symptom_counts JSON,      -- JSON object with symptom counts
            pdf_adverse_events JSON,        -- JSON array of adverse events from PDF
            total_vaers_reports INTEGER,    -- total VAERS reports for this vaccine
            pdf_controlled_trial_text VARCHAR -- full text from controlled trials
        )
        """)
        
        # Prepare data for insertion
        records = []
        for vaers_vaccine, pdf_vaccine in self.vaccine_mappings.items():
            
            # Get VAERS symptom counts (convert Counter to dict)
            symptom_counts = dict(vaers_symptom_counts.get(vaers_vaccine, {}))
            total_reports = vaers_report_counts.get(vaers_vaccine, 0)
            
            # Get PDF adverse events
            pdf_info = pdf_data.get(pdf_vaccine, {})
            adverse_events = pdf_info.get('adverse_events', [])
            controlled_trial_text = pdf_info.get('controlled_trial_text', '')
            
            record = {
                'vaccine_name': pdf_vaccine,
                'vaers_name': vaers_vaccine,
                'pdf_name': pdf_vaccine,
                'vaers_symptom_counts': json.dumps(symptom_counts),
                'pdf_adverse_events': json.dumps(adverse_events),
                'total_vaers_reports': total_reports,
                'pdf_controlled_trial_text': controlled_trial_text
            }
            records.append(record)
            
            print(f"Added: {vaers_vaccine}")
            print(f"  → {pdf_vaccine}")
            print(f"  VAERS reports: {total_reports:,}")
            print(f"  VAERS unique symptoms: {len(symptom_counts)}")
            print(f"  PDF adverse events: {len(adverse_events)}")
            print()
        
        # Insert data
        records_df = pd.DataFrame(records)
        conn.execute("DELETE FROM vaccine_comparisons")  # Clear existing data
        conn.execute("INSERT INTO vaccine_comparisons SELECT * FROM records_df")
        
        print(f"Inserted {len(records)} vaccine comparisons into database")
        
        # Show summary
        summary = conn.execute("""
        SELECT 
            COUNT(*) as total_vaccines,
            SUM(total_vaers_reports) as total_reports,
            AVG(total_vaers_reports) as avg_reports_per_vaccine
        FROM vaccine_comparisons
        """).fetchone()
        
        print(f"\nDatabase Summary:")
        print(f"  Total vaccines: {summary[0]}")
        print(f"  Total VAERS reports: {summary[1]:,}")
        print(f"  Average reports per vaccine: {summary[2]:.1f}")
        
        conn.close()
        print(f"\nDatabase saved to: {self.output_db_path}")
        
        # Also save as JSON
        print(f"\nSaving JSON output...")
        
        # Save the main comparison data
        json_output = {
            "vaccines": records,
            "summary": {
                "total_vaccines": summary[0],
                "total_vaers_reports": int(summary[1]),
                "avg_reports_per_vaccine": float(summary[2])
            },
            "metadata": {
                "created_date": "2025-06-03",
                "description": "Vaccine comparison data with VAERS symptom counts and PDF adverse events"
            }
        }
        
        with open(self.json_output_dir / "vaccine_comparisons.json", 'w') as f:
            json.dump(json_output, f, indent=2)
        
        # Also save symptom counts separately for easier access
        symptom_data = {}
        for record in records:
            symptom_data[record['vaers_name']] = {
                "pdf_name": record['pdf_name'],
                "symptom_counts": json.loads(record['vaers_symptom_counts']),
                "total_reports": record['total_vaers_reports'],
                "pdf_adverse_events": json.loads(record['pdf_adverse_events'])
            }
        
        with open(self.json_output_dir / "vaccine_symptom_counts.json", 'w') as f:
            json.dump(symptom_data, f, indent=2)
        
        print(f"JSON files saved to: {self.json_output_dir}")

def main():
    creator = ComparisonDatabaseCreator()
    creator.create_comparison_database()

if __name__ == "__main__":
    main()