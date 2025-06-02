import os
from pathlib import Path
from typing import Optional, Dict, List, Union
import time
import json
import duckdb

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
import fitz  # PyMuPDF


class VaccineAdverseData(BaseModel):
    vax_name: str  # Commercial brand name (e.g., "DENGVAXIA", "GARDASIL")
    vax_type: Optional[str]  # CDC abbreviation (e.g., "COVID19", "FLU3", "HEPB")
    vax_manu: Optional[str]  # Manufacturer name
    controlled_trial_text: str
    symptoms_list: List[str]
    study_type: Optional[str]
    source_section: Optional[str]
    full_pdf_text: str


class PDFVaccineExtractor:
    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"
    DEFAULT_MODEL = "claude-3-haiku-20240307"
    DEFAULT_MAX_TOKENS = 2048

    def __init__(self, api_key: Optional[str] = None, db_path: str = "../intermediate_results/vaers_database.duckdb"):
        load_dotenv()
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set ANTHROPIC_API_KEY or pass api_key parameter.")
        
        # Connect to DuckDB
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self._create_pdf_extraction_table()

    def _create_pdf_extraction_table(self):
        """Create table for PDF extraction results if it doesn't exist"""
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS pdf_vaccine_extractions (
            filename VARCHAR PRIMARY KEY,
            vax_name VARCHAR,
            vax_type VARCHAR,
            vax_manu VARCHAR,
            controlled_trial_text TEXT,
            symptoms_list TEXT,  -- JSON array as string
            study_type VARCHAR,
            source_section VARCHAR,
            full_pdf_text TEXT,
            extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN,
            error_message VARCHAR
        )
        """)
        print("✓ PDF extraction table ready in DuckDB")

    def extract_text_from_pdf(self, pdf_path: Union[str, Path]) -> str:
        """Extract text from PDF using PyMuPDF"""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise ValueError(f"PDF file not found: {pdf_path}")
        
        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            raise ValueError(f"Error reading PDF {pdf_path}: {e}")
        
        return text

    def extract_vaccine_and_adverse_data(
        self,
        text: str,
        filename: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, any]:
        """Extract vaccine info and adverse reaction data from PDF text"""
        
        prompt = (
            "Extract vaccine information and adverse reaction data from this pharmaceutical package insert.\n\n"
            "First, identify the vaccine using VAERS database format:\n"
            "- vax_name: The full vaccine name including brand name and description\n"
            "- vax_type: CDC vaccine type abbreviation\n"
            "- vax_manu: Manufacturer name\n\n"
            "IMPORTANT FORMAT EXAMPLES from VAERS:\n"
            "vax_type: DTP, vax_manu: CONNAUGHT LABORATORIES, vax_name: DTP (NO BRAND NAME)\n"
            "vax_type: DTP, vax_manu: LEDERLE LABORATORIES, vax_name: DTP (TRI-IMMUNOL)\n"
            "vax_type: OPV, vax_manu: PFIZER\\WYETH, vax_name: POLIO VIRUS, ORAL (ORIMUNE)\n"
            "vax_type: TD, vax_manu: LEDERLE LABORATORIES, vax_name: TD ADSORBED (NO BRAND NAME)\n"
            "vax_type: MMR, vax_manu: UNKNOWN MANUFACTURER, vax_name: MEASLES + MUMPS + RUBELLA (NO BRAND NAME)\n"
            "vax_type: COVID19, vax_manu: PFIZER\\BIONTECH, vax_name: COVID19 (COVID19 (PFIZER-BIONTECH))\n"
            "vax_type: FLU3, vax_manu: GLAXOSMITHKLINE BIOLOGICALS, vax_name: INFLUENZA (FLUARIX)\n"
            "vax_type: HEPB, vax_manu: MERCK & CO. INC., vax_name: HEPATITIS B (RECOMBIVAX HB)\n\n"
            "Common vaccine type codes:\n"
            "- DTP/DTAP: Diphtheria, Tetanus, Pertussis\n"
            "- OPV/IPV: Polio vaccines\n"
            "- MMR: Measles, Mumps, Rubella\n"
            "- HEPB/HEPA: Hepatitis vaccines\n"
            "- FLU3/FLU4: Influenza vaccines\n"
            "- COVID19: COVID-19 vaccines\n"
            "- HPV4/HPV9: HPV vaccines\n"
            "- VAR: Varicella (chickenpox)\n"
            "- ZOSTER: Shingles vaccine\n"
            "- HIBV: Haemophilus influenzae type b\n\n"
            "For vax_name format:\n"
            "- If brand name exists: VACCINE TYPE (BRAND NAME)\n"
            "- If no brand name: VACCINE TYPE (NO BRAND NAME)\n"
            "- Use uppercase for entire name\n"
            "- Include full description like 'POLIO VIRUS, ORAL' not just 'POLIO'\n\n"
            "Then extract adverse reaction information ONLY from CONTROLLED CLINICAL TRIALS, SOLICITED ADVERSE REACTIONS, "
            "or other CONTROLLED STUDIES. DO NOT include information from:\n"
            "- VAERS data\n"
            "- Unsolicited adverse events\n"
            "- Post-marketing surveillance\n"
            "- Spontaneous reports\n\n"
            "Return a JSON object with:\n"
            "{\n"
            "  \"vax_name\": \"full vaccine name in VAERS format (uppercase)\",\n"
            "  \"vax_type\": \"CDC abbreviation in uppercase\",\n"
            "  \"vax_manu\": \"manufacturer name in uppercase\",\n"
            "  \"controlled_trial_text\": \"Direct quote of text related to adverse reactions from controlled trials\",\n"
            "  \"symptoms_list\": [\"list of specific symptoms/adverse reactions mentioned\"],\n"
            "  \"study_type\": \"type of controlled study\",\n"
            "  \"source_section\": \"section name where this information was found\"\n"
            "}\n\n"
            "If unable to determine, use 'UNKNOWN MANUFACTURER' for vax_manu.\n\n"
            f"Document text:\n{text[:10000]}\n\n"  # Limit text to avoid token limits
            "Respond ONLY with the JSON object."
        )

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

            parsed_json = json.loads(raw_text)
            # Add the full PDF text
            parsed_json["full_pdf_text"] = text
            structured_data = VaccineAdverseData(**parsed_json)
            
            return {
                "filename": filename,
                "success": True,
                "data": structured_data.model_dump(),
                "raw_response": raw_text
            }
        except (json.JSONDecodeError, ValidationError, requests.RequestException) as e:
            return {
                "filename": filename,
                "success": False,
                "error": str(e),
                "raw_response": raw_text if 'raw_text' in locals() else None
            }

    def save_to_duckdb(self, result: Dict[str, any]):
        """Save extraction result to DuckDB"""
        if result["success"]:
            data = result["data"]
            self.conn.execute("""
            INSERT OR REPLACE INTO pdf_vaccine_extractions 
            (filename, vax_name, vax_type, vax_manu, controlled_trial_text, 
             symptoms_list, study_type, source_section, full_pdf_text, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """, [
                result["filename"],
                data["vax_name"],
                data["vax_type"],
                data["vax_manu"],
                data["controlled_trial_text"],
                json.dumps(data["symptoms_list"]),  # Store as JSON string
                data["study_type"],
                data["source_section"],
                data["full_pdf_text"],
                True
            ])
        else:
            self.conn.execute("""
            INSERT OR REPLACE INTO pdf_vaccine_extractions 
            (filename, success, error_message)
            VALUES (?, ?, ?)
            """, [
                result["filename"],
                False,
                result.get("error", "Unknown error")
            ])

    def process_pdf_folder(
        self,
        folder_path: Union[str, Path],
        delay_between_calls: float = 1.0,
        max_files: Optional[int] = None
    ) -> Dict[str, int]:
        """Process all PDFs in a folder and save to DuckDB"""
        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            raise ValueError(f"Invalid folder path: {folder_path}")

        pdf_files = list(folder_path.glob("*.pdf"))
        if max_files:
            pdf_files = pdf_files[:max_files]

        successful = 0
        failed = 0

        for i, pdf_file in enumerate(pdf_files):
            if i > 0:
                time.sleep(delay_between_calls)

            print(f"Processing {pdf_file.name} ({i+1}/{len(pdf_files)})...")

            try:
                # Extract text from PDF
                text = self.extract_text_from_pdf(pdf_file)
                
                if not text.strip():
                    result = {
                        "filename": pdf_file.name,
                        "success": False,
                        "error": "No text extracted from PDF"
                    }
                    self.save_to_duckdb(result)
                    failed += 1
                    print(f"✗ No text found in {pdf_file.name}")
                    continue

                # Extract vaccine and adverse reactions
                result = self.extract_vaccine_and_adverse_data(text, pdf_file.name)
                self.save_to_duckdb(result)
                
                if result["success"]:
                    successful += 1
                    vax_name = result["data"]["vax_name"]
                    print(f"✓ Processed {pdf_file.name} - Vaccine: {vax_name}")
                else:
                    failed += 1
                    print(f"✗ Failed {pdf_file.name}: {result.get('error', 'Unknown error')}")

            except Exception as e:
                result = {
                    "filename": pdf_file.name,
                    "success": False,
                    "error": str(e)
                }
                self.save_to_duckdb(result)
                failed += 1
                print(f"✗ Error processing {pdf_file.name}: {e}")

        return {"successful": successful, "failed": failed}

    def create_vaccine_mapping_view(self):
        """Create a view to map vaccines between VAERS and PDF data"""
        # Check if all_vax table exists
        table_check = self.conn.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = 'all_vax'
        """).fetchone()
        
        if table_check[0] == 0:
            print("⚠ Warning: all_vax table not found. Run vaers_parser.py first to create VAERS database.")
            print("  Skipping vaccine mapping view creation.")
            return False
        
        self.conn.execute("""
        CREATE OR REPLACE VIEW vaccine_pdf_mapping AS
        SELECT DISTINCT
            v.VAX_NAME as vaers_vax_name,
            v.VAX_TYPE as vaers_vax_type,
            p.vax_name as pdf_vax_name,
            p.vax_type as pdf_vax_type,
            p.filename as pdf_filename,
            p.vax_manu as pdf_manufacturer
        FROM all_vax v
        LEFT JOIN pdf_vaccine_extractions p 
            ON UPPER(TRIM(v.VAX_NAME)) = UPPER(TRIM(p.vax_name))
            OR UPPER(TRIM(v.VAX_TYPE)) = UPPER(TRIM(p.vax_type))
        WHERE v.VAX_NAME IS NOT NULL
        ORDER BY v.VAX_NAME
        """)
        print("✓ Created vaccine_pdf_mapping view")
        return True

    def get_extraction_summary(self) -> Dict:
        """Get summary of extraction results"""
        summary = self.conn.execute("""
        SELECT 
            COUNT(*) as total_pdfs,
            SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
            SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failed,
            COUNT(DISTINCT vax_name) as unique_vaccines
        FROM pdf_vaccine_extractions
        """).fetchone()
        
        return {
            "total_pdfs": summary[0],
            "successful": summary[1],
            "failed": summary[2],
            "unique_vaccines": summary[3]
        }

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    try:
        extractor = PDFVaccineExtractor()

        # Process PDFs in data folder
        results = extractor.process_pdf_folder(
            folder_path="../data",
            delay_between_calls=1.5,
            max_files=5  # Process first 5 for testing
        )

        # Create mapping view
        mapping_created = extractor.create_vaccine_mapping_view()

        # Get and print summary
        summary = extractor.get_extraction_summary()
        print(f"\nProcessing complete:")
        print(f"✓ Total PDFs: {summary['total_pdfs']}")
        print(f"✓ Successful: {summary['successful']}")
        print(f"✗ Failed: {summary['failed']}")
        print(f"✓ Unique vaccines identified: {summary['unique_vaccines']}")

        # Show sample mappings if view was created
        if mapping_created:
            print("\nSample vaccine mappings:")
            mappings = extractor.conn.execute("""
            SELECT vaers_vax_name, pdf_vax_name, pdf_filename
            FROM vaccine_pdf_mapping
            WHERE pdf_vax_name IS NOT NULL
            LIMIT 5
            """).fetchall()
            
            for vaers_name, pdf_name, filename in mappings:
                print(f"  VAERS: {vaers_name} -> PDF: {pdf_name} ({filename}")
        else:
            # Show extracted vaccine names instead
            print("\nExtracted vaccine names:")
            extracted = extractor.conn.execute("""
            SELECT vax_name, vax_type, vax_manu, filename
            FROM pdf_vaccine_extractions
            WHERE success = true
            LIMIT 5
            """).fetchall()
            
            for vax_name, vax_type, vax_manu, filename in extracted:
                print(f"  {vax_type}: {vax_name} by {vax_manu} ({filename})")

        extractor.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()