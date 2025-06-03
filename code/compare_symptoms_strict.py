#!/usr/bin/env python3

import os
import duckdb
import json
import time
from typing import Dict, List
from pathlib import Path

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError


class StrictSymptomClassification(BaseModel):
    symptom: str
    classification: str  # "confirmed" or "not_confirmed"
    matched_pdf_event: str  # exact PDF adverse event that matches, or "none"
    
    
class StrictSymptomComparator:
    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"
    DEFAULT_MODEL = "claude-3-haiku-20240307"
    DEFAULT_MAX_TOKENS = 200

    def __init__(self, 
                 comparison_db_path="../duckdb_data/vaccine_comparison.duckdb",
                 output_db_path="../duckdb_data/strict_symptom_classifications.duckdb",
                 json_output_dir="../json_data"):
        load_dotenv()
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set ANTHROPIC_API_KEY")
        
        self.comparison_db_path = comparison_db_path
        self.output_db_path = output_db_path
        self.json_output_dir = Path(json_output_dir)
        self.json_output_dir.mkdir(exist_ok=True)
    
    def get_vaccine_data(self, limit=None):
        """Get all vaccine data from comparison database"""
        conn = duckdb.connect(self.comparison_db_path)
        
        query = """
        SELECT vaccine_name, vaers_name, vaers_symptom_counts, pdf_adverse_events, total_vaers_reports
        FROM vaccine_comparisons
        ORDER BY total_vaers_reports DESC
        """
        if limit:
            query += f" LIMIT {limit}"
            
        vaccines = conn.execute(query).fetchall()
        
        conn.close()
        
        vaccine_data = []
        for row in vaccines:
            vaccine_data.append({
                'vaccine_name': row[0],
                'vaers_name': row[1], 
                'vaers_symptom_counts': json.loads(row[2]),
                'pdf_adverse_events': json.loads(row[3]),
                'total_vaers_reports': row[4]
            })
        
        return vaccine_data
    
    def classify_single_symptom_strict(self, symptom: str, pdf_adverse_events: List[str], vaccine_name: str) -> Dict:
        """Classify a single VAERS symptom with required PDF quote"""
        
        prompt = f"""Does the VAERS symptom "{symptom}" match any adverse event from the {vaccine_name} package insert?

PDF ADVERSE EVENTS: {json.dumps(pdf_adverse_events)}

Rules:
1. Only return "confirmed" if the VAERS symptom is an EXACT MATCH or CLEAR SYNONYM
2. You MUST quote the exact PDF adverse event that matches
3. Be very strict - don't stretch connections

Return a JSON object with this exact structure:
{{
  "symptom": "{symptom}",
  "classification": "confirmed" or "not_confirmed",
  "matched_pdf_event": "exact PDF text that matches" or "none"
}}

Examples:
- VAERS "pyrexia" + PDF "fever" → {{"classification": "confirmed", "matched_pdf_event": "fever"}}
- VAERS "headache" + PDF "headache" → {{"classification": "confirmed", "matched_pdf_event": "headache"}}
- VAERS "rash" + PDF "skin reactions" → {{"classification": "confirmed", "matched_pdf_event": "skin reactions"}}
- VAERS "diarrhea" + PDF ["headache", "fever"] → {{"classification": "not_confirmed", "matched_pdf_event": "none"}}

Return ONLY the JSON object."""

        payload = {
            "model": self.DEFAULT_MODEL,
            "max_tokens": self.DEFAULT_MAX_TOKENS,
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
            raw_text = response.json()["content"][0]["text"].strip()
            
            # Clean up the response (remove markdown code blocks if present)
            if "```" in raw_text:
                start_pos = raw_text.find('{')
                end_pos = raw_text.rfind('}') + 1
                if start_pos != -1 and end_pos != 0:
                    raw_text = raw_text[start_pos:end_pos]
            
            # Parse JSON
            classification_data = json.loads(raw_text)
            
            # Validate structure
            StrictSymptomClassification(**classification_data)
            
            # Verify the matched_pdf_event is actually in the PDF list (if confirmed)
            if classification_data['classification'] == 'confirmed':
                matched_event = classification_data['matched_pdf_event']
                if matched_event == 'none' or matched_event not in pdf_adverse_events:
                    # LLM said confirmed but quoted something not in the PDF - mark as not_confirmed
                    classification_data['classification'] = 'not_confirmed'
                    classification_data['matched_pdf_event'] = 'none'
                    print(f"    ⚠️  Fixed false positive: {symptom} -> {matched_event} not in PDF")
            
            return classification_data
                
        except Exception as e:
            print(f"    Error classifying {symptom}: {e}")
            return {
                'symptom': symptom,
                'classification': 'not_confirmed',
                'matched_pdf_event': 'none'
            }

    def classify_symptoms_for_vaccine_strict(self, vaccine_data: Dict, min_symptom_count: int = 10) -> Dict:
        """Process one vaccine by classifying each symptom with strict matching"""
        
        vaccine_name = vaccine_data['vaccine_name']
        vaers_symptoms = vaccine_data['vaers_symptom_counts']
        pdf_adverse_events = vaccine_data['pdf_adverse_events']
        
        # Filter and sort VAERS symptoms by count (most common first)
        filtered_symptoms = {symptom: count for symptom, count in vaers_symptoms.items() 
                           if count >= min_symptom_count}
        sorted_symptoms = sorted(filtered_symptoms.items(), key=lambda x: x[1], reverse=True)
        
        # Process random 20 symptoms per vaccine for quick testing
        import random
        if len(sorted_symptoms) > 20:
            sorted_symptoms = random.sample(sorted_symptoms, 20)
        else:
            sorted_symptoms = sorted_symptoms[:20]
        
        print(f"\nProcessing {vaccine_name}")
        print(f"  Filtered symptoms (>={min_symptom_count}): {len(sorted_symptoms)}")
        print(f"  PDF adverse events: {pdf_adverse_events}")
        
        # Classify each symptom individually
        classifications = []
        confirmed_count = 0
        
        for i, (symptom, count) in enumerate(sorted_symptoms):
            if i > 0 and i % 10 == 0:  # Progress update every 10 symptoms
                print(f"    Processed {i}/{len(sorted_symptoms)} symptoms...")
            
            classification_result = self.classify_single_symptom_strict(symptom, pdf_adverse_events, vaccine_name)
            classification_result['vaers_count'] = count
            classifications.append(classification_result)
            
            if classification_result['classification'] == "confirmed":
                confirmed_count += 1
                matched_event = classification_result['matched_pdf_event']
                print(f"    ✓ {symptom} ({count:,} reports) -> CONFIRMED via '{matched_event}'")
            
            # Small delay between calls
            time.sleep(0.1)
        
        print(f"  ✓ Complete: {confirmed_count}/{len(classifications)} symptoms confirmed")
        
        return {
            'success': True,
            'vaccine_name': vaccine_name,
            'vaers_name': vaccine_data['vaers_name'],
            'classifications': classifications,
            'total_vaers_reports': vaccine_data['total_vaers_reports'],
            'pdf_adverse_events': pdf_adverse_events
        }
    
    def create_strict_classifications_database(self, classifications: List[Dict]):
        """Create database with strict symptom classifications"""
        conn = duckdb.connect(self.output_db_path)
        
        # Create main classifications table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS strict_symptom_classifications (
            vaccine_name VARCHAR,
            vaers_name VARCHAR,
            symptom VARCHAR,
            classification VARCHAR,  -- 'confirmed' or 'not_confirmed'
            matched_pdf_event VARCHAR,  -- exact PDF adverse event quoted
            vaers_count INTEGER,
            total_vaers_reports INTEGER,
            pdf_adverse_events JSON
        )
        """)
        
        # Create symptom mapping/normalization table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS symptom_mappings (
            canonical_symptom VARCHAR,  -- standardized symptom name (PDF adverse event)
            vaers_symptom VARCHAR,      -- original VAERS symptom
            vaccine_name VARCHAR,       -- which vaccine this mapping is from
            vaers_count INTEGER,        -- how many times this VAERS symptom was reported
            mapping_confidence VARCHAR  -- 'exact_match', 'synonym', 'related'
        )
        """)
        
        # Clear existing data
        conn.execute("DELETE FROM strict_symptom_classifications")
        conn.execute("DELETE FROM symptom_mappings")
        
        # Insert data
        records = []
        for result in classifications:
            if not result['success']:
                continue
                
            vaccine_name = result['vaccine_name']
            vaers_name = result['vaers_name']
            total_reports = result['total_vaers_reports']
            pdf_events = json.dumps(result['pdf_adverse_events'])
            
            for classification_data in result['classifications']:
                records.append({
                    'vaccine_name': vaccine_name,
                    'vaers_name': vaers_name,
                    'symptom': classification_data['symptom'],
                    'classification': classification_data['classification'],
                    'matched_pdf_event': classification_data['matched_pdf_event'],
                    'vaers_count': classification_data['vaers_count'],
                    'total_vaers_reports': total_reports,
                    'pdf_adverse_events': pdf_events
                })
        
        # Insert main classification records
        if records:
            import pandas as pd
            records_df = pd.DataFrame(records)
            conn.execute("INSERT INTO strict_symptom_classifications SELECT * FROM records_df")
        
        # Create symptom mappings for confirmed symptoms
        mapping_records = []
        for result in classifications:
            if not result['success']:
                continue
                
            vaccine_name = result['vaccine_name']
            
            for classification_data in result['classifications']:
                if classification_data['classification'] == 'confirmed':
                    vaers_symptom = classification_data['symptom']
                    canonical_symptom = classification_data['matched_pdf_event']
                    vaers_count = classification_data['vaers_count']
                    
                    # Determine mapping confidence
                    if vaers_symptom.lower() == canonical_symptom.lower():
                        confidence = 'exact_match'
                    elif any(word in vaers_symptom.lower() for word in canonical_symptom.lower().split()):
                        confidence = 'synonym'
                    else:
                        confidence = 'related'
                    
                    mapping_records.append({
                        'canonical_symptom': canonical_symptom,
                        'vaers_symptom': vaers_symptom,
                        'vaccine_name': vaccine_name,
                        'vaers_count': vaers_count,
                        'mapping_confidence': confidence
                    })
        
        # Insert mapping records
        if mapping_records:
            mappings_df = pd.DataFrame(mapping_records)
            conn.execute("INSERT INTO symptom_mappings SELECT * FROM mappings_df")
        
        # Get summary stats
        summary = conn.execute("""
        SELECT 
            classification,
            COUNT(*) as symptom_count,
            COUNT(DISTINCT vaccine_name) as vaccine_count
        FROM strict_symptom_classifications
        GROUP BY classification
        """).fetchall()
        
        print(f"\nStrict Classification Summary:")
        for row in summary:
            print(f"  {row[0]}: {row[1]} symptoms across {row[2]} vaccines")
        
        # Show examples of confirmed matches
        confirmed_examples = conn.execute("""
        SELECT vaccine_name, symptom, matched_pdf_event, vaers_count
        FROM strict_symptom_classifications
        WHERE classification = 'confirmed'
        ORDER BY vaers_count DESC
        LIMIT 10
        """).fetchall()
        
        print(f"\nTop confirmed matches with PDF quotes:")
        for vaccine, symptom, matched_event, count in confirmed_examples:
            print(f"  {vaccine}: '{symptom}' ({count:,}) -> '{matched_event}'")
        
        conn.close()
        print(f"\nStrict database saved to: {self.output_db_path}")
        
        # Also save as JSON
        print(f"\nSaving JSON output...")
        
        # Save all classifications
        classifications_json = []
        for result in classifications:
            if result['success']:
                for c in result['classifications']:
                    classifications_json.append({
                        'vaccine_name': result['vaccine_name'],
                        'vaers_name': result['vaers_name'],
                        'symptom': c['symptom'],
                        'classification': c['classification'],
                        'matched_pdf_event': c['matched_pdf_event'],
                        'vaers_count': c.get('vaers_count', 0)
                    })
        
        with open(self.json_output_dir / "strict_symptom_classifications.json", 'w') as f:
            json.dump(classifications_json, f, indent=2)
        
        # Save mappings
        if mapping_records:
            with open(self.json_output_dir / "symptom_mappings_initial.json", 'w') as f:
                json.dump(mapping_records, f, indent=2)
        
        print(f"JSON files saved to: {self.json_output_dir}")
    
    def process_all_vaccines_strict(self, delay_between_calls: float = 0.5, min_symptom_count: int = 10, limit_vaccines: int = None):
        """Process all vaccines with strict classification"""
        print("=== STRICT SYMPTOM CLASSIFICATION WITH PDF QUOTES ===")
        
        # Get vaccine data
        vaccine_data = self.get_vaccine_data(limit=limit_vaccines)
        print(f"Found {len(vaccine_data)} vaccines to process")
        
        # Process each vaccine
        results = []
        for i, vaccine in enumerate(vaccine_data):
            if i > 0:
                print(f"Waiting {delay_between_calls}s between vaccines...")
                time.sleep(delay_between_calls)
            
            result = self.classify_symptoms_for_vaccine_strict(vaccine, min_symptom_count)
            results.append(result)
        
        # Show summary
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\n=== SUMMARY ===")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        
        if failed:
            print("\nFailed vaccines:")
            for f in failed:
                print(f"  {f['vaccine_name']}: {f['error']}")
        
        # Create database
        if successful:
            self.create_strict_classifications_database(successful)
            
            # Show sample results
            print(f"\n=== SAMPLE RESULTS ===")
            for result in successful[:2]:  # Show first 2
                vaccine_name = result['vaccine_name']
                classifications = result['classifications']
                confirmed = sum(1 for c in classifications if c['classification'] == 'confirmed')
                not_confirmed = sum(1 for c in classifications if c['classification'] == 'not_confirmed')
                
                print(f"\n{vaccine_name}:")
                print(f"  Confirmed in PDF: {confirmed}")
                print(f"  Not confirmed in PDF: {not_confirmed}")
                
                # Show confirmed examples with quotes
                confirmed_examples = [c for c in classifications if c['classification'] == 'confirmed'][:5]
                for ex in confirmed_examples:
                    print(f"    ✓ '{ex['symptom']}' -> '{ex['matched_pdf_event']}'")
        
        return results


def main():
    comparator = StrictSymptomComparator()
    results = comparator.process_all_vaccines_strict(
        delay_between_calls=0.5,  # Be respectful to API  
        min_symptom_count=10,     # Only classify symptoms with 10+ reports
        limit_vaccines=None       # Process ALL 16 vaccines
    )

if __name__ == "__main__":
    import pandas as pd
    main()