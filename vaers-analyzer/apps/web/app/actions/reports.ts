"use server";

import { 
  VaersReportRepository, 
  VaersVaccineRepository, 
  VaersSymptomRepository,
  importVaersData 
} from '@vaers/database';
import type { VaersRawData, VaersReport } from '@vaers/types';
import { revalidatePath } from 'next/cache';

const reportRepo = new VaersReportRepository();
const vaccineRepo = new VaersVaccineRepository();
const symptomRepo = new VaersSymptomRepository();

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
  includeDetails: boolean = true,
  filters: ReportFilters = {}
): Promise<PaginatedReports> {
  try {
    // Load all reports with details for filtering
    const baseReports = await reportRepo.getAll();
    const allReports = await Promise.all(
      baseReports.map(async (r) => {
        const details = await reportRepo.getReportWithDetails(r.id);
        if (!details) return null;
        return {
          ...details,
          ageYrs: details.ageYrs ? parseFloat(details.ageYrs as string) : undefined,
        } as VaersReport;
      })
    );
    const validReports = allReports.filter((r): r is VaersReport => r !== null);

    // Apply filters in memory
    let filtered = validReports;

    if (filters.vaccineType) {
      const type = filters.vaccineType.toLowerCase();
      filtered = filtered.filter((r) =>
        r.vaccines.some((v) => v.vaxType?.toLowerCase() === type)
      );
    }

    if (filters.outcome) {
      if (filters.outcome === 'recovered') {
        filtered = filtered.filter((r) => r.recovd === 'Y');
      } else if (filters.outcome === 'hospitalized') {
        filtered = filtered.filter((r) => r.hospital === true);
      } else if (filters.outcome === 'serious') {
        filtered = filtered.filter((r) => r.died || r.lThreat);
      }
    }

    if (filters.search) {
      const q = filters.search.toLowerCase();
      filtered = filtered.filter((r) => {
        const inVaccines = r.vaccines.some(
          (v) =>
            v.vaxName?.toLowerCase().includes(q) ||
            v.vaxType?.toLowerCase().includes(q)
        );
        const inSymptoms = r.symptoms.some((s) =>
          s.symptomName.toLowerCase().includes(q)
        );
        return (
          r.vaersId.toLowerCase().includes(q) ||
          (r.symptomText && r.symptomText.toLowerCase().includes(q)) ||
          inVaccines ||
          inSymptoms
        );
      });
    }

    if (filters.dateRange) {
      const days =
        filters.dateRange === '7days'
          ? 7
          : filters.dateRange === '30days'
          ? 30
          : 90;
      const now = Date.now();
      filtered = filtered.filter((r) => {
        if (!r.recvDate) return false;
        const diff = (now - new Date(r.recvDate).getTime()) / (1000 * 60 * 60 * 24);
        return diff <= days;
      });
    }

    const totalFiltered = filtered.length;
    const paginatedReports = filtered.slice(offset, offset + limit);

    return {
      reports: paginatedReports,
      pagination: {
        total: totalFiltered,
        limit,
        offset,
        hasMore: offset + limit < totalFiltered
      }
    };
  } catch (error) {
    console.error('Error fetching reports:', error);
    throw new Error('Failed to fetch reports');
  }
}

export async function getReportById(id: number): Promise<VaersReport | null> {
  try {
    const report = await reportRepo.getReportWithDetails(id);
    if (!report) return null;
    
    return {
      ...report,
      ageYrs: report.ageYrs ? parseFloat(report.ageYrs as string) : undefined,
    } as VaersReport;
  } catch (error) {
    console.error('Error fetching report:', error);
    throw new Error('Failed to fetch report');
  }
}

export async function getReportByVaersId(vaersId: string): Promise<VaersReport | null> {
  try {
    const report = await reportRepo.getByVaersId(vaersId);
    if (!report) return null;
    
    const details = await reportRepo.getReportWithDetails(report.id);
    if (!details) return null;
    
    return {
      ...details,
      ageYrs: details.ageYrs ? parseFloat(details.ageYrs as string) : undefined,
    } as VaersReport;
  } catch (error) {
    console.error('Error fetching report by VAERS ID:', error);
    throw new Error('Failed to fetch report');
  }
}

export async function createReport(data: VaersRawData): Promise<VaersReport> {
  try {
    // Check if report already exists
    const existing = await reportRepo.getByVaersId(String(data.VAERS_ID));
    if (existing) {
      throw new Error('Report with this VAERS ID already exists');
    }
    
    // Use the data import utility to handle the conversion
    const result = await importVaersData(
      [data],
      reportRepo,
      vaccineRepo,
      symptomRepo
    );
    
    if (result.errors.length > 0) {
      throw new Error(result.errors[0]);
    }
    
    // Fetch the created report with details
    const createdReport = await reportRepo.getByVaersId(String(data.VAERS_ID));
    if (!createdReport) {
      throw new Error('Failed to retrieve created report');
    }
    
    const reportWithDetails = await reportRepo.getReportWithDetails(createdReport.id);
    if (!reportWithDetails) {
      throw new Error('Failed to retrieve created report details');
    }
    
    // Revalidate the reports pages
    revalidatePath('/reports');
    revalidatePath('/reports/new');
    
    return {
      ...reportWithDetails,
      ageYrs: reportWithDetails.ageYrs ? parseFloat(reportWithDetails.ageYrs as string) : undefined,
    } as VaersReport;
  } catch (error) {
    console.error('Error creating report:', error);
    throw error;
  }
}

// Helper function to convert VaersReport to database record type
function convertToDbRecord(report: Partial<VaersReport>) {
  return {
    ...report,
    ageYrs: report.ageYrs ? report.ageYrs.toString() : undefined,
    // Remove fields that don't exist in the database record
    vaccines: undefined,
    symptoms: undefined,
  };
}

export async function updateReport(
  id: number, 
  updateData: Partial<VaersReport>
): Promise<VaersReport> {
  try {
    const dbUpdateData = convertToDbRecord(updateData);
    await reportRepo.update(id, dbUpdateData);
    const updated = await reportRepo.getReportWithDetails(id);
    
    if (!updated) {
      throw new Error('Failed to retrieve updated report');
    }
    
    // Revalidate relevant paths
    revalidatePath('/reports');
    revalidatePath(`/reports/${id}`);
    
    return {
      ...updated,
      ageYrs: updated.ageYrs ? parseFloat(updated.ageYrs as string) : undefined,
    } as VaersReport;
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
    const { reports } = await getReports(limit, 0, true);
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
    
    // Get details for each report
    const reportsWithDetails = await Promise.all(
      reports.map(report => reportRepo.getReportWithDetails(report.id))
    );
    
    return reportsWithDetails
      .filter(Boolean)
      .map(report => ({
        ...report!,
        ageYrs: report!.ageYrs ? parseFloat(report!.ageYrs as string) : undefined,
      })) as VaersReport[];
  } catch (error) {
    console.error('Error fetching reports by outcome:', error);
    throw error;
  }
}