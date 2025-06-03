import { db } from '../db-connection';
import { eq, and, sql } from 'drizzle-orm';
import { vaersSymptoms, type VaersSymptomRecord, type NewVaersSymptomRecord } from '../schema/vaers-symptoms';
import { symptomAnalogies } from '../schema/symptom-analogies';

export class VaersSymptomRepository {
  async insert(symptomData: NewVaersSymptomRecord): Promise<VaersSymptomRecord> {
    const [symptom] = await db.insert(vaersSymptoms).values(symptomData).returning();
    if (!symptom) {
      throw new Error('Failed to insert VAERS symptom');
    }
    return symptom;
  }

  async insertMany(symptomsData: NewVaersSymptomRecord[]): Promise<VaersSymptomRecord[]> {
    return await db.insert(vaersSymptoms).values(symptomsData).returning();
  }

  async update(symptomId: number, updateData: Partial<VaersSymptomRecord>): Promise<VaersSymptomRecord[]> {
    return await db
      .update(vaersSymptoms)
      .set(updateData)
      .where(eq(vaersSymptoms.id, symptomId))
      .returning();
  }

  async getById(symptomId: number): Promise<VaersSymptomRecord | undefined> {
    const results = await db.select().from(vaersSymptoms).where(eq(vaersSymptoms.id, symptomId));
    return results.length ? results[0] : undefined;
  }

  async getByReportId(reportId: number): Promise<VaersSymptomRecord[]> {
    return await db.select().from(vaersSymptoms).where(eq(vaersSymptoms.reportId, reportId));
  }

  async delete(symptomId: number): Promise<void> {
    await db.delete(vaersSymptoms).where(eq(vaersSymptoms.id, symptomId));
  }

  async getValidatedSymptoms(): Promise<VaersSymptomRecord[]> {
    return await db
      .select()
      .from(vaersSymptoms)
      .where(eq(vaersSymptoms.validationStatus, 'validated'));
  }

  async getSymptomWithAnalogies(symptomId: number) {
    const symptom = await this.getById(symptomId);
    if (!symptom) return null;

    const analogies = await db
      .select()
      .from(symptomAnalogies)
      .where(eq(symptomAnalogies.symptomId, symptomId));

    return { ...symptom, analogies };
  }

  private preparedSymptomsByReport = db
    .select()
    .from(vaersSymptoms)
    .where(eq(vaersSymptoms.reportId, sql.placeholder('reportId')))
    .prepare('get_symptoms_by_report');

  async executePreparedSymptomsByReport(reportId: number): Promise<VaersSymptomRecord[]> {
    return await this.preparedSymptomsByReport.execute({ reportId });
  }
}