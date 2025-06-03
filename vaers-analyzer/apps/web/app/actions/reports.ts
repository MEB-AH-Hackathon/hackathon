"use server";

import { 
  VaersReportRepository,
  importVaersData,
  type VaersReportRecord
} from '@vaers/database';
import type { VaersRawData, VaersReport, Sex, RecoveryStatus, ReportStatus } from '@vaers/types';
import { revalidatePath } from 'next/cache';

const reportRepo = new VaersReportRepository();

// Helper function to convert database record to VaersReport
function dbRecordToVaersReport(record: VaersReportRecord): VaersReport {
  return {
    id: record.id,
    vaersId: String(record.vaersId),
    recvDate: record.recvDate ? new Date(record.recvDate) : undefined,
    state: record.state || undefined,
    ageYrs: record.ageYrs ? parseFloat(record.ageYrs) : undefined,
    sex: record.sex as Sex | undefined,
    symptomText: record.symptomText || undefined,
    died: record.died,
    lThreat: record.lThreat,
    erVisit: record.erVisit,
    hospital: record.hospital,
    disable: record.disable,
    recovd: record.recovd as RecoveryStatus | undefined,
    vaxDate: record.vaxDate ? new Date(record.vaxDate) : undefined,
    onsetDate: record.onsetDate ? new Date(record.onsetDate) : undefined,
    numDays: record.numDays ? Number(record.numDays) : undefined,
    status: record.status as ReportStatus,
    createdAt: record.createdAt,
    updatedAt: record.updatedAt,
    vaccines: (record.vaxTypeList || []).map((type: string, i: number) => ({
      id: i,
      reportId: record.id,
      vaxType: type || undefined,
      vaxManufacturer: record.vaxManuList?.[i] || undefined,
      vaxName: record.vaxNameList?.[i] || undefined,
      vaxDoseSeries: record.vaxDoseSeriesList?.[i] || undefined,
      vaxRoute: record.vaxRouteList?.[i] || undefined,
      vaxSite: record.vaxSiteList?.[i] || undefined,
      createdAt: record.createdAt
    })),
    symptoms: (record.symptomList || []).map((symptom: string, i: number) => ({
      id: i,
      reportId: record.id,
      symptomName: symptom,
      severity: undefined,
      validationStatus: 'unvalidated' as const,
      fdaReference: undefined,
      createdAt: record.createdAt
    }))
  };
}

export interface PaginatedReports {
  reports: VaersReport[];
  pagination: {
    total: number;
    limit: number;
    offset: number;
    hasMore: boolean;
  };
}

export interface ReportFilters {
  search?: string;
  vaccineType?: string;
  outcome?: 'recovered' | 'hospitalized' | 'serious';
  dateRange?: '7days' | '30days' | '90days';
}

export async function getReports(
  limit: number = 20,
  offset: number = 0,
  filters: ReportFilters = {}
): Promise<PaginatedReports> {
  try {
    // Map outcome filter
    const outcomeMap: Record<string, 'died' | 'lThreat' | 'erVisit' | 'hospital' | 'disable'> = {
      'hospitalized': 'hospital',
      'serious': 'died' // For serious, we'll need special handling
    };

    // Map date range to days
    const dateRangeDays = filters.dateRange === '7days' ? 7 
      : filters.dateRange === '30days' ? 30 
      : filters.dateRange === '90days' ? 90 
      : undefined;

    // Handle 'recovered' outcome which maps to recovd='yes'
    if (filters.outcome === 'recovered') {
      // We need to check for recovd='yes' - for now, use base pagination and filter
      const baseQuery = await reportRepo.getPaginated(limit, offset);
      return {
        reports: baseQuery.reports
          .filter(r => r.recovd === 'yes')
          .map(dbRecordToVaersReport),
        pagination: {
          total: baseQuery.total,
          limit,
          offset,
          hasMore: offset + limit < baseQuery.total
        }
      };
    }

    // For 'serious' outcome, we need to fetch both died and life threatening
    if (filters.outcome === 'serious') {
      // Need to handle this case separately - for now, just use died
      const { reports, total } = await reportRepo.getPaginatedWithFilters(limit, offset, {
        search: filters.search,
        vaccineType: filters.vaccineType,
        outcome: 'died',
        dateRange: dateRangeDays
      });

      return {
        reports: reports.map(dbRecordToVaersReport),
        pagination: {
          total,
          limit,
          offset,
          hasMore: offset + limit < total
        }
      };
    }

    // Use the new paginated method with filters
    const { reports, total } = await reportRepo.getPaginatedWithFilters(limit, offset, {
      search: filters.search,
      vaccineType: filters.vaccineType,
      outcome: filters.outcome && filters.outcome in outcomeMap ? outcomeMap[filters.outcome] as ('died' | 'lThreat' | 'erVisit' | 'hospital' | 'disable') : undefined,
      dateRange: dateRangeDays
    });

    return {
      reports: reports.map(dbRecordToVaersReport),
      pagination: {
        total,
        limit,
        offset,
        hasMore: offset + limit < total
      }
    };
  } catch (error) {
    console.error('Error fetching reports:', error);
    throw new Error('Failed to fetch reports');
  }
}

export async function getReportById(id: number): Promise<VaersReport | null> {
  try {
    const report = await reportRepo.getById(id);
    if (!report) return null;
    
    return dbRecordToVaersReport(report);
  } catch (error) {
    console.error('Error fetching report:', error);
    throw new Error('Failed to fetch report');
  }
}

export async function getReportByVaersId(vaersId: string): Promise<VaersReport | null> {
  try {
    const report = await reportRepo.getByVaersId(Number(vaersId));
    if (!report) return null;
    
    return dbRecordToVaersReport(report);
  } catch (error) {
    console.error('Error fetching report by VAERS ID:', error);
    throw new Error('Failed to fetch report');
  }
}

export async function createReport(data: VaersRawData): Promise<VaersReport> {
  try {
    // Check if report already exists
    const existing = await reportRepo.getByVaersId(Number(data.VAERS_ID));
    if (existing) {
      throw new Error('Report with this VAERS ID already exists');
    }
    
    // Use the data import utility to handle the conversion
    const result = await importVaersData(
      [data],
      reportRepo
    );
    
    if (result.errors.length > 0) {
      throw new Error(result.errors[0]);
    }
    
    // Fetch the created report
    const createdReport = await reportRepo.getByVaersId(Number(data.VAERS_ID));
    if (!createdReport) {
      throw new Error('Failed to retrieve created report');
    }
    
    // Revalidate the reports pages
    revalidatePath('/reports');
    revalidatePath('/reports/new');
    
    return dbRecordToVaersReport(createdReport);
  } catch (error) {
    console.error('Error creating report:', error);
    throw error;
  }
}

// Helper function to convert VaersReport to database record type
function convertToDbRecord(report: Partial<VaersReport>) {
  const { vaccines, symptoms, ...dbFields } = report;
  return {
    ...dbFields,
    vaersId: report.vaersId ? Number(report.vaersId) : undefined,
    ageYrs: report.ageYrs ? report.ageYrs.toString() : undefined,
    died: report.died,
    lThreat: report.lThreat,
    erVisit: report.erVisit,
    hospital: report.hospital,
    disable: report.disable,
    recvDate: report.recvDate ? report.recvDate.toLocaleDateString('en-US') : undefined,
    vaxDate: report.vaxDate ? report.vaxDate.toLocaleDateString('en-US') : undefined,
    onsetDate: report.onsetDate ? report.onsetDate.toLocaleDateString('en-US') : undefined,
    numDays: report.numDays?.toString(),
    vaxTypeList: vaccines?.map(v => v.vaxType || ''),
    vaxManuList: vaccines?.map(v => v.vaxManufacturer || ''),
    vaxNameList: vaccines?.map(v => v.vaxName || ''),
    vaxDoseSeriesList: vaccines?.map(v => v.vaxDoseSeries || ''),
    vaxRouteList: vaccines?.map(v => v.vaxRoute || ''),
    vaxSiteList: vaccines?.map(v => v.vaxSite || ''),
    symptomList: symptoms?.map(s => s.symptomName)
  };
}

export async function updateReport(
  id: number, 
  updateData: Partial<VaersReport>
): Promise<VaersReport> {
  try {
    const dbUpdateData = convertToDbRecord(updateData);
    await reportRepo.update(id, dbUpdateData);
    const updated = await reportRepo.getById(id);
    
    if (!updated) {
      throw new Error('Failed to retrieve updated report');
    }
    
    // Revalidate relevant paths
    revalidatePath('/reports');
    revalidatePath(`/reports/${id}`);
    
    return dbRecordToVaersReport(updated);
  } catch (error) {
    console.error('Error updating report:', error);
    throw error;
  }
}

export async function deleteReport(id: number): Promise<void> {
  try {
    await reportRepo.delete(id);
    
    // Revalidate the reports list
    revalidatePath('/reports');
  } catch (error) {
    console.error('Error deleting report:', error);
    throw error;
  }
}

export async function getExampleReports(limit: number = 5): Promise<VaersReport[]> {
  try {
    const { reports } = await getReports(limit, 0);
    return reports;
  } catch (error) {
    console.error('Error fetching example reports:', error);
    throw error;
  }
}

export async function getReportsByOutcome(
  outcome: 'died' | 'lThreat' | 'erVisit' | 'hospital' | 'disable'
): Promise<VaersReport[]> {
  try {
    const reports = await reportRepo.getReportsByOutcome(outcome);
    return reports.map(dbRecordToVaersReport);
  } catch (error) {
    console.error('Error fetching reports by outcome:', error);
    throw error;
  }
}