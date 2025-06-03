import { serial, text, timestamp, pgTable, boolean, jsonb } from "drizzle-orm/pg-core";

export const fdaReports = pgTable("fda_reports", {
  id: serial("id").primaryKey(),
  filename: text("filename").notNull(),
  success: boolean("success").notNull().default(true),
  controlledTrialText: text("controlled_trial_text").notNull(),
  symptomsList: jsonb("symptoms_list").$type<string[]>().notNull(),
  studyType: text("study_type"),
  sourceSection: text("source_section"),
  fullPdfText: text("full_pdf_text").notNull(),
  rawResponse: text("raw_response").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
});

export type FdaReportRecord = typeof fdaReports.$inferSelect;
export type NewFdaReportRecord = typeof fdaReports.$inferInsert;