import duckdb
import json
from typing import List, Dict, Tuple
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv
import requests


class VaccineMapper:
    def __init__(self, db_path: str = "../intermediate_results/vaers_database.duckdb"):
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        
        # For LLM mapping if needed
        load_dotenv()
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        
    def get_vaers_vaccines(self) -> List[Dict]:
        """Get unique vaccines from VAERS data"""
        query = """
        SELECT DISTINCT 
            VAX_TYPE,
            VAX_NAME,
            VAX_MANU,
            COUNT(*) as record_count
        FROM all_vax
        WHERE VAX_NAME IS NOT NULL
        GROUP BY VAX_TYPE, VAX_NAME, VAX_MANU
        ORDER BY record_count DESC
        """
        
        try:
            result = self.conn.execute(query).fetchall()
            vaccines = []
            for row in result:
                vaccines.append({
                    'vax_type': row[0],
                    'vax_name': row[1],
                    'vax_manu': row[2],
                    'record_count': row[3]
                })
            return vaccines
        except Exception as e:
            print(f"Error getting VAERS vaccines: {e}")
            return []
    
    def get_pdf_vaccines(self) -> List[Dict]:
        """Get unique vaccines from PDF extractions"""
        query = """
        SELECT DISTINCT
            vax_type,
            vax_name,
            vax_manu,
            filename
        FROM pdf_vaccine_extractions
        WHERE success = true AND vax_name IS NOT NULL
        ORDER BY vax_name
        """
        
        try:
            result = self.conn.execute(query).fetchall()
            vaccines = []
            for row in result:
                vaccines.append({
                    'pdf_vax_type': row[0],
                    'pdf_vax_name': row[1],
                    'pdf_vax_manu': row[2],
                    'pdf_filename': row[3]
                })
            return vaccines
        except Exception as e:
            print(f"Error getting PDF vaccines: {e}")
            return []
    
    def create_manual_mappings(self, vaers_vaccines: List[Dict], pdf_vaccines: List[Dict]) -> List[Dict]:
        """Create mappings using rule-based matching"""
        mappings = []
        
        # Create lookup dictionaries for faster matching
        pdf_by_name = {}
        pdf_by_type = {}
        
        for pdf in pdf_vaccines:
            # Clean and standardize names
            clean_name = pdf['pdf_vax_name'].upper().strip()
            pdf_by_name[clean_name] = pdf
            
            if pdf['pdf_vax_type']:
                clean_type = pdf['pdf_vax_type'].upper().strip()
                if clean_type not in pdf_by_type:
                    pdf_by_type[clean_type] = []
                pdf_by_type[clean_type].append(pdf)
        
        # Try to match each VAERS vaccine
        for vaers in vaers_vaccines:
            vaers_name = vaers['vax_name'].upper().strip() if vaers['vax_name'] else ''
            vaers_type = vaers['vax_type'].upper().strip() if vaers['vax_type'] else ''
            
            match_found = False
            
            # 1. Try exact name match
            if vaers_name in pdf_by_name:
                pdf = pdf_by_name[vaers_name]
                mappings.append({
                    'vaers_vax_type': vaers['vax_type'],
                    'vaers_vax_name': vaers['vax_name'],
                    'vaers_vax_manu': vaers['vax_manu'],
                    'vaers_record_count': vaers['record_count'],
                    'pdf_vax_type': pdf['pdf_vax_type'],
                    'pdf_vax_name': pdf['pdf_vax_name'],
                    'pdf_vax_manu': pdf['pdf_vax_manu'],
                    'pdf_filename': pdf['pdf_filename'],
                    'match_type': 'exact_name',
                    'match_confidence': 1.0
                })
                match_found = True
                continue
            
            # 2. Try type match
            if vaers_type and vaers_type in pdf_by_type:
                # Check if manufacturer also matches
                for pdf in pdf_by_type[vaers_type]:
                    if (vaers['vax_manu'] and pdf['pdf_vax_manu'] and 
                        vaers['vax_manu'].upper() in pdf['pdf_vax_manu'].upper()):
                        mappings.append({
                            'vaers_vax_type': vaers['vax_type'],
                            'vaers_vax_name': vaers['vax_name'],
                            'vaers_vax_manu': vaers['vax_manu'],
                            'vaers_record_count': vaers['record_count'],
                            'pdf_vax_type': pdf['pdf_vax_type'],
                            'pdf_vax_name': pdf['pdf_vax_name'],
                            'pdf_vax_manu': pdf['pdf_vax_manu'],
                            'pdf_filename': pdf['pdf_filename'],
                            'match_type': 'type_and_manu',
                            'match_confidence': 0.8
                        })
                        match_found = True
                        break
                
                # If no manufacturer match, take first type match
                if not match_found and pdf_by_type[vaers_type]:
                    pdf = pdf_by_type[vaers_type][0]
                    mappings.append({
                        'vaers_vax_type': vaers['vax_type'],
                        'vaers_vax_name': vaers['vax_name'],
                        'vaers_vax_manu': vaers['vax_manu'],
                        'vaers_record_count': vaers['record_count'],
                        'pdf_vax_type': pdf['pdf_vax_type'],
                        'pdf_vax_name': pdf['pdf_vax_name'],
                        'pdf_vax_manu': pdf['pdf_vax_manu'],
                        'pdf_filename': pdf['pdf_filename'],
                        'match_type': 'type_only',
                        'match_confidence': 0.6
                    })
                    match_found = True
            
            # 3. Try partial name matching
            if not match_found and vaers_name:
                for pdf_name, pdf in pdf_by_name.items():
                    # Check if key words match
                    vaers_words = set(vaers_name.split())
                    pdf_words = set(pdf_name.split())
                    common_words = vaers_words.intersection(pdf_words)
                    
                    # Remove common words like 'VACCINE', 'NO', 'BRAND', 'NAME'
                    common_words -= {'VACCINE', 'NO', 'BRAND', 'NAME', 'THE', 'OF', 'AND'}
                    
                    if len(common_words) >= 2:  # At least 2 meaningful words match
                        mappings.append({
                            'vaers_vax_type': vaers['vax_type'],
                            'vaers_vax_name': vaers['vax_name'],
                            'vaers_vax_manu': vaers['vax_manu'],
                            'vaers_record_count': vaers['record_count'],
                            'pdf_vax_type': pdf['pdf_vax_type'],
                            'pdf_vax_name': pdf['pdf_vax_name'],
                            'pdf_vax_manu': pdf['pdf_vax_manu'],
                            'pdf_filename': pdf['pdf_filename'],
                            'match_type': 'partial_name',
                            'match_confidence': 0.4
                        })
                        match_found = True
                        break
            
            # 4. No match found
            if not match_found:
                mappings.append({
                    'vaers_vax_type': vaers['vax_type'],
                    'vaers_vax_name': vaers['vax_name'],
                    'vaers_vax_manu': vaers['vax_manu'],
                    'vaers_record_count': vaers['record_count'],
                    'pdf_vax_type': None,
                    'pdf_vax_name': 'NO MATCH',
                    'pdf_vax_manu': None,
                    'pdf_filename': None,
                    'match_type': 'no_match',
                    'match_confidence': 0.0
                })
        
        return mappings
    
    def create_llm_mappings(self, vaers_vaccines: List[Dict], pdf_vaccines: List[Dict]) -> List[Dict]:
        """Use Claude to create intelligent mappings"""
        # Prepare data for LLM
        vaers_list = []
        for v in vaers_vaccines[:50]:  # Limit to avoid token limits
            vaers_list.append(f"{v['vax_type']} | {v['vax_name']} | {v['vax_manu']}")
        
        pdf_list = []
        for p in pdf_vaccines:
            pdf_list.append(f"{p['pdf_vax_type']} | {p['pdf_vax_name']} | {p['pdf_vax_manu']} | {p['pdf_filename']}")
        
        prompt = f"""
        Match VAERS vaccine records to PDF vaccine records. Return JSON array with mappings.
        
        VAERS Vaccines (TYPE | NAME | MANUFACTURER):
        {chr(10).join(vaers_list)}
        
        PDF Vaccines (TYPE | NAME | MANUFACTURER | FILENAME):
        {chr(10).join(pdf_list)}
        
        For each VAERS vaccine, find the best matching PDF or mark as "NO MATCH".
        Return JSON array of objects with: vaers_index, pdf_index (or -1 for no match), match_confidence (0-1)
        """
        
        # Make API call (simplified version - you might want to use the full implementation from llm_ask.py)
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            response.raise_for_status()
            # Parse response and create mappings
            # ... implementation details ...
        except Exception as e:
            print(f"LLM mapping failed: {e}")
            return []
    
    def save_mappings_to_db(self, mappings: List[Dict]):
        """Save mapping table to database"""
        # Create mapping table
        self.conn.execute("""
        CREATE OR REPLACE TABLE vaccine_mapping_table (
            vaers_vax_type VARCHAR,
            vaers_vax_name VARCHAR,
            vaers_vax_manu VARCHAR,
            vaers_record_count INTEGER,
            pdf_vax_type VARCHAR,
            pdf_vax_name VARCHAR,
            pdf_vax_manu VARCHAR,
            pdf_filename VARCHAR,
            match_type VARCHAR,
            match_confidence FLOAT
        )
        """)
        
        # Convert to DataFrame for easy insertion
        df = pd.DataFrame(mappings)
        self.conn.execute("INSERT INTO vaccine_mapping_table SELECT * FROM df")
        
        print(f"✓ Saved {len(mappings)} mappings to vaccine_mapping_table")
    
    def create_mapping_views(self):
        """Create useful views for analysis"""
        # Summary view
        self.conn.execute("""
        CREATE OR REPLACE VIEW vaccine_mapping_summary AS
        SELECT 
            match_type,
            COUNT(*) as count,
            SUM(vaers_record_count) as total_vaers_records,
            AVG(match_confidence) as avg_confidence
        FROM vaccine_mapping_table
        GROUP BY match_type
        ORDER BY count DESC
        """)
        
        # High confidence matches
        self.conn.execute("""
        CREATE OR REPLACE VIEW high_confidence_matches AS
        SELECT * FROM vaccine_mapping_table
        WHERE match_confidence >= 0.8
        ORDER BY vaers_record_count DESC
        """)
        
        # Vaccines needing manual review
        self.conn.execute("""
        CREATE OR REPLACE VIEW vaccines_for_review AS
        SELECT * FROM vaccine_mapping_table
        WHERE match_confidence > 0 AND match_confidence < 0.8
        ORDER BY vaers_record_count DESC
        """)
        
        print("✓ Created mapping analysis views")
    
    def generate_mapping_report(self):
        """Generate summary report of mappings"""
        # Overall statistics
        stats = self.conn.execute("""
        SELECT 
            COUNT(DISTINCT vaers_vax_name) as total_vaers_vaccines,
            COUNT(DISTINCT CASE WHEN pdf_filename IS NOT NULL THEN vaers_vax_name END) as matched_vaccines,
            COUNT(DISTINCT pdf_filename) as unique_pdfs_matched,
            SUM(vaers_record_count) as total_vaers_records,
            SUM(CASE WHEN pdf_filename IS NOT NULL THEN vaers_record_count ELSE 0 END) as matched_records
        FROM vaccine_mapping_table
        """).fetchone()
        
        print("\n=== VACCINE MAPPING REPORT ===")
        print(f"Total VAERS vaccines: {stats[0]}")
        print(f"Matched vaccines: {stats[1]} ({stats[1]/stats[0]*100:.1f}%)")
        print(f"Unique PDFs matched: {stats[2]}")
        print(f"Total VAERS records: {stats[3]:,}")
        print(f"Matched VAERS records: {stats[4]:,} ({stats[4]/stats[3]*100:.1f}%)")
        
        # Match type breakdown
        print("\nMatch Type Breakdown:")
        breakdown = self.conn.execute("SELECT * FROM vaccine_mapping_summary").fetchall()
        for row in breakdown:
            print(f"  {row[0]}: {row[1]} vaccines ({row[2]:,} records, {row[3]:.2f} confidence)")
        
        # Top unmatched vaccines
        print("\nTop 10 Unmatched Vaccines (by record count):")
        unmatched = self.conn.execute("""
        SELECT vaers_vax_name, vaers_vax_type, vaers_vax_manu, vaers_record_count
        FROM vaccine_mapping_table
        WHERE match_type = 'no_match'
        ORDER BY vaers_record_count DESC
        LIMIT 10
        """).fetchall()
        
        for vaccine in unmatched:
            print(f"  {vaccine[1]} - {vaccine[0]} by {vaccine[2]} ({vaccine[3]:,} records)")
    
    def export_mapping_to_excel(self, output_path: str = "../intermediate_results/vaccine_mappings.xlsx"):
        """Export mappings to Excel for manual review"""
        # Get all mappings
        df = self.conn.execute("SELECT * FROM vaccine_mapping_table ORDER BY vaers_record_count DESC").df()
        
        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # All mappings
            df.to_excel(writer, sheet_name='All Mappings', index=False)
            
            # Matched only
            matched_df = df[df['match_type'] != 'no_match']
            matched_df.to_excel(writer, sheet_name='Matched Vaccines', index=False)
            
            # Unmatched only
            unmatched_df = df[df['match_type'] == 'no_match']
            unmatched_df.to_excel(writer, sheet_name='Unmatched Vaccines', index=False)
            
            # Summary statistics
            summary_df = self.conn.execute("SELECT * FROM vaccine_mapping_summary").df()
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"\n✓ Exported mappings to {output_path}")


def main():
    mapper = VaccineMapper()
    
    print("Loading vaccine data...")
    vaers_vaccines = mapper.get_vaers_vaccines()
    pdf_vaccines = mapper.get_pdf_vaccines()
    
    print(f"Found {len(vaers_vaccines)} unique VAERS vaccines")
    print(f"Found {len(pdf_vaccines)} unique PDF vaccines")
    
    if not vaers_vaccines or not pdf_vaccines:
        print("✗ Error: Missing vaccine data. Make sure to run vaers_parser.py and pdf_vaccine_extractor.py first.")
        return
    
    print("\nCreating vaccine mappings...")
    mappings = mapper.create_manual_mappings(vaers_vaccines, pdf_vaccines)
    
    print("Saving mappings to database...")
    mapper.save_mappings_to_db(mappings)
    mapper.create_mapping_views()
    
    # Generate report
    mapper.generate_mapping_report()
    
    # Export to Excel
    mapper.export_mapping_to_excel()
    
    print("\n✓ Vaccine mapping complete!")
    print("  - Use 'vaccine_mapping_table' to join VAERS and PDF data")
    print("  - Check 'vaccine_mappings.xlsx' for manual review")


if __name__ == "__main__":
    main()