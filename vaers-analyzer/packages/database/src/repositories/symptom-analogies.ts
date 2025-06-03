import { db } from '../db-connection';
import { eq, and, sql, desc } from 'drizzle-orm';
import { symptomAnalogies, type SymptomAnalogyRecord, type NewSymptomAnalogyRecord } from '../schema/symptom-analogies';

export class SymptomAnalogyRepository {
  async insert(analogyData: NewSymptomAnalogyRecord): Promise<SymptomAnalogyRecord> {
    const [analogy] = await db.insert(symptomAnalogies).values(analogyData).returning();
    return analogy;
  }

  async insertMany(analogiesData: NewSymptomAnalogyRecord[]): Promise<SymptomAnalogyRecord[]> {
    return await db.insert(symptomAnalogies).values(analogiesData).returning();
  }

  async update(analogyId: number, updateData: Partial<SymptomAnalogyRecord>): Promise<SymptomAnalogyRecord[]> {
    return await db
      .update(symptomAnalogies)
      .set(updateData)
      .where(eq(symptomAnalogies.id, analogyId))
      .returning();
  }

  async getById(analogyId: number): Promise<SymptomAnalogyRecord | undefined> {
    const results = await db.select().from(symptomAnalogies).where(eq(symptomAnalogies.id, analogyId));
    return results.length ? results[0] : undefined;
  }

  async getBySymptomId(symptomId: number): Promise<SymptomAnalogyRecord[]> {
    return await db
      .select()
      .from(symptomAnalogies)
      .where(eq(symptomAnalogies.symptomId, symptomId))
      .orderBy(desc(symptomAnalogies.similarityScore));
  }

  async delete(analogyId: number): Promise<void> {
    await db.delete(symptomAnalogies).where(eq(symptomAnalogies.id, analogyId));
  }

  async getTopAnalogiesForSymptom(symptomId: number, limit: number = 10): Promise<SymptomAnalogyRecord[]> {
    return await db
      .select()
      .from(symptomAnalogies)
      .where(eq(symptomAnalogies.symptomId, symptomId))
      .orderBy(desc(symptomAnalogies.similarityScore))
      .limit(limit);
  }

  async getValidatedAnalogies(symptomId: number): Promise<SymptomAnalogyRecord[]> {
    return await db
      .select()
      .from(symptomAnalogies)
      .where(
        and(
          eq(symptomAnalogies.symptomId, symptomId),
          eq(symptomAnalogies.validationStatus, 'validated')
        )
      )
      .orderBy(desc(symptomAnalogies.similarityScore));
  }
}