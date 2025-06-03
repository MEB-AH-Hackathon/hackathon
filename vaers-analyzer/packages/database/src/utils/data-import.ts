import type { VaersRawData } from '@vaers/types';
import type { NewVaersReportRecord } from '../schema/vaers-reports';
import type { NewVaersVaccineRecord } from '../schema/vaers-vaccines';
import type { NewVaersSymptomRecord } from '../schema/vaers-symptoms';

/**
 * Parse date string in MM/DD/YYYY format to Date object
 */
export function parseVaersDate(dateStr: string | null | undefined): Date | null {
  if (!dateStr) return null;
  
  // Handle MM/DD/YYYY format
  const parts = dateStr.split('/');
  if (parts.length !== 3) return null;
  
  const month = parseInt(parts[0], 10);
  const day = parseInt(parts[1], 10);
  const year = parseInt(parts[2], 10);
  
  if (isNaN(month) || isNaN(day) || isNaN(year)) return null;
  
  // JavaScript Date uses 0-based months
  return new Date(year, month - 1, day);
}

/**
 * Convert Y/N/U string to boolean or null
 */
export function parseYesNo(value: string | null | undefined): boolean | null {
  if (value === 'Y') return true;
  if (value === 'N') return false;
  return null;
}

/**
 * Convert raw VAERS data to database report record
 */
export function convertToReportRecord(raw: VaersRawData): Omit<NewVaersReportRecord, 'id'> {
  return {
    vaersId: String(raw.VAERS_ID),
    recvDate: parseVaersDate(raw.RECVDATE),
    state: raw.STATE || null,
    ageYrs: raw.AGE_YRS !== null && !isNaN(Number(raw.AGE_YRS)) ? String(raw.AGE_YRS) : null,
    sex: (raw.SEX === 'F' || raw.SEX === 'M' || raw.SEX === 'U') ? raw.SEX : null,
    symptomText: raw.SYMPTOM_TEXT || null,
    died: parseYesNo(raw.DIED),
    lThreat: parseYesNo(raw.L_THREAT),
    erVisit: parseYesNo(raw.ER_VISIT),
    hospital: parseYesNo(raw.HOSPITAL),
    disable: parseYesNo(raw.DISABLE),
    recovd: (raw.RECOVD === 'Y' || raw.RECOVD === 'N' || raw.RECOVD === 'U') ? raw.RECOVD : null,
    vaxDate: parseVaersDate(raw.VAX_DATE),
    onsetDate: parseVaersDate(raw.ONSET_DATE),
    numDays: raw.NUMDAYS !== null && !isNaN(Number(raw.NUMDAYS)) ? Number(raw.NUMDAYS) : null,
    status: 'new'
  };
}

/**
 * Convert raw VAERS data to vaccine records
 */
export function convertToVaccineRecords(raw: VaersRawData, reportId: number): NewVaersVaccineRecord[] {
  const vaccines: NewVaersVaccineRecord[] = [];
  
  const vaxTypes = raw.VAX_TYPE_list || [];
  const vaxManus = raw.VAX_MANU_list || [];
  const vaxNames = raw.VAX_NAME_list || [];
  const vaxDoses = raw.VAX_DOSE_SERIES_list || [];
  const vaxRoutes = raw.VAX_ROUTE_list || [];
  const vaxSites = raw.VAX_SITE_list || [];
  
  // Create vaccine records based on the longest array
  const maxLength = Math.max(
    vaxTypes.length,
    vaxManus.length,
    vaxNames.length,
    vaxDoses.length,
    vaxRoutes.length,
    vaxSites.length
  );
  
  for (let i = 0; i < maxLength; i++) {
    vaccines.push({
      reportId,
      vaxType: vaxTypes[i] || null,
      vaxManufacturer: vaxManus[i] || null,
      vaxName: vaxNames[i] || null,
      vaxDoseSeries: vaxDoses[i] || null,
      vaxRoute: vaxRoutes[i] || null,
      vaxSite: vaxSites[i] || null
    });
  }
  
  return vaccines;
}

/**
 * Convert raw VAERS data to symptom records
 */
export function convertToSymptomRecords(raw: VaersRawData, reportId: number): NewVaersSymptomRecord[] {
  const symptoms: NewVaersSymptomRecord[] = [];
  
  if (raw.symptom_list && Array.isArray(raw.symptom_list)) {
    for (const symptomName of raw.symptom_list) {
      if (symptomName && typeof symptomName === 'string') {
        symptoms.push({
          reportId,
          symptomName,
          validationStatus: 'unvalidated'
        });
      }
    }
  }
  
  return symptoms;
}

/**
 * Import a batch of raw VAERS data
 */
export async function importVaersData(
  rawData: VaersRawData[],
  reportRepo: any,
  vaccineRepo: any,
  symptomRepo: any
): Promise<{ imported: number; errors: string[] }> {
  let imported = 0;
  const errors: string[] = [];
  
  for (const raw of rawData) {
    try {
      // Check if report already exists
      const existing = await reportRepo.getByVaersId(String(raw.VAERS_ID));
      if (existing) {
        errors.push(`Report ${raw.VAERS_ID} already exists`);
        continue;
      }
      
      // Convert and insert report
      const reportData = convertToReportRecord(raw);
      const report = await reportRepo.insert(reportData);
      
      // Insert vaccines
      const vaccines = convertToVaccineRecords(raw, report.id);
      if (vaccines.length > 0) {
        await vaccineRepo.insertMany(vaccines);
      }
      
      // Insert symptoms
      const symptoms = convertToSymptomRecords(raw, report.id);
      if (symptoms.length > 0) {
        await symptomRepo.insertMany(symptoms);
      }
      
      imported++;
    } catch (error) {
      errors.push(`Failed to import ${raw.VAERS_ID}: ${error}`);
    }
  }
  
  return { imported, errors };
}