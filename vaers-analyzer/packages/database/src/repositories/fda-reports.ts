import { db } from '../db-connection';
import { eq, sql, ilike } from 'drizzle-orm';
import { fdaReports, type FdaReportRecord, type NewFdaReportRecord } from '../schema/fda-reports';

export class FdaReportRepository {
  async insert(reportData: NewFdaReportRecord): Promise<FdaReportRecord> {
    const [report] = await db.insert(fdaReports).values(reportData).returning();
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

  async getByFilename(filename: string): Promise<FdaReportRecord | undefined> {
    const results = await db.select().from(fdaReports).where(eq(fdaReports.filename, filename));
    return results.length ? results[0] : undefined;
  }

  async delete(reportId: number): Promise<void> {
    await db.delete(fdaReports).where(eq(fdaReports.id, reportId));
  }

  async getAllReports(): Promise<FdaReportRecord[]> {
    return await db.select().from(fdaReports).where(eq(fdaReports.success, true));
  }

  async getReportsByStudyType(studyType: string): Promise<FdaReportRecord[]> {
    return await db.select().from(fdaReports).where(eq(fdaReports.studyType, studyType));
  }

  async searchBySymptom(symptom: string): Promise<FdaReportRecord[]> {
    return await db
      .select()
      .from(fdaReports)
      .where(sql`${fdaReports.symptomsList}::jsonb @> ${JSON.stringify([symptom])}::jsonb`);
  }

  async searchByText(searchText: string): Promise<FdaReportRecord[]> {
    return await db
      .select()
      .from(fdaReports)
      .where(
        sql`${fdaReports.controlledTrialText} ILIKE ${`%${searchText}%`} OR 
            ${fdaReports.fullPdfText} ILIKE ${`%${searchText}%`}`
      );
  }

  async getUniqueSymptoms(): Promise<string[]> {
    const results = await db
      .select({
        symptoms: sql<string[]>`DISTINCT jsonb_array_elements_text(${fdaReports.symptomsList})`
      })
      .from(fdaReports);
    
    return results.map(r => r.symptoms).flat();
  }

  async getReportsBySourceSection(sourceSection: string): Promise<FdaReportRecord[]> {
    return await db.select().from(fdaReports).where(eq(fdaReports.sourceSection, sourceSection));
  }
}