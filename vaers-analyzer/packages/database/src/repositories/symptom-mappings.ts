import { db } from '../db-connection';
import { eq, like, sql } from 'drizzle-orm';
import { symptomMappings, type SymptomMappingRecord, type NewSymptomMappingRecord } from '../schema/symptom-mappings';

export class SymptomMappingRepository {
  async insert(mappingData: NewSymptomMappingRecord): Promise<SymptomMappingRecord> {
    const [mapping] = await db.insert(symptomMappings).values(mappingData).returning();
    if (!mapping) {
      throw new Error('Failed to insert symptom mapping');
    }
    return mapping;
  }

  async update(mappingId: number, updateData: Partial<SymptomMappingRecord>): Promise<SymptomMappingRecord[]> {
    return await db
      .update(symptomMappings)
      .set({ ...updateData, updatedAt: new Date() })
      .where(eq(symptomMappings.id, mappingId))
      .returning();
  }

  async getById(mappingId: number): Promise<SymptomMappingRecord | undefined> {
    const results = await db.select().from(symptomMappings).where(eq(symptomMappings.id, mappingId));
    return results.length ? results[0] : undefined;
  }

  async getByVaersSymptom(vaersSymptom: string): Promise<SymptomMappingRecord | undefined> {
    const results = await db.select().from(symptomMappings).where(eq(symptomMappings.vaersSymptom, vaersSymptom));
    return results.length ? results[0] : undefined;
  }

  async delete(mappingId: number): Promise<void> {
    await db.delete(symptomMappings).where(eq(symptomMappings.id, mappingId));
  }

  async getAll(): Promise<SymptomMappingRecord[]> {
    return await db.select().from(symptomMappings).orderBy(symptomMappings.vaersSymptom);
  }

  async searchVaersSymptoms(searchTerm: string): Promise<SymptomMappingRecord[]> {
    return await db
      .select()
      .from(symptomMappings)
      .where(like(symptomMappings.vaersSymptom, `%${searchTerm}%`));
  }

  async getMappingsWithFdaEvents(): Promise<SymptomMappingRecord[]> {
    return await db
      .select()
      .from(symptomMappings)
      .where(sql`jsonb_array_length(${symptomMappings.fdaAdverseEvents}) > 0`);
  }

  async getMappingsWithoutFdaEvents(): Promise<SymptomMappingRecord[]> {
    return await db
      .select()
      .from(symptomMappings)
      .where(sql`jsonb_array_length(${symptomMappings.fdaAdverseEvents}) = 0`);
  }
}