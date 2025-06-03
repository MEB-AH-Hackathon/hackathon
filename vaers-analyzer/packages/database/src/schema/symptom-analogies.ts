import { serial, integer, decimal, timestamp, pgTable } from "drizzle-orm/pg-core";
import { vaersSymptoms } from './vaers-symptoms';
import { vaersReports } from './vaers-reports';
import { validationStatus } from './vaers-symptoms';

export const symptomAnalogies = pgTable("symptom_analogies", {
  id: serial("id").primaryKey(),
  symptomId: integer("symptom_id").notNull().references(() => vaersSymptoms.id, { onDelete: 'cascade' }),
  similarReportId: integer("similar_report_id").notNull().references(() => vaersReports.id, { onDelete: 'cascade' }),
  similarityScore: decimal("similarity_score", { precision: 5, scale: 4 }).notNull(),
  validationStatus: validationStatus("validation_status").notNull().default("unvalidated"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export type SymptomAnalogyRecord = typeof symptomAnalogies.$inferSelect;
export type NewSymptomAnalogyRecord = typeof symptomAnalogies.$inferInsert;