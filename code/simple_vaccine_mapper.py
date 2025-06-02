import os
import csv
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
import pandas as pd
import duckdb
from collections import Counter

import requests
from dotenv import load_dotenv


class SimpleVaccineMapper:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set ANTHROPIC_API_KEY")
    
    def extract_vaers_vaccines(self, vaers_data_dir: str = "../vaers_data/vaers_data") -> List[Dict]:
        """Extract unique vaccines from VAERSVAX CSV files"""
        print("Extracting unique vaccines from VAERS VAX files...")
        
        # Track unique vaccines across all files
        global_unique_vaccines = {}
        vaers_dir = Path(vaers_data_dir)
        
        # Find all VAERSVAX files
        vax_files = list(vaers_dir.glob("*VAERSVAX.csv"))
        print(f"Found {len(vax_files)} VAERSVAX files")
        
        total_records = 0
        
        for vax_file in vax_files:
            print(f"  Reading {vax_file.name}...", end="")
            file_vaccines = {}
            file_records = 0
            
            try:
                # Read CSV with different encodings
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        with open(vax_file, 'r', encoding=encoding) as f:
                            reader = csv.DictReader(f)
                            for row in reader:
                                file_records += 1
                                if row.get('VAX_NAME'):
                                    # Create key for this vaccine
                                    key = (
                                        row.get('VAX_TYPE', '').strip(),
                                        row.get('VAX_NAME', '').strip(),
                                        row.get('VAX_MANU', '').strip()
                                    )
                                    # Count within this file
                                    if key not in file_vaccines:
                                        file_vaccines[key] = 1
                                    else:
                                        file_vaccines[key] += 1
                        break
                    except UnicodeDecodeError:
                        continue
                
                # Add file's unique vaccines to global count
                for key, count in file_vaccines.items():
                    if key not in global_unique_vaccines:
                        global_unique_vaccines[key] = count
                    else:
                        global_unique_vaccines[key] += count
                
                total_records += file_records
                print(f" {file_records} records, {len(file_vaccines)} unique vaccines")
                
            except Exception as e:
                print(f" Error: {e}")
        
        print(f"\nTotal vaccine records across all files: {total_records}")
        print(f"Global unique vaccine combinations: {len(global_unique_vaccines)}")
        
        # Convert to list with counts
        vaccine_list = []
        for (vax_type, vax_name, vax_manu), count in global_unique_vaccines.items():
            # Skip empty vaccine names
            if vax_name:
                vaccine_list.append({
                    'vax_type': vax_type,
                    'vax_name': vax_name,
                    'vax_manu': vax_manu,
                    'record_count': count
                })
        
        # Sort by record count
        vaccine_list.sort(key=lambda x: x['record_count'], reverse=True)
        print(f"Final unique vaccines (excluding empty names): {len(vaccine_list)}")
        
        # Show top 10 vaccines
        print("\nTop 10 vaccines by frequency:")
        for i, vax in enumerate(vaccine_list[:10]):
            print(f"  {i+1}. {vax['vax_name']} ({vax['vax_type']}) - {vax['record_count']:,} records")
        
        return vaccine_list
    
    def get_pdf_vaccines(self, db_path: str = "../intermediate_results/vaers_database.duckdb") -> List[Dict]:
        """Get vaccines from PDF extractions"""
        print("\nExtracting vaccines from PDF database...")
        
        conn = duckdb.connect(db_path)
        try:
            result = conn.execute("""
            SELECT DISTINCT
                vax_type,
                vax_name,
                vax_manu,
                filename
            FROM pdf_vaccine_extractions
            WHERE success = true AND vax_name IS NOT NULL
            ORDER BY vax_name
            """).fetchall()
            
            pdf_vaccines = []
            for row in result:
                pdf_vaccines.append({
                    'pdf_vax_type': row[0],
                    'pdf_vax_name': row[1],
                    'pdf_vax_manu': row[2],
                    'pdf_filename': row[3]
                })
            
            print(f"Found {len(pdf_vaccines)} vaccines from PDFs")
            return pdf_vaccines
        finally:
            conn.close()
    
    def create_mappings_with_llm(self, vaers_vaccines: List[Dict], pdf_vaccines: List[Dict]) -> List[Dict]:
        """Send vaccines to Claude for mapping"""
        print("\nSending to Claude for intelligent mapping...")
        
        # Prepare data for Claude - limit to top vaccines to avoid token limits
        vaers_subset = vaers_vaccines[:100]  # Top 100 by frequency
        
        # Format for prompt
        vaers_lines = []
        for i, v in enumerate(vaers_subset):
            vaers_lines.append(
                f"{i}. {v['vax_type']} | {v['vax_name']} | {v['vax_manu']} | Count: {v['record_count']}"
            )
        
        pdf_lines = []
        for i, p in enumerate(pdf_vaccines):
            pdf_lines.append(
                f"{i}. {p['pdf_vax_type']} | {p['pdf_vax_name']} | {p['pdf_vax_manu']} | File: {p['pdf_filename']}"
            )
        
        prompt = f"""Match VAERS vaccine records to PDF package insert records.

VAERS VACCINES (index. TYPE | NAME | MANUFACTURER | Record Count):
{chr(10).join(vaers_lines)}

PDF VACCINES (index. TYPE | NAME | MANUFACTURER | Filename):
{chr(10).join(pdf_lines)}

Create a mapping for each VAERS vaccine. Return a JSON array where each element has:
- vaers_index: index of VAERS vaccine
- pdf_index: index of matching PDF (-1 if no match)
- confidence: 0.0 to 1.0
- reason: brief explanation

Match based on vaccine names, types, and manufacturers. Handle variations like:
- "(NO BRAND NAME)" entries
- Different manufacturer name formats
- Generic vs brand names

Return ONLY the JSON array."""

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
            raw_text = response.json()["content"][0]["text"]
            
            # Clean up the response text
            # Remove any markdown code blocks
            if "```" in raw_text:
                parts = raw_text.split("```")
                for part in parts:
                    if part.strip().startswith("[") or part.strip().startswith("{"):
                        raw_text = part.strip()
                        break
                    elif part.strip().startswith("json"):
                        raw_text = part.strip()[4:].strip()
                        break
            
            raw_text = raw_text.strip()
            
            # Parse response
            try:
                mappings_data = json.loads(raw_text)
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                print(f"Raw response preview: {raw_text[:200]}...")
                return []
            
            # Convert to final mapping format
            final_mappings = []
            for mapping in mappings_data:
                vaers_idx = mapping['vaers_index']
                pdf_idx = mapping['pdf_index']
                
                vaers = vaers_subset[vaers_idx]
                
                if pdf_idx >= 0 and pdf_idx < len(pdf_vaccines):
                    pdf = pdf_vaccines[pdf_idx]
                    final_mappings.append({
                        'vaers_vax_type': vaers['vax_type'],
                        'vaers_vax_name': vaers['vax_name'],
                        'vaers_vax_manu': vaers['vax_manu'],
                        'vaers_record_count': vaers['record_count'],
                        'pdf_vax_type': pdf['pdf_vax_type'],
                        'pdf_vax_name': pdf['pdf_vax_name'],
                        'pdf_vax_manu': pdf['pdf_vax_manu'],
                        'pdf_filename': pdf['pdf_filename'],
                        'match_confidence': mapping['confidence'],
                        'match_reason': mapping['reason']
                    })
                else:
                    final_mappings.append({
                        'vaers_vax_type': vaers['vax_type'],
                        'vaers_vax_name': vaers['vax_name'],
                        'vaers_vax_manu': vaers['vax_manu'],
                        'vaers_record_count': vaers['record_count'],
                        'pdf_vax_type': None,
                        'pdf_vax_name': 'NO MATCH',
                        'pdf_vax_manu': None,
                        'pdf_filename': None,
                        'match_confidence': 0.0,
                        'match_reason': mapping.get('reason', 'No matching PDF found')
                    })
            
            return final_mappings
            
        except Exception as e:
            print(f"Error calling Claude: {e}")
            return []
    
    def save_results(self, mappings: List[Dict]):
        """Save mappings to Excel and JSON"""
        if not mappings:
            print("No mappings to save")
            return
        
        # Save to Excel
        df = pd.DataFrame(mappings)
        output_path = "../intermediate_results/simple_vaccine_mappings.xlsx"
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # All mappings
            df.to_excel(writer, sheet_name='All Mappings', index=False)
            
            # Matched only
            matched_df = df[df['pdf_filename'].notna()]
            matched_df.to_excel(writer, sheet_name='Matched', index=False)
            
            # Unmatched only
            unmatched_df = df[df['pdf_filename'].isna()]
            unmatched_df.to_excel(writer, sheet_name='Unmatched', index=False)
        
        print(f"\nSaved to: {output_path}")
        
        # Also save as JSON
        json_path = "../intermediate_results/simple_vaccine_mappings.json"
        with open(json_path, 'w') as f:
            json.dump(mappings, f, indent=2)
        print(f"Also saved to: {json_path}")
        
        # Print summary
        total = len(mappings)
        matched = len(matched_df)
        print(f"\nSummary:")
        print(f"  Total vaccines: {total}")
        print(f"  Matched: {matched} ({matched/total*100:.1f}%)")
        print(f"  Unmatched: {total - matched} ({(total-matched)/total*100:.1f}%)")


def main():
    mapper = SimpleVaccineMapper()
    
    # Extract VAERS vaccines
    vaers_vaccines = mapper.extract_vaers_vaccines()
    
    # Get PDF vaccines
    pdf_vaccines = mapper.get_pdf_vaccines()
    
    # Create mappings with Claude
    mappings = mapper.create_mappings_with_llm(vaers_vaccines, pdf_vaccines)
    
    # Save results
    mapper.save_results(mappings)
    
    # Show some examples
    if mappings:
        print("\nExample mappings:")
        for mapping in mappings[:5]:
            if mapping['pdf_filename']:
                print(f"\n{mapping['vaers_vax_name']} → {mapping['pdf_vax_name']}")
                print(f"  Confidence: {mapping['match_confidence']}")
                print(f"  Reason: {mapping['match_reason']}")


if __name__ == "__main__":
    main()