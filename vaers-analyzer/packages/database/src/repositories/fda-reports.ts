import { db } from '../db-connection';
import { eq, sql, like } from 'drizzle-orm';
import { fdaReports, type FdaReportRecord, type NewFdaReportRecord } from '../schema/fda-reports';

export class FdaReportRepository {
  async insert(reportData: NewFdaReportRecord): Promise<FdaReportRecord> {
    const [report] = await db.insert(fdaReports).values(reportData).returning();
    if (!report) {
      throw new Error('Failed to insert FDA report');
    }
    return report;
  }

  async update(reportId: number, updateData: Partial<FdaReportRecord>): Promise<FdaReportRecord[]> {
    return await db
      .update(fdaReports)
      .set({ ...updateData, updatedAt: new Date() })
      .where(eq(fdaReports.id, reportId))
      .returning();
  }

  async getById(reportId: number): Promise<FdaReportRecord | undefined> {
    const results = await db.select().from(fdaReports).where(eq(fdaReports.id, reportId));
    return results.length ? results[0] : undefined;
  }

  async getByVaccineName(vaccineName: string): Promise<FdaReportRecord | undefined> {
    const results = await db.select().from(fdaReports).where(eq(fdaReports.vaccineName, vaccineName));
    return results.length ? results[0] : undefined;
  }

  async getByManufacturer(manufacturer: string): Promise<FdaReportRecord[]> {
    return await db.select().from(fdaReports).where(eq(fdaReports.manufacturer, manufacturer));
  }

  async delete(reportId: number): Promise<void> {
    await db.delete(fdaReports).where(eq(fdaReports.id, reportId));
  }

  async getAll(): Promise<FdaReportRecord[]> {
    return await db.select().from(fdaReports).orderBy(fdaReports.vaccineName);
  }

  async searchByAdverseEvent(adverseEvent: string): Promise<FdaReportRecord[]> {
    return await db
      .select()
      .from(fdaReports)
      .where(sql`${fdaReports.adverseEvents} @> ${JSON.stringify([adverseEvent])}`);
  }

  async searchVaccineNames(searchTerm: string): Promise<FdaReportRecord[]> {
    return await db
      .select()
      .from(fdaReports)
      .where(like(fdaReports.vaccineName, `%${searchTerm}%`));
  }

  async getUniqueAdverseEvents(): Promise<string[]> {
    const results = await db
      .select({
        events: sql<string[]>`DISTINCT jsonb_array_elements_text(${fdaReports.adverseEvents})`
      })
      .from(fdaReports);
    
    return results.map(r => r.events).flat();
  }

  async getUniqueManufacturers(): Promise<string[]> {
    const results = await db
      .selectDistinct({ manufacturer: fdaReports.manufacturer })
      .from(fdaReports);
    
    return results.map(r => r.manufacturer);
  }
}