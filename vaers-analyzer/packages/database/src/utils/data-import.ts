import type { VaersRawData } from '@vaers/types';
import type { NewVaersReportRecord } from '../schema/vaers-reports';

/**
 * Parse date string in MM/DD/YYYY format to string (keep original format)
 */
export function parseVaersDate(dateStr: string | null | undefined): string | null {
  if (!dateStr) return null;
  return dateStr;
}

/**
 * Keep Y/N/U string as is
 */
export function parseYesNo(value: string | null | undefined): string | null {
  if (value === 'Y' || value === 'N') return value;
  return null;
}

/**
 * Convert raw VAERS data to database report record
 */
export function convertToReportRecord(raw: VaersRawData): Omit<NewVaersReportRecord, 'id' | 'createdAt' | 'updatedAt'> {
  return {
    vaersId: Number(raw.VAERS_ID),
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
    numDays: raw.NUMDAYS !== null && !isNaN(Number(raw.NUMDAYS)) ? String(raw.NUMDAYS) : null,
    vaxTypeList: raw.VAX_TYPE_list || [],
    vaxManuList: raw.VAX_MANU_list || [],
    vaxNameList: raw.VAX_NAME_list || [],
    vaxDoseSeriesList: raw.VAX_DOSE_SERIES_list?.map(d => d || '') || [],
    vaxRouteList: raw.VAX_ROUTE_list?.map(r => r || '') || [],
    vaxSiteList: raw.VAX_SITE_list?.map(s => s || '') || [],
    symptomList: raw.symptom_list || [],
    status: 'new'
  };
}


/**
 * Import a batch of raw VAERS data
 */
export async function importVaersData(
  rawData: VaersRawData[],
  reportRepo: any
): Promise<{ imported: number; errors: string[] }> {
  let imported = 0;
  const errors: string[] = [];
  
  for (const raw of rawData) {
    try {
      // Check if report already exists
      const existing = await reportRepo.getByVaersId(Number(raw.VAERS_ID));
      if (existing) {
        errors.push(`Report ${raw.VAERS_ID} already exists`);
        continue;
      }
      
      // Convert and insert report
      const reportData = convertToReportRecord(raw);
      const report = await reportRepo.insert(reportData);
      
      imported++;
    } catch (error) {
      errors.push(`Failed to import ${raw.VAERS_ID}: ${error}`);
    }
  }
  
  return { imported, errors };
}