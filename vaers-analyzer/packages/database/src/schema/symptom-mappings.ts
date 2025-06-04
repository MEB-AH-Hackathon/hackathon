import { serial, text, timestamp, pgTable, jsonb } from "drizzle-orm/pg-core";

export const symptomMappings = pgTable("symptom_mappings", {
  id: serial("id").primaryKey(),
  vaersSymptom: text("vaers_symptom").notNull().unique(),
  fdaAdverseEvents: jsonb("fda_adverse_events").$type<string[]>().notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
});

export type SymptomMappingRecord = typeof symptomMappings.$inferSelect;
export type NewSymptomMappingRecord = typeof symptomMappings.$inferInsert;