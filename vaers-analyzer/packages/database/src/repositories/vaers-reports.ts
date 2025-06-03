import { db } from '../db-connection';
import { eq, and, sql } from 'drizzle-orm';
import { vaersReports, type VaersReportRecord, type NewVaersReportRecord } from '../schema/vaers-reports';
import { vaersSymptoms } from '../schema/vaers-symptoms';
import { vaersVaccines } from '../schema/vaers-vaccines';

export class VaersReportRepository {
  async insert(reportData: NewVaersReportRecord): Promise<VaersReportRecord> {
    const [report] = await db.insert(vaersReports).values(reportData).returning();
    return report;
  }

  async update(reportId: number, updateData: Partial<VaersReportRecord>): Promise<VaersReportRecord[]> {
    return await db
      .update(vaersReports)
      .set({ ...updateData, updatedAt: new Date() })
      .where(eq(vaersReports.id, reportId))
      .returning();
  }

  async getById(reportId: number): Promise<VaersReportRecord | undefined> {
    const results = await db.select().from(vaersReports).where(eq(vaersReports.id, reportId));
    return results.length ? results[0] : undefined;
  }

  async getByVaersId(vaersId: string): Promise<VaersReportRecord | undefined> {
    const results = await db.select().from(vaersReports).where(eq(vaersReports.vaersId, vaersId));
    return results.length ? results[0] : undefined;
  }

  async delete(reportId: number): Promise<void> {
    await db.delete(vaersReports).where(eq(vaersReports.id, reportId));
  }

  async getAll(): Promise<VaersReportRecord[]> {
    return await db.select().from(vaersReports).orderBy(vaersReports.createdAt);
  }

  async getReportWithDetails(reportId: number) {
    const report = await this.getById(reportId);
    if (!report) return null;

    const [symptoms, vaccines] = await Promise.all([
      db.select().from(vaersSymptoms).where(eq(vaersSymptoms.reportId, reportId)),
      db.select().from(vaersVaccines).where(eq(vaersVaccines.reportId, reportId))
    ]);

    return { ...report, symptoms, vaccines };
  }

  async getReportsByOutcome(outcome: 'died' | 'lThreat' | 'erVisit' | 'hospital' | 'disable'): Promise<VaersReportRecord[]> {
    return await db.select().from(vaersReports).where(eq(vaersReports[outcome], true));
  }

  async getReportsWithMultipleVaccines(): Promise<VaersReportRecord[]> {
    const reportsWithMultipleVaccines = await db
      .select({ 
        reportId: vaersVaccines.reportId,
        vaccineCount: sql<number>`count(*)::int` 
      })
      .from(vaersVaccines)
      .groupBy(vaersVaccines.reportId)
      .having(sql`count(*) > 1`);

    if (reportsWithMultipleVaccines.length === 0) return [];

    const reportIds = reportsWithMultipleVaccines.map(r => r.reportId);
    return await db
      .select()
      .from(vaersReports)
      .where(sql`${vaersReports.id} = ANY(${reportIds})`);
  }
}