export const REPORT_STATUS = ['new', 'validated', 'pending_validation', 'rejected'] as const;
export const SYMPTOM_SEVERITY = ['mild', 'moderate', 'severe', 'life_threatening'] as const;
export const VALIDATION_STATUS = ['validated', 'unvalidated', 'disputed'] as const;

export type ReportStatus = typeof REPORT_STATUS[number];
export type SymptomSeverity = typeof SYMPTOM_SEVERITY[number];
export type ValidationStatus = typeof VALIDATION_STATUS[number];

export interface VaersReport {
  id: number;
  vaersId: string;
  patientAge?: number;
  patientSex?: string;
  vaccineName: string;
  vaccineManufacturer: string;
  vaccineLot?: string;
  vaccineDate: Date;
  onsetDate?: Date;
  reportedDate: Date;
  status: ReportStatus;
  symptoms: VaersSymptom[];
  narrative?: string;
  createdAt: Date;
  updatedAt: Date;
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