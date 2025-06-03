export const REPORT_STATUS = ['new', 'validated', 'pending_validation', 'rejected'] as const;
export const SYMPTOM_SEVERITY = ['mild', 'moderate', 'severe', 'life_threatening'] as const;
export const VALIDATION_STATUS = ['validated', 'unvalidated', 'disputed'] as const;
export const RECOVERY_STATUS = ['Y', 'N', 'U'] as const;
export const SEX_VALUES = ['F', 'M', 'U'] as const;

export type ReportStatus = typeof REPORT_STATUS[number];
export type SymptomSeverity = typeof SYMPTOM_SEVERITY[number];
export type ValidationStatus = typeof VALIDATION_STATUS[number];
export type RecoveryStatus = typeof RECOVERY_STATUS[number];
export type Sex = typeof SEX_VALUES[number];

export interface VaersReport {
  id: number;
  vaersId: string;
  recvDate?: Date;
  state?: string;
  ageYrs?: number;
  sex?: Sex;
  symptomText?: string;
  died?: boolean;
  lThreat?: boolean;
  erVisit?: boolean;
  hospital?: boolean;
  disable?: boolean;
  recovd?: RecoveryStatus;
  vaxDate?: Date;
  onsetDate?: Date;
  numDays?: number;
  status: ReportStatus;
  vaccines: VaersVaccine[];
  symptoms: VaersSymptom[];
  createdAt: Date;
  updatedAt: Date;
}

export interface VaersVaccine {
  id: number;
  reportId: number;
  vaxType?: string;
  vaxManufacturer?: string;
  vaxName?: string;
  vaxDoseSeries?: string;
  vaxRoute?: string;
  vaxSite?: string;
  createdAt: Date;
}

export interface VaersSymptom {
  id: number;
  reportId: number;
  symptomName: string;
  severity?: SymptomSeverity;
  validationStatus: ValidationStatus;
  fdaReference?: string;
  createdAt: Date;
}

export interface SymptomAnalogy {
  id: number;
  symptomId: number;
  similarReportId: number;
  similarityScore: number;
  validationStatus: ValidationStatus;
  createdAt: Date;
}

// Data import interfaces matching the actual VAERS data format
export interface VaersRawData {
  VAERS_ID: string | number;
  RECVDATE?: string | null;
  STATE?: string | null;
  AGE_YRS?: number | null;
  SEX?: string | null;
  SYMPTOM_TEXT?: string | null;
  DIED?: string | null;
  L_THREAT?: string | null;
  ER_VISIT?: string | null;
  HOSPITAL?: string | null;
  DISABLE?: string | null;
  RECOVD?: string | null;
  VAX_DATE?: string | null;
  ONSET_DATE?: string | null;
  NUMDAYS?: number | null;
  VAX_TYPE_list?: string[] | null;
  VAX_MANU_list?: string[] | null;
  VAX_NAME_list?: string[] | null;
  VAX_DOSE_SERIES_list?: (string | null)[] | null;
  VAX_ROUTE_list?: (string | null)[] | null;
  VAX_SITE_list?: (string | null)[] | null;
  symptom_list: string[];
}

// FDA Report interfaces
export interface FdaReportData {
  controlled_trial_text: string;
  symptoms_list: string[];
  study_type: string | null;
  source_section: string | null;
  full_pdf_text: string;
}

export interface FdaReportItem {
  filename: string;
  success: boolean;
  data: FdaReportData;
  raw_response: string;
}

export interface FdaReport {
  id: number;
  filename: string;
  success: boolean;
  controlledTrialText: string;
  symptomsList: string[];
  studyType?: string | null;
  sourceSection?: string | null;
  fullPdfText: string;
  rawResponse: string;
  createdAt: Date;
  updatedAt: Date;
}