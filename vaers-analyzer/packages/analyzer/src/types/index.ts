import type { VaersReport } from '@vaers/types';

export interface StreamController {
  emit(event: string, data: any): Promise<void>;
}

export interface AnalysisStep {
  id: number;
  title: string;
  status: 'pending' | 'in-progress' | 'completed' | 'error';
  details?: string;
  error?: string;
}

export interface ExtractedInfo {
  vaccines: Array<{
    type: string;
    manufacturer?: string;
    dose?: string;
  }>;
  symptoms: string[];
  outcomes: {
    died: boolean;
    lifeThreatening: boolean;
    hospitalized: boolean;
    disabled: boolean;
    emergencyRoom: boolean;
  };
  onsetDays?: number;
  patientInfo: {
    age?: number;
    sex?: string;
  };
}

export interface FDASearchResult {
  vaccine: string;
  symptoms: string[];
  foundReports: number;
  reports: Array<{
    id: number;
    studyType: string;
    sourceSection: string;
    symptoms: string[];
    excerpt: string;
  }>;
}

export interface SimilarReport {
  vaersId: string;
  similarityScore: number;
  matchedSymptoms: string[];
  vaccines: string[];
  outcomes: string[];
}

export interface AnalysisResult {
  report: VaersReport;
  extractedInfo: ExtractedInfo;
  fdaResults: FDASearchResult[];
  similarReports: SimilarReport[];
  overallConfidence: 'high' | 'medium' | 'low';
  recommendations: string[];
}

export interface StructuredReport {
  summary: string;
  disclaimer: string;
  sections: Array<{
    title: string;
    content: string;
    confidence?: 'high' | 'medium' | 'low';
    links?: Array<{
      vaersId: string;
      similarity: number;
    }>;
  }>;
  metadata: {
    searchedDatabases: string[];
    analysisDate: Date;
    confidenceLevel: 'high' | 'medium' | 'low';
  };
}