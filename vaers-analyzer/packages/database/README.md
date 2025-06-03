# VAERS Database Package

## Schema Overview

The database schema has been updated to match the actual VAERS data format:

### Tables

1. **vaers_reports** - Core report information
   - Includes outcome flags: died, l_threat, er_visit, hospital, disable
   - Patient demographics: age, sex, state
   - Dates: recv_date, vax_date, onset_date
   - Free text: symptom_text

2. **vaers_vaccines** - Vaccines administered (one-to-many with reports)
   - Supports multiple vaccines per report
   - Stores: vax_type, vax_manufacturer, vax_name, dose_series, route, site

3. **vaers_symptoms** - Structured symptoms (one-to-many with reports)
   - MedDRA preferred terms
   - Severity and validation status
   - FDA reference links

4. **symptom_analogies** - AI-powered symptom similarity matching
   - Links similar symptoms across reports
   - Similarity scores (0-1 scale)

## Data Import

Use the data import utilities to convert raw VAERS data:

```typescript
import { 
  importVaersData,
  VaersReportRepository,
  VaersVaccineRepository,
  VaersSymptomRepository 
} from '@vaers/database';

// Example usage
const reportRepo = new VaersReportRepository();
const vaccineRepo = new VaersVaccineRepository();
const symptomRepo = new VaersSymptomRepository();

const rawData = [
  {
    VAERS_ID: "2729674",
    RECVDATE: "01/03/2024",
    STATE: "CA",
    AGE_YRS: 1.17,
    // ... other fields
    VAX_TYPE_list: ["COVID19"],
    VAX_MANU_list: ["MODERNA"],
    symptom_list: ["Incorrect dose administered"]
  }
];

const result = await importVaersData(
  rawData,
  reportRepo,
  vaccineRepo,
  symptomRepo
);

console.log(`Imported ${result.imported} reports`);
console.log(`Errors: ${result.errors}`);
```

## Migrations

Run the migration to update your database schema:

```bash
psql -U your_user -d your_database -f src/migrations/001_update_vaers_schema.sql
```

**WARNING**: This migration will drop existing tables. Backup your data first!