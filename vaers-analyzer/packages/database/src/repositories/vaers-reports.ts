import { db } from '../db-connection';
import { eq, sql, like, desc, and, or, gte } from 'drizzle-orm';
import { vaersReports, type VaersReportRecord, type NewVaersReportRecord } from '../schema/vaers-reports';

export class VaersReportRepository {
  async insert(reportData: NewVaersReportRecord): Promise<VaersReportRecord> {
    const [report] = await db.insert(vaersReports).values(reportData).returning();
    if (!report) {
      throw new Error('Failed to insert VAERS report');
    }
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

  async getByVaersId(vaersId: number): Promise<VaersReportRecord | undefined> {
    const results = await db.select().from(vaersReports).where(eq(vaersReports.vaersId, vaersId));
    return results.length ? results[0] : undefined;
  }

  async delete(reportId: number): Promise<void> {
    await db.delete(vaersReports).where(eq(vaersReports.id, reportId));
  }

  async getAll(): Promise<VaersReportRecord[]> {
    return await db.select().from(vaersReports).orderBy(vaersReports.createdAt);
  }

  async getReportsByOutcome(outcome: 'died' | 'lThreat' | 'erVisit' | 'hospital' | 'disable'): Promise<VaersReportRecord[]> {
    return await db.select().from(vaersReports).where(eq(vaersReports[outcome], 'Y'));
  }

  async getReportsWithMultipleVaccines(): Promise<VaersReportRecord[]> {
    return await db
      .select()
      .from(vaersReports)
      .where(sql`jsonb_array_length(${vaersReports.vaxTypeList}) > 1`);
  }

  async getReportsByVaccineType(vaccineType: string): Promise<VaersReportRecord[]> {
    return await db
      .select()
      .from(vaersReports)
      .where(sql`${vaersReports.vaxTypeList} @> ${JSON.stringify([vaccineType])}`);
  }

  async getReportsBySymptom(symptom: string): Promise<VaersReportRecord[]> {
    return await db
      .select()
      .from(vaersReports)
      .where(sql`${vaersReports.symptomList} @> ${JSON.stringify([symptom])}`);
  }

  async searchSymptoms(searchTerm: string): Promise<VaersReportRecord[]> {
    return await db
      .select()
      .from(vaersReports)
      .where(like(vaersReports.symptomText, `%${searchTerm}%`));
  }

  async getPaginated(limit: number, offset: number): Promise<{ reports: VaersReportRecord[], total: number }> {
    const [reports, countResult] = await Promise.all([
      db.select()
        .from(vaersReports)
        .orderBy(desc(vaersReports.createdAt))
        .limit(limit)
        .offset(offset),
      db.select({ count: sql<number>`count(*)::int` })
        .from(vaersReports)
    ]);
    
    return {
      reports,
      total: countResult[0]?.count || 0
    };
  }

  async getPaginatedWithFilters(
    limit: number,
    offset: number,
    filters: {
      search?: string;
      vaccineType?: string;
      outcome?: 'died' | 'lThreat' | 'erVisit' | 'hospital' | 'disable';
      dateRange?: number; // days
    }
  ): Promise<{ reports: VaersReportRecord[], total: number }> {
    const conditions = [];

    if (filters.search) {
      conditions.push(
        or(
          like(vaersReports.symptomText, `%${filters.search}%`),
          sql`${vaersReports.vaersId}::text LIKE ${`%${filters.search}%`}`,
          sql`EXISTS (
            SELECT 1 FROM jsonb_array_elements_text(${vaersReports.symptomList}) AS symptom
            WHERE symptom ILIKE ${`%${filters.search}%`}
          )`,
          sql`EXISTS (
            SELECT 1 FROM jsonb_array_elements_text(${vaersReports.vaxNameList}) AS vaccine
            WHERE vaccine ILIKE ${`%${filters.search}%`}
          )`
        )
      );
    }

    if (filters.vaccineType) {
      conditions.push(sql`${vaersReports.vaxTypeList} @> ${JSON.stringify([filters.vaccineType])}`);
    }

    if (filters.outcome) {
      conditions.push(eq(vaersReports[filters.outcome], 'Y'));
    }

    if (filters.dateRange) {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - filters.dateRange);
      conditions.push(gte(vaersReports.recvDate, cutoffDate.toLocaleDateString('en-US')));
    }

    const whereClause = conditions.length > 0 ? and(...conditions) : undefined;

    const [reports, countResult] = await Promise.all([
      db.select()
        .from(vaersReports)
        .where(whereClause)
        .orderBy(desc(vaersReports.createdAt))
        .limit(limit)
        .offset(offset),
      db.select({ count: sql<number>`count(*)::int` })
        .from(vaersReports)
        .where(whereClause)
    ]);

    return {
      reports,
      total: countResult[0]?.count || 0
    };
  }
}