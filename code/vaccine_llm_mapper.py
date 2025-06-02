import os
import duckdb
import json
from typing import List, Dict, Optional
import time
from pathlib import Path
import pandas as pd

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError


class VaccineMapping(BaseModel):
    vaers_index: int
    pdf_index: int  # -1 for no match
    match_confidence: float
    match_reason: str


class VaccineMappingResponse(BaseModel):
    mappings: List[VaccineMapping]


class VaccineLLMMapper:
    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"
    DEFAULT_MODEL = "claude-3-haiku-20240307"
    DEFAULT_MAX_TOKENS = 4096

    def __init__(self, api_key: Optional[str] = None, db_path: str = "../intermediate_results/vaers_database.duckdb"):
        load_dotenv()
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set ANTHROPIC_API_KEY or pass api_key parameter.")
        
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)

    def get_vaers_vaccines(self, limit: Optional[int] = None) -> List[Dict]:
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
        
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            result = self.conn.execute(query).fetchall()
            vaccines = []
            for i, row in enumerate(result):
                vaccines.append({
                    'index': i,
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
            for i, row in enumerate(result):
                vaccines.append({
                    'index': i,
                    'pdf_vax_type': row[0],
                    'pdf_vax_name': row[1],
                    'pdf_vax_manu': row[2],
                    'pdf_filename': row[3]
                })
            return vaccines
        except Exception as e:
            print(f"Error getting PDF vaccines: {e}")
            return []

    def create_mapping_batch(
        self,
        vaers_batch: List[Dict],
        pdf_vaccines: List[Dict],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, any]:
        """Create mappings for a batch of VAERS vaccines using LLM"""
        
        # Format VAERS vaccines for prompt
        vaers_lines = []
        for v in vaers_batch:
            vaers_lines.append(
                f"{v['index']}. Type: {v['vax_type'] or 'N/A'} | "
                f"Name: {v['vax_name']} | "
                f"Manufacturer: {v['vax_manu'] or 'N/A'} | "
                f"Records: {v['record_count']}"
            )
        
        # Format PDF vaccines for prompt
        pdf_lines = []
        for p in pdf_vaccines:
            pdf_lines.append(
                f"{p['index']}. Type: {p['pdf_vax_type'] or 'N/A'} | "
                f"Name: {p['pdf_vax_name']} | "
                f"Manufacturer: {p['pdf_vax_manu'] or 'N/A'} | "
                f"File: {p['pdf_filename']}"
            )
        
        prompt = f"""You are a vaccine matching expert. Match VAERS vaccine records to PDF package insert records.

VAERS VACCINES (index. Type | Name | Manufacturer | Record Count):
{chr(10).join(vaers_lines)}

PDF VACCINES (index. Type | Name | Manufacturer | Filename):
{chr(10).join(pdf_lines)}

MATCHING RULES:
1. Match based on vaccine name similarity (brand names, generic names)
2. Consider vaccine type codes (e.g., DTP, MMR, COVID19, FLU3)
3. Consider manufacturer names (may have variations like PFIZER vs PFIZER\\WYETH)
4. Some VAERS entries say "(NO BRAND NAME)" - match these to appropriate generic vaccines
5. If no good match exists, use pdf_index: -1

Return a JSON object with this exact structure:
{{
  "mappings": [
    {{
      "vaers_index": 0,
      "pdf_index": 3,  // or -1 for no match
      "match_confidence": 0.95,  // 0.0 to 1.0
      "match_reason": "Exact name match: DENGVAXIA"
    }},
    // ... one entry for each VAERS vaccine
  ]
}}

IMPORTANT: 
- Include one mapping for EACH VAERS vaccine in the list
- Use pdf_index -1 for vaccines with no good match
- match_confidence: 0.9-1.0 for exact matches, 0.7-0.9 for good matches, 0.4-0.7 for partial matches
- Provide clear match_reason explaining your decision

Respond ONLY with the JSON object."""

        payload = {
            "model": model or self.DEFAULT_MODEL,
            "max_tokens": max_tokens or self.DEFAULT_MAX_TOKENS,
            "messages": [{"role": "user", "content": prompt}]
        }

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.API_VERSION,
            "content-type": "application/json"
        }

        try:
            response = requests.post(self.API_URL, headers=headers, json=payload)
            response.raise_for_status()
            raw_text = response.json()["content"][0]["text"]
            
            # Parse and validate response
            parsed_json = json.loads(raw_text)
            validated_response = VaccineMappingResponse(**parsed_json)
            
            return {
                "success": True,
                "data": validated_response.model_dump(),
                "raw_response": raw_text
            }
        except (json.JSONDecodeError, ValidationError, requests.RequestException) as e:
            return {
                "success": False,
                "error": str(e),
                "raw_response": raw_text if 'raw_text' in locals() else None
            }

    def process_all_vaccines(
        self,
        batch_size: int = 20,
        delay_between_batches: float = 1.5,
        max_vaccines: Optional[int] = None
    ):
        """Process all VAERS vaccines in batches"""
        print("Loading vaccine data...")
        vaers_vaccines = self.get_vaers_vaccines(limit=max_vaccines)
        pdf_vaccines = self.get_pdf_vaccines()
        
        if not vaers_vaccines or not pdf_vaccines:
            print("✗ Error: Missing vaccine data")
            return
        
        print(f"Found {len(vaers_vaccines)} VAERS vaccines to map")
        print(f"Found {len(pdf_vaccines)} PDF vaccines available")
        
        all_mappings = []
        failed_batches = []
        
        # Process in batches
        for i in range(0, len(vaers_vaccines), batch_size):
            batch = vaers_vaccines[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(vaers_vaccines) + batch_size - 1) // batch_size
            
            print(f"\nProcessing batch {batch_num}/{total_batches} ({len(batch)} vaccines)...")
            
            if i > 0:
                time.sleep(delay_between_batches)
            
            result = self.create_mapping_batch(batch, pdf_vaccines)
            
            if result["success"]:
                # Process successful mappings
                for mapping in result["data"]["mappings"]:
                    vaers_idx = mapping["vaers_index"]
                    pdf_idx = mapping["pdf_index"]
                    
                    vaers = batch[vaers_idx - i]  # Adjust for batch offset
                    
                    if pdf_idx >= 0:
                        pdf = pdf_vaccines[pdf_idx]
                        all_mappings.append({
                            'vaers_vax_type': vaers['vax_type'],
                            'vaers_vax_name': vaers['vax_name'],
                            'vaers_vax_manu': vaers['vax_manu'],
                            'vaers_record_count': vaers['record_count'],
                            'pdf_vax_type': pdf['pdf_vax_type'],
                            'pdf_vax_name': pdf['pdf_vax_name'],
                            'pdf_vax_manu': pdf['pdf_vax_manu'],
                            'pdf_filename': pdf['pdf_filename'],
                            'match_confidence': mapping['match_confidence'],
                            'match_reason': mapping['match_reason']
                        })
                    else:
                        all_mappings.append({
                            'vaers_vax_type': vaers['vax_type'],
                            'vaers_vax_name': vaers['vax_name'],
                            'vaers_vax_manu': vaers['vax_manu'],
                            'vaers_record_count': vaers['record_count'],
                            'pdf_vax_type': None,
                            'pdf_vax_name': 'NO MATCH',
                            'pdf_vax_manu': None,
                            'pdf_filename': None,
                            'match_confidence': 0.0,
                            'match_reason': mapping['match_reason']
                        })
                
                print(f"✓ Batch {batch_num} processed successfully")
            else:
                failed_batches.append({
                    'batch_num': batch_num,
                    'error': result['error'],
                    'vaccines': batch
                })
                print(f"✗ Batch {batch_num} failed: {result['error']}")
        
        # Save to database
        if all_mappings:
            self.save_mappings_to_db(all_mappings)
            self.create_summary_views()
            self.generate_report(all_mappings, failed_batches)
            self.export_to_excel(all_mappings)

    def save_mappings_to_db(self, mappings: List[Dict]):
        """Save mappings to database"""
        # Create table
        self.conn.execute("""
        CREATE OR REPLACE TABLE vaccine_llm_mapping (
            vaers_vax_type VARCHAR,
            vaers_vax_name VARCHAR,
            vaers_vax_manu VARCHAR,
            vaers_record_count INTEGER,
            pdf_vax_type VARCHAR,
            pdf_vax_name VARCHAR,
            pdf_vax_manu VARCHAR,
            pdf_filename VARCHAR,
            match_confidence FLOAT,
            match_reason VARCHAR
        )
        """)
        
        # Insert data
        df = pd.DataFrame(mappings)
        self.conn.execute("INSERT INTO vaccine_llm_mapping SELECT * FROM df")
        
        print(f"\n✓ Saved {len(mappings)} mappings to vaccine_llm_mapping table")

    def create_summary_views(self):
        """Create analysis views"""
        # Summary by confidence level
        self.conn.execute("""
        CREATE OR REPLACE VIEW vaccine_mapping_confidence_summary AS
        SELECT 
            CASE 
                WHEN match_confidence >= 0.9 THEN 'High (0.9-1.0)'
                WHEN match_confidence >= 0.7 THEN 'Good (0.7-0.9)'
                WHEN match_confidence >= 0.4 THEN 'Partial (0.4-0.7)'
                WHEN match_confidence > 0 THEN 'Low (0.0-0.4)'
                ELSE 'No Match'
            END as confidence_level,
            COUNT(*) as vaccine_count,
            SUM(vaers_record_count) as total_records
        FROM vaccine_llm_mapping
        GROUP BY confidence_level
        ORDER BY MIN(match_confidence) DESC
        """)
        
        # High confidence matches for immediate use
        self.conn.execute("""
        CREATE OR REPLACE VIEW high_confidence_vaccine_matches AS
        SELECT * FROM vaccine_llm_mapping
        WHERE match_confidence >= 0.9
        ORDER BY vaers_record_count DESC
        """)
        
        print("✓ Created summary views")

    def generate_report(self, mappings: List[Dict], failed_batches: List[Dict]):
        """Generate summary report"""
        total_vaccines = len(mappings)
        matched = len([m for m in mappings if m['pdf_filename'] is not None])
        total_records = sum(m['vaers_record_count'] for m in mappings)
        matched_records = sum(m['vaers_record_count'] for m in mappings if m['pdf_filename'] is not None)
        
        print("\n=== VACCINE MAPPING REPORT ===")
        print(f"Total VAERS vaccines processed: {total_vaccines}")
        print(f"Successfully matched: {matched} ({matched/total_vaccines*100:.1f}%)")
        print(f"Total VAERS records: {total_records:,}")
        print(f"Matched VAERS records: {matched_records:,} ({matched_records/total_records*100:.1f}%)")
        
        if failed_batches:
            print(f"\nFailed batches: {len(failed_batches)}")
        
        # Confidence breakdown
        print("\nConfidence Level Breakdown:")
        breakdown = self.conn.execute("SELECT * FROM vaccine_mapping_confidence_summary").fetchall()
        for row in breakdown:
            print(f"  {row[0]}: {row[1]} vaccines ({row[2]:,} records)")

    def export_to_excel(self, mappings: List[Dict], output_path: str = "../intermediate_results/vaccine_llm_mappings.xlsx"):
        """Export mappings to Excel"""
        df = pd.DataFrame(mappings)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # All mappings
            df.to_excel(writer, sheet_name='All Mappings', index=False)
            
            # High confidence only
            high_conf_df = df[df['match_confidence'] >= 0.9]
            high_conf_df.to_excel(writer, sheet_name='High Confidence', index=False)
            
            # No matches
            no_match_df = df[df['match_confidence'] == 0.0]
            no_match_df.to_excel(writer, sheet_name='No Matches', index=False)
            
            # Summary stats
            summary_data = {
                'Metric': ['Total Vaccines', 'Matched Vaccines', 'Match Rate', 'Total Records', 'Matched Records', 'Record Match Rate'],
                'Value': [
                    len(df),
                    len(df[df['pdf_filename'].notna()]),
                    f"{len(df[df['pdf_filename'].notna()])/len(df)*100:.1f}%",
                    df['vaers_record_count'].sum(),
                    df[df['pdf_filename'].notna()]['vaers_record_count'].sum(),
                    f"{df[df['pdf_filename'].notna()]['vaers_record_count'].sum()/df['vaers_record_count'].sum()*100:.1f}%"
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"\n✓ Exported mappings to {output_path}")


def main():
    try:
        mapper = VaccineLLMMapper()
        
        # Process vaccines with LLM
        mapper.process_all_vaccines(
            batch_size=20,  # Process 20 vaccines at a time
            delay_between_batches=1.5,
            max_vaccines=None  # Set to a number to limit for testing
        )
        
        print("\n✓ Vaccine mapping complete!")
        print("  - Use 'vaccine_llm_mapping' table to join VAERS and PDF data")
        print("  - Check 'vaccine_llm_mappings.xlsx' for manual review")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()