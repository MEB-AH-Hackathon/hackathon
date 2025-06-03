# VAERS Adverse Event Analysis System

This system analyzes VAERS (Vaccine Adverse Event Reporting System) data against FDA package inserts to identify which reported symptoms are documented in official vaccine literature.

## Overview

The system processes VAERS adverse event reports and cross-references them with FDA package insert data to determine:
- Which symptoms reported in VAERS are documented in official vaccine literature
- Frequency of symptoms across different vaccines  
- Individual-level VAERS reports for detailed analysis
- Normalized symptom mappings for finding similar reports

## Key Statistics

- **14 crosswalked vaccines** between VAERS and FDA package inserts
- **1M+ individual VAERS reports** with structured symptom data (2020-2024)
- **Validated symptom classifications** using LLM analysis with PDF quotes
- **Symptom normalization** for finding similar reports across different wordings

## Data Structure

### Input Data
- **VAERS CSV files**: Raw adverse event reports from FDA (2020-2024)
- **FDA Package Inserts**: 34 PDF documents with adverse event information
- **Vaccine Name Crosswalk**: Manual mapping between VAERS and PDF vaccine names

### Output Formats
- **DuckDB databases**: For complex queries and analysis (`duckdb_data/`)
- **JSON files**: For web frontend consumption (`json_data/`)

## Available Data Files

### JSON Data (`json_data/`)

#### Core Dataset Files
- `vaccine_comparisons.json` - Complete vaccine comparison data with symptom counts
- `vaccine_symptom_counts.json` - Symptom frequencies for each crosswalked vaccine
- `pdf_extraction_results.json` - Raw adverse events extracted from FDA PDFs

#### VAERS Report Files  
- `vaers_reports_sample_1k.json` - 1,000 random VAERS reports
- `vaers_reports_sample_10k.json` - 10,000 random VAERS reports  
- `vaers_reports_sample_100k.json` - 100,000 random VAERS reports
- Each report includes: vaccine name, patient demographics, symptoms, dates

#### Symptom Analysis Files  
- `strict_symptom_classifications.json` - LLM-validated symptom classifications
- `symptom_mappings_initial.json` - Maps VAERS symptoms to PDF adverse events
- Additional files generated during build process

#### Reference Files
- `pdf_vaccine_names_only.json` - Mapping between PDF filenames and vaccine names
- `manifest.json` - Complete file descriptions and metadata

### DuckDB Data (`duckdb_data/`)
- `vaccine_comparison.duckdb` - Aggregate vaccine and symptom data
- `unified_vaers_analysis.duckdb` - Complete database with individual reports
- `strict_symptom_classifications.duckdb` - LLM validation results

### Schemas (`KEY_INFO/`)
- `system_overview.json` - High-level system architecture and capabilities
- `json_data_schema.json` - Schema for all JSON output files  
- `unified_database_schema.json` - Schema for main DuckDB database
- `vaers_merged_schema.json` - Schema for VAERS data structure

## 14 Crosswalked Vaccines

1. **COVID19 (COVID19 (PFIZER-BIONTECH))** → COVID19 (COVID19 (MNEXSPIKE))
2. **ZOSTER (SHINGRIX)** → SHINGRIX (ZOSTER VACCINE RECOMBINANT, ADJUVANTED)  
3. **HPV (GARDASIL)** → HUMAN PAPILLOMAVIRUS QUADRIVALENT (GARDASIL)
4. **ZOSTER LIVE (ZOSTAVAX)** → ZOSTER VACCINE LIVE (ZOSTAVAX)
5. **TDAP (ADACEL)** → TETANUS TOXOID, REDUCED DIPHTHERIA TOXOID AND ACELLULAR PERTUSSIS VACCINE ADSORBED (ADACEL)
6. **HEP A (HAVRIX)** → HEPATITIS A (HAVRIX)
7. **DTAP (INFANRIX)** → DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS (INFANRIX)
8. **ROTAVIRUS (ROTARIX)** → ROTARIX (ROTAVIRUS VACCINE, LIVE, ORAL)
9. **DTAP (DAPTACEL)** → DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS VACCINE ADSORBED (DAPTACEL)
10. **DTAP + HEPB + IPV (PEDIARIX)** → DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS ADSORBED, HEPATITIS B (RECOMBINANT) AND INACTIVATED POLIOVIRUS VACCINE (PEDIARIX)
11. **DTAP + IPV (KINRIX)** → DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS ADSORBED AND INACTIVATED POLIOVIRUS VACCINE (KINRIX)
12. **DTAP + IPV + HIB (PENTACEL)** → DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS ADSORBED, INACTIVATED POLIOVIRUS AND HAEMOPHILUS B CONJUGATE (TETANUS TOXOID CONJUGATE) VACCINE (PENTACEL)
13. **YELLOW FEVER (YF-VAX)** → YELLOW FEVER (YF-VAX)
14. **TYPHOID VI POLYSACCHARIDE (TYPHIM VI)** → TYPHOID VI POLYSACCHARIDE VACCINE (TYPHIM VI)

## Usage Examples

### Check if a symptom is documented in FDA package insert
```javascript
// Load symptom classifications
const classifications = await loadJSON('strict_symptom_classifications.json');

// Find if "headache" is confirmed for Shingrix
const isConfirmed = classifications.find(c => 
  c.vaccine_name.includes('SHINGRIX') && 
  c.symptom.toLowerCase() === 'headache' &&
  c.classification === 'confirmed'
);
```

### Get symptom counts for a vaccine
```javascript
// Load vaccine symptom data
const symptomCounts = await loadJSON('vaccine_symptom_counts.json');
const shingrixData = symptomCounts['ZOSTER (SHINGRIX)'];
console.log(shingrixData.symptom_counts); // All VAERS symptoms with counts
```

### Find VAERS reports with specific symptoms
```javascript  
// Load VAERS reports
const reports = await loadJSON('vaers_reports_sample_10k.json');

// Find reports with headache for Shingrix
const headacheReports = reports.filter(r => 
  r.vaccine_name.includes('SHINGRIX') &&
  r.symptoms.includes('Headache')
);
```

## Building the System

### Requirements
- Python 3.8+
- DuckDB, pandas, requests
- Anthropic API key for LLM classification  
- VAERS data files (2020-2024) in `vaers_data/vaers_data/`

### Build Process
```bash
cd code
./build_complete_system.sh
```

This will:
1. Process VAERS data for crosswalked vaccines only
2. Run LLM validation of symptom classifications (~4 minutes)
3. Build unified database with individual reports
4. Create symptom normalization tables
5. Export everything to JSON format

### Build Output
- **Total processing time**: ~30 minutes (includes processing 1M+ VAERS reports)
- **DuckDB databases**: `duckdb_data/` (for analysis)
- **JSON files**: `json_data/` (for frontend)
- **Individual scripts**: Can be run separately if needed

## Data Processing Pipeline

1. **Raw Data**: VAERS CSV files + FDA PDF package inserts
2. **Vaccine Crosswalk**: Map names between VAERS and PDFs (14 successful matches)
3. **Symptom Extraction**: Parse individual symptoms from VAERS reports
4. **LLM Classification**: Validate which symptoms appear in package inserts using Claude AI
5. **Normalization**: Create symptom mappings for cross-vaccine analysis
6. **Export**: Generate JSON files for frontend consumption

## File Structure
```
hackathon/
├── README.md                    # This file
├── code/                        # Python processing scripts
├── json_data/                   # JSON output for frontend
├── duckdb_data/                 # DuckDB databases for analysis  
├── KEY_INFO/                    # Data schemas and documentation
└── vaers_data/                  # Raw VAERS CSV files (not in repo)
```

## Demo Use Cases

### Input: New VAERS-like report
```json
{
  "vaccine": "ZOSTER (SHINGRIX)",
  "symptoms": ["headache", "fatigue", "injection site pain"],
  "age": 65,
  "sex": "F"
}
```

### Output: Analysis
- **Confirmed in package insert**: headache ✓, fatigue ✓, injection site pain ✓
- **All symptoms documented**: Yes, all symptoms are in FDA package insert
- **Similar reports**: 2,847 other Shingrix reports with headache + fatigue
- **Risk context**: 5.8% of Shingrix recipients report this combination

## Data Sources
- **VAERS**: https://vaers.hhs.gov/data.html
- **FDA Package Inserts**: https://www.fda.gov/vaccines-blood-biologics/
- **Crosswalk**: Manual mapping of 14 vaccine name matches verified by LLM analysis

## Validation
- LLM classifications require exact PDF quotes to minimize false positives
- Symptom mappings validated against source documents
- False positives automatically filtered out during processing