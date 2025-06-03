# VAERS Adverse Event Analysis System

## Quick Start for Frontend Developers

**Three JSON files, that's it:**

1. **`json_data/fda_reports.json`** - 14 vaccines with their official FDA adverse events
2. **`json_data/vaers_subset.json`** - 100K real VAERS reports with patient data and symptoms  
3. **`json_data/symptom_mappings.json`** - AI mapping between VAERS terms and FDA terms

### Basic Usage Pattern
```javascript
// 1. Get a vaccine's official FDA adverse events
const fdaReports = await fetch('json_data/fda_reports.json').then(r => r.json());
const shingrix = fdaReports.find(v => v.vaccine_name === 'SHINGRIX');
console.log(shingrix.adverse_events); // ["headache", "fatigue", "injection site pain", ...]

// 2. Find VAERS reports for that vaccine
const vaersReports = await fetch('json_data/vaers_subset.json').then(r => r.json());
const shingrixReports = vaersReports.filter(report => 
  report.VAX_NAME_list.some(name => name.includes('SHINGRIX'))
);

// 3. Use AI mappings to find related symptoms
const mappings = await fetch('json_data/symptom_mappings.json').then(r => r.json());
const headacheMapping = mappings.find(m => m.vaers_symptom === 'Cephalgia');
console.log(headacheMapping.fda_adverse_events); // ["headache"] - maps to FDA term
```

## System Overview

Three core datasets for analyzing VAERS symptoms against FDA package insert adverse events:
1. **FDA Reports**: Adverse events extracted from 14 vaccine package inserts
2. **VAERS Subset**: 100,000 individual VAERS reports (2023-2024) with structured symptom data
3. **Symptom Mappings**: AI-powered crosswalk between VAERS symptoms and FDA adverse events

## File Structures (for frontend devs)

### 1. FDA Reports - `json_data/fda_reports.json` (~100KB)
```javascript
[
  {
    "vaccine_name": "SHINGRIX",
    "manufacturer": "GlaxoSmithKline",
    "adverse_events": ["headache", "fatigue", "muscle pain", "injection site pain"],
    "pdf_file": "shingrix_pi.pdf"
  },
  // ... 13 more vaccines
]
```

### 2. VAERS Subset - `json_data/vaers_subset.json` (~144MB)
```javascript
[
  {
    "VAERS_ID": 2696276,
    "AGE_YRS": 49.0,
    "SEX": "M",
    "STATE": "CO",
    "VAX_NAME_list": ["ZOSTER (SHINGRIX)"],
    "symptom_list": ["Product administered to patient of inappropriate age"],
    "DIED": null,
    "HOSPITAL": null,
    "ER_VISIT": null
    // ... more fields
  },
  // ... 99,999 more reports
]
```

### 3. Symptom Mappings - `json_data/symptom_mappings.json` (~500KB)
```javascript
[
  {
    "vaers_symptom": "Cephalgia",
    "fda_adverse_events": ["headache"]
  },
  {
    "vaers_symptom": "Injection site vasculitis", 
    "fda_adverse_events": ["cellulitis", "erythema", "injection site reactions"]
  },
  // ... 498 more mappings
]
```

## Common Frontend Patterns

### Get all vaccines
```javascript
const vaccines = fdaReports.map(v => v.vaccine_name);
// ["SHINGRIX", "GARDASIL", "ADACEL", ...]
```

### Filter reports by vaccine
```javascript
const covidReports = vaersReports.filter(r => 
  r.VAX_NAME_list.some(name => name.includes('COVID'))
);
```

### Filter reports by demographics
```javascript
const elderlyWomen = vaersReports.filter(r => 
  r.SEX === 'F' && r.AGE_YRS >= 65
);
```

### Check if symptom is FDA-documented
```javascript
function isSymptomDocumented(vaersSymptom, vaccineName) {
  // Find mapping
  const mapping = mappings.find(m => m.vaers_symptom === vaersSymptom);
  if (!mapping || mapping.fda_adverse_events.length === 0) return false;
  
  // Check if any mapped FDA events are in vaccine's official list
  const vaccine = fdaReports.find(v => v.vaccine_name === vaccineName);
  return mapping.fda_adverse_events.some(fdaEvent => 
    vaccine.adverse_events.includes(fdaEvent)
  );
}
```

### Get symptom statistics
```javascript
function getSymptomStats(vaccineName) {
  const reports = vaersReports.filter(r => 
    r.VAX_NAME_list.some(name => name.includes(vaccineName))
  );
  
  const symptomCounts = {};
  reports.forEach(r => {
    r.symptom_list.forEach(symptom => {
      symptomCounts[symptom] = (symptomCounts[symptom] || 0) + 1;
    });
  });
  
  return Object.entries(symptomCounts)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 10); // Top 10
}
```

## Available Vaccines (14 total)

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

### Find VAERS reports with specific symptoms
```javascript  
// Load VAERS reports
const reports = await loadJSON('vaers_subset.json');

// Find reports with headache for Shingrix
const headacheReports = reports.filter(r => 
  r.VAX_NAME_list.some(name => name.includes('SHINGRIX')) &&
  r.symptom_list.includes('Headache')
);
```

### Check FDA adverse events for a vaccine
```javascript
// Load FDA reports
const fdaReports = await loadJSON('fda_reports.json');
const shingrix = fdaReports.find(v => v.vaccine_name === 'SHINGRIX');
console.log(shingrix.adverse_events); // Official FDA adverse events
```

### Map VAERS symptoms to FDA events
```javascript
// Load symptom mappings
const mappings = await loadJSON('symptom_mappings.json');

// Find what FDA events "headache" maps to
const headacheMapping = mappings.find(m => 
  m.vaers_symptom.toLowerCase() === 'headache'
);
console.log(headacheMapping.fda_adverse_events); // ["headache", "cephalgia"]
```

## Building the System

### Requirements
- Python 3.8+
- pandas, requests
- Anthropic API key for Claude AI mapping
- VAERS data files (2023-2024) in `vaers_data/vaers_data/`

### Build Process
```bash
cd code
./build_complete_system.sh
```

This will:
1. Extract 100K VAERS reports from 2023-2024 CSV files
2. Create symptom mappings using Claude AI (~10-15 minutes for 500 symptoms)
3. Generate the 3 core JSON files

### Build Output
- **Total processing time**: ~15 minutes
- **JSON files**: 3 files in `json_data/` ready for analysis

## Linking the Datasets

The three JSON files are designed to work together:

### 1. Find relevant symptoms for a vaccine
```javascript
// Get FDA-documented symptoms for a vaccine
const fdaReports = await loadJSON('fda_reports.json');
const vaccine = fdaReports.find(v => v.vaccine_name === 'SHINGRIX');
const fdaSymptoms = vaccine.adverse_events; // ["headache", "fatigue", ...]
```

### 2. Find VAERS reports with those symptoms  
```javascript
// Get VAERS reports with those symptoms
const vaersReports = await loadJSON('vaers_subset.json');
const matchingReports = vaersReports.filter(report => 
  report.VAX_NAME_list.some(name => name.includes('SHINGRIX')) &&
  report.symptom_list.some(symptom => 
    fdaSymptoms.includes(symptom) // Direct match
  )
);
```

### 3. Use mappings for fuzzy matching
```javascript
// Use AI mappings for broader symptom matching
const mappings = await loadJSON('symptom_mappings.json');

// Find all VAERS symptoms that map to FDA "headache"
const headacheMappings = mappings.filter(m => 
  m.fda_adverse_events.includes('headache')
);
const vaersHeadacheTerms = headacheMappings.map(m => m.vaers_symptom);

// Now find reports with any of these VAERS terms
const broadMatchingReports = vaersReports.filter(report =>
  report.symptom_list.some(symptom => 
    vaersHeadacheTerms.includes(symptom)
  )
);
```

### 4. Cross-reference analysis
```javascript
// Complete analysis: FDA events -> VAERS symptoms -> Reports
function analyzeVaccineSymptoms(vaccineName) {
  // 1. Get FDA documented symptoms
  const vaccine = fdaReports.find(v => v.vaccine_name === vaccineName);
  const fdaEvents = vaccine.adverse_events;
  
  // 2. Find VAERS symptoms that map to FDA events
  const relevantMappings = mappings.filter(m => 
    m.fda_adverse_events.some(event => fdaEvents.includes(event))
  );
  const vaersSymptoms = relevantMappings.map(m => m.vaers_symptom);
  
  // 3. Find VAERS reports with those symptoms
  const reports = vaersReports.filter(r => 
    r.VAX_NAME_list.some(name => name.includes(vaccineName)) &&
    r.symptom_list.some(symptom => vaersSymptoms.includes(symptom))
  );
  
  return {
    fdaEvents,
    vaersSymptoms,
    reportCount: reports.length,
    reports
  };
}
```

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