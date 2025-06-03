# VAERS Adverse Event Analysis System

## Quick Start for Frontend Developers

**Four main JSON files:**

1. **`json_data/fda_reports.json`** (48KB) - 33 vaccine entries with FDA adverse events from package inserts
2. **`json_data/vaers_subset.json`** (77MB) - 51,976 VAERS reports filtered to only FDA-matching vaccines
3. **`json_data/symptom_mappings.json`** (70KB) - 352 AI-powered mappings between VAERS and FDA terminology
4. **`json_data/vaers_categorization.json`** (21MB) - Categorizes each VAERS report by symptom matching status

### What's New: Report Categorization

We now categorize each VAERS report based on how well its symptoms match FDA documentation:
- **fully_matched** (0.04%) - ALL symptoms are in FDA package insert
- **not_mapped** (86.95%) - None of the symptoms have been processed yet
- **mapped_not_matched** (0.87%) - Symptoms are mapped but not in FDA list
- **Mixed categories** (12.14%) - Various combinations of the above

### Basic Usage Pattern
```javascript
// 1. Get a vaccine's official FDA adverse events
const fdaReports = await fetch('json_data/fda_reports.json').then(r => r.json());
const shingrix = fdaReports.find(v => v.vaccine_name === 'ZOSTER (SHINGRIX)');
console.log(shingrix.adverse_events); // ["pain", "redness", "swelling", ...]

// 2. Find VAERS reports for that vaccine
const vaersReports = await fetch('json_data/vaers_subset.json').then(r => r.json());
const shingrixReports = vaersReports.filter(report => 
  report.VAX_NAME_list.includes('ZOSTER (SHINGRIX)')
);

// 3. Check report categorization
const categorization = await fetch('json_data/vaers_categorization.json').then(r => r.json());
const reportCategory = categorization.reports.find(r => r.VAERS_ID === someId);
console.log(reportCategory.category); // e.g., "fully_matched_and_not_mapped"
```

## System Overview

Four datasets working together:
1. **FDA Reports**: Official adverse events from vaccine package inserts
2. **VAERS Subset**: Real-world reports filtered to only include FDA-matching vaccines
3. **Symptom Mappings**: AI crosswalk between VAERS terminology and FDA terminology
4. **Report Categorization**: Analysis of how well each report matches FDA documentation

## File Structures

### 1. FDA Reports - `json_data/fda_reports.json`
```javascript
{
  "vaccine_name": "ZOSTER (SHINGRIX)",  // VAERS-compatible name
  "vax_name": "SHINGRIX (ZOSTER VACCINE...)",  // Original FDA name
  "vax_manu": "GLAXOSMITHKLINE BIOLOGICALS",
  "adverse_events": ["pain", "redness", "swelling", "myalgia", "fatigue", ...],
  "vaers_vaccine_names": ["ZOSTER (SHINGRIX)"],  // All VAERS names that map here
  // ... more fields
}
```

### 2. VAERS Subset - `json_data/vaers_subset.json`
```javascript
{
  "VAERS_ID": 2547732,
  "AGE_YRS": 38.0,
  "SEX": "female",  // Mapped from M/F/U
  "DIED": false,    // Boolean (was Y/null)
  "L_THREAT": false,  // Boolean
  "ER_VISIT": false,  // Boolean
  "HOSPITAL": false,  // Boolean
  "DISABLE": false,   // Boolean
  "RECOVD": "yes",    // String: yes/no/unknown (was Y/N/U)
  "VAX_NAME_list": ["COVID19 (COVID19 (MODERNA BIVALENT))"],
  "symptom_list": ["Injury associated with device"],
  // ... more fields
}
```

### 3. Symptom Mappings - `json_data/symptom_mappings.json`
```javascript
{
  "vaers_symptom": "Injection site vasculitis",
  "fda_adverse_events": ["cellulitis", "erythema", "injection site reactions"]
}
```

### 4. Report Categorization - `json_data/vaers_categorization.json`
```javascript
{
  "metadata": { /* category definitions */ },
  "summary": {
    "total_reports": 51469,
    "category_counts": { /* counts by category */ },
    "category_percentages": { /* percentages */ }
  },
  "reports": [
    {
      "VAERS_ID": "2547732",
      "vaccine": "COVID19 (COVID19 (MODERNA))",
      "category": "fully_matched_and_not_mapped",
      "total_symptoms": 5,
      "symptom_breakdown": {
        "fully_matched": 1,
        "mapped_not_matched": 0,
        "not_mapped": 4
      }
    }
  ]
}
```

## Key Statistics

- **Vaccines**: 19 unique vaccines in VAERS subset (all match FDA reports)
- **Reports**: 51,976 VAERS reports (filtered from ~1.7M to only FDA-matching vaccines)
- **Symptom Mappings**: 352 VAERS symptoms mapped to FDA terminology
- **Match Rate**: Only 0.5% of symptom instances are FDA-documented (95.2% unmapped)

## Data Pipeline

1. **Extract FDA Data**: Parse adverse events from package insert PDFs
2. **Map Vaccine Names**: Create VAERS-compatible names for FDA vaccines
3. **Filter VAERS**: Keep only reports for vaccines in FDA list
4. **Map Symptoms**: Use Claude AI to map VAERS→FDA terminology
5. **Categorize Reports**: Analyze each report's symptom matching status

## Building the System

### Prerequisites
```bash
pip install pandas requests python-dotenv duckdb
export ANTHROPIC_API_KEY=your_key_here
```

### Key Scripts
- `fix_vaccine_mappings.py` - Maps FDA vaccine names to VAERS format
- `create_proper_vaers_subset.py` - Creates filtered VAERS subset
- `create_real_symptom_mappings.py` - AI-powered symptom mapping
- `create_vaers_categorization.py` - Categorizes reports by match status
- `database_fixed.py` - Loads data into DuckDB for analysis

### Build Process
```bash
# 1. Fix vaccine name mappings
python code/fix_vaccine_mappings.py

# 2. Create VAERS subset (only FDA-matching vaccines)
python code/create_proper_vaers_subset.py

# 3. Create symptom mappings (uses Claude AI)
python code/create_real_symptom_mappings.py

# 4. Analyze and categorize reports
python code/database_fixed.py
python code/create_vaers_categorization.py
```

## Analysis Tools

### DuckDB Database
We create a DuckDB database for efficient analysis:
```python
# Load all data into DuckDB
python code/database_fixed.py

# Get sample analysis
python code/sample_vaers_analysis.py
```

### Sample Output Categories
1. **Fully Matched**: Symptoms documented in FDA package insert
2. **Mapped but Not Matched**: Mapped to FDA terms but not in that vaccine's list
3. **Not Mapped**: Symptoms we haven't processed yet

## File Organization
```
hackathon/
├── README.md
├── code/                    # Processing scripts
├── json_data/              # Output JSON files (what you need!)
│   ├── fda_reports.json
│   ├── vaers_subset.json
│   ├── symptom_mappings.json
│   └── vaers_categorization.json
├── KEY_INFO/               # Data schemas
├── duckdb/                 # Analysis database
└── vaers_data/            # Raw VAERS CSVs (gitignored)
```

## Important Notes

1. **Vaccine Names**: We use VAERS naming convention (e.g., "ZOSTER (SHINGRIX)")
2. **Boolean Fields**: DIED, L_THREAT, ER_VISIT, HOSPITAL, DISABLE are now true/false
3. **Large Files**: Only vaers_subset.json uses Git LFS (77MB)
4. **Match Rate**: Low (0.5%) because most symptoms aren't mapped yet

## Next Steps

To improve the system:
1. Map more symptoms (currently only 352 of thousands)
2. Add more vaccines (currently 33 entries for 19 unique vaccines)
3. Improve mapping quality with better prompts
4. Add temporal analysis (dates are available)