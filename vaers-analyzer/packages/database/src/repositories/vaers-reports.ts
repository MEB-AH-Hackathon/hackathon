import { db } from '../db-connection';
import { eq, and, sql } from 'drizzle-orm';
import { vaersReports, type VaersReportRecord, type NewVaersReportRecord } from '../schema/vaers-reports';
import { vaersSymptoms } from '../schema/vaers-symptoms';

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

  async getByVaccine(vaccineName: string): Promise<VaersReportRecord[]> {
    return await db.select().from(vaersReports).where(eq(vaersReports.vaccineName, vaccineName));
  }

  async getReportWithSymptoms(reportId: number) {
    const report = await this.getById(reportId);
    if (!report) return null;

    const symptoms = await db
      .select()
      .from(vaersSymptoms)
      .where(eq(vaersSymptoms.reportId, reportId));

    return { ...report, symptoms };
  }

  private preparedReportsByVaccine = db
    .select()
    .from(vaersReports)
    .where(eq(vaersReports.vaccineName, sql.placeholder('vaccineName')))
    .prepare('get_reports_by_vaccine');

  async executePreparedReportsByVaccine(vaccineName: string): Promise<VaersReportRecord[]> {
    return await this.preparedReportsByVaccine.execute({ vaccineName });
  }
}