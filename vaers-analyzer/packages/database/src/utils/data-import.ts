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
 * Convert Y/N to boolean, with default false
 */
export function parseYesNoToBoolean(value: string | null | undefined): boolean {
  return value === 'Y';
}

/**
 * Convert sex values from F/M/U to male/female/unknown
 */
export function parseSex(sex: string | null | undefined): 'male' | 'female' | 'unknown' | null {
  if (sex === 'F') return 'female';
  if (sex === 'M') return 'male';
  if (sex === 'U') return 'unknown';
  return null;
}

/**
 * Convert recovery status from Y/N/U to yes/no/unknown
 */
export function parseRecoveryStatus(recovd: string | null | undefined): 'yes' | 'no' | 'unknown' | null {
  if (recovd === 'Y') return 'yes';
  if (recovd === 'N') return 'no';
  if (recovd === 'U') return 'unknown';
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
    sex: parseSex(raw.SEX),
    symptomText: raw.SYMPTOM_TEXT || null,
    died: parseYesNoToBoolean(raw.DIED),
    lThreat: parseYesNoToBoolean(raw.L_THREAT),
    erVisit: parseYesNoToBoolean(raw.ER_VISIT),
    hospital: parseYesNoToBoolean(raw.HOSPITAL),
    disable: parseYesNoToBoolean(raw.DISABLE),
    recovd: parseRecoveryStatus(raw.RECOVD),
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