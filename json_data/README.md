# JSON Data for VAERS Analysis Frontend

This folder contains all the data needed for the VAERS adverse event analysis frontend in JSON format.

## Quick Start

The main files you'll need are:
1. `vaccines.json` - List of 16 vaccines with their VAERS and PDF names
2. `symptom_classifications_full.json` - Which symptoms are confirmed in PDFs
3. `canonical_symptoms.json` - Normalized symptom names across vaccines

## File Descriptions

### Core Data Files

#### `vaccines.json`
Master list of 16 crosswalked vaccines.
```json
{
  "vaccine_id": 1,
  "vaers_name": "COVID19 (COVID19 (MODERNA))",
  "pdf_name": "COVID19 (SPIKEVAX)",
  "total_vaers_reports": 606035,
  "pdf_adverse_events": ["headache", "fatigue", ...]
}
```

#### `symptom_classifications_full.json`
LLM-validated classifications showing which VAERS symptoms match PDF documentation.
```json
{
  "vaccine_id": 1,
  "symptom": "Headache",
  "classification": "confirmed",
  "vaers_count": 1234,
  "vaccine_name": "COVID19 (COVID19 (MODERNA))",
  "pdf_name": "COVID19 (SPIKEVAX)"
}
```

#### `canonical_symptoms.json`
Normalized symptom lookup across all vaccines.
```json
{
  "canonical_symptom": "headache",
  "total_vaers_reports": 5898,
  "vaccine_count": 3,
  "most_common_vaers_form": "Headache",
  "example_vaccines": ["SHINGRIX", "COVID19"]
}
```

### Supporting Data Files

- `vaccine_comparisons.json` - Detailed comparison data with symptom counts
- `vaccine_symptom_counts.json` - Simplified symptom frequency data
- `symptom_mappings_final.json` - Maps VAERS symptoms to PDF adverse events
- `pdf_extraction_results.json` - Raw extracted text from FDA package inserts
- `database_summary.json` - Overall statistics

## Common Use Cases

### 1. Check if a symptom is documented in PDF
```javascript
// Load symptom_classifications_full.json
const classifications = await loadJSON('symptom_classifications_full.json');

// Find if "headache" is confirmed for Moderna
const isConfirmed = classifications.find(c => 
  c.vaccine_name.includes('MODERNA') && 
  c.symptom.toLowerCase() === 'headache' &&
  c.classification === 'confirmed'
);
```

### 2. Get all symptoms for a vaccine
```javascript
// Load vaccines.json for PDF adverse events
const vaccines = await loadJSON('vaccines.json');
const moderna = vaccines.find(v => v.vaers_name.includes('MODERNA'));
console.log(moderna.pdf_adverse_events); // All documented symptoms
```

### 3. Find symptom variations
```javascript
// Load canonical_symptoms.json
const canonical = await loadJSON('canonical_symptoms.json');
const headacheData = canonical.find(s => s.canonical_symptom === 'headache');
console.log(headacheData.most_common_vaers_form); // "Headache"
console.log(headacheData.total_vaers_reports); // 5898
```

## Data Pipeline

1. **Raw Data**: VAERS CSV files + FDA PDF package inserts
2. **Processing**: Python scripts extract and crosswalk vaccine names
3. **LLM Validation**: AI validates which symptoms match PDF documentation
4. **Output**: These JSON files for frontend consumption

## Notes

- All files are generated fresh when the pipeline runs
- Symptom counts are from VAERS reports 2020-2024
- Only includes 16 vaccines that could be matched between VAERS and PDFs
- The `classification` field is either "confirmed" (found in PDF) or "not_confirmed"

## Questions?

Check the `manifest.json` file for complete file descriptions and statistics.