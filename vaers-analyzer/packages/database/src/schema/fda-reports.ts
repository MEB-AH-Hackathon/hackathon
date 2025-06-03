import { serial, text, timestamp, pgTable, jsonb } from "drizzle-orm/pg-core";

export const fdaReports = pgTable("fda_reports", {
  id: serial("id").primaryKey(),
  vaccineName: text("vaccine_name").notNull(),
  manufacturer: text("manufacturer").notNull(),
  adverseEvents: jsonb("adverse_events").$type<string[]>().notNull(),
  pdfFile: text("pdf_file").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
});

export type FdaReportRecord = typeof fdaReports.$inferSelect;
export type NewFdaReportRecord = typeof fdaReports.$inferInsert;