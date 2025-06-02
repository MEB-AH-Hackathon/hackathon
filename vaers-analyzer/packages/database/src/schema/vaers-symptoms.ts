import { serial, integer, text, timestamp, pgTable, pgEnum, varchar } from "drizzle-orm/pg-core";
import { SYMPTOM_SEVERITY, VALIDATION_STATUS } from '@vaers/types';
import { vaersReports } from './vaers-reports';

export const symptomSeverity = pgEnum("symptom_severity", SYMPTOM_SEVERITY as unknown as [string, ...string[]]);
export const validationStatus = pgEnum("validation_status", VALIDATION_STATUS as unknown as [string, ...string[]]);

export const vaersSymptoms = pgTable("vaers_symptoms", {
  id: serial("id").primaryKey(),
  reportId: integer("report_id").notNull().references(() => vaersReports.id, { onDelete: 'cascade' }),
  symptomName: text("symptom_name").notNull(),
  severity: symptomSeverity("severity"),
  validationStatus: validationStatus("validation_status").notNull().default("unvalidated"),
  fdaReference: text("fda_reference"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export type VaersSymptomRecord = typeof vaersSymptoms.$inferSelect;
export type NewVaersSymptomRecord = typeof vaersSymptoms.$inferInsert;