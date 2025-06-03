import { db } from '../db-connection';
import { eq, and } from 'drizzle-orm';
import { vaersVaccines, type VaersVaccineRecord, type NewVaersVaccineRecord } from '../schema/vaers-vaccines';

export class VaersVaccineRepository {
  async insert(vaccineData: NewVaersVaccineRecord): Promise<VaersVaccineRecord> {
    const [vaccine] = await db.insert(vaersVaccines).values(vaccineData).returning();
    if (!vaccine) {
      throw new Error('Failed to insert VAERS vaccine');
    }
    return vaccine;
  }

  async insertMany(vaccinesData: NewVaersVaccineRecord[]): Promise<VaersVaccineRecord[]> {
    if (vaccinesData.length === 0) return [];
    return await db.insert(vaersVaccines).values(vaccinesData).returning();
  }

  async update(vaccineId: number, updateData: Partial<VaersVaccineRecord>): Promise<VaersVaccineRecord[]> {
    return await db
      .update(vaersVaccines)
      .set(updateData)
      .where(eq(vaersVaccines.id, vaccineId))
      .returning();
  }

  async getById(vaccineId: number): Promise<VaersVaccineRecord | undefined> {
    const results = await db.select().from(vaersVaccines).where(eq(vaersVaccines.id, vaccineId));
    return results.length ? results[0] : undefined;
  }

  async getByReportId(reportId: number): Promise<VaersVaccineRecord[]> {
    return await db.select().from(vaersVaccines).where(eq(vaersVaccines.reportId, reportId));
  }

  async delete(vaccineId: number): Promise<void> {
    await db.delete(vaersVaccines).where(eq(vaersVaccines.id, vaccineId));
  }

  async deleteByReportId(reportId: number): Promise<void> {
    await db.delete(vaersVaccines).where(eq(vaersVaccines.reportId, reportId));
  }

  async getByVaxType(vaxType: string): Promise<VaersVaccineRecord[]> {
    return await db
      .select()
      .from(vaersVaccines)
      .where(eq(vaersVaccines.vaxType, vaxType));
  }

  async getByManufacturer(manufacturer: string): Promise<VaersVaccineRecord[]> {
    return await db
      .select()
      .from(vaersVaccines)
      .where(eq(vaersVaccines.vaxManufacturer, manufacturer));
  }
}