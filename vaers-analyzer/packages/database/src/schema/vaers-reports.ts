import { serial, integer, text, timestamp, date, pgTable, pgEnum, varchar } from "drizzle-orm/pg-core";
import { REPORT_STATUS } from '@vaers/types';

export const reportStatus = pgEnum("report_status", REPORT_STATUS as unknown as [string, ...string[]]);

export const vaersReports = pgTable("vaers_reports", {
  id: serial("id").primaryKey(),
  vaersId: varchar("vaers_id", { length: 50 }).notNull().unique(),
  patientAge: integer("patient_age"),
  patientSex: varchar("patient_sex", { length: 10 }),
  vaccineName: text("vaccine_name").notNull(),
  vaccineManufacturer: text("vaccine_manufacturer").notNull(),
  vaccineLot: varchar("vaccine_lot", { length: 100 }),
  vaccineDate: date("vaccine_date", { mode: 'date' }).notNull(),
  onsetDate: date("onset_date", { mode: 'date' }),
  reportedDate: date("reported_date", { mode: 'date' }).notNull(),
  status: reportStatus("status").notNull().default("new"),
  narrative: text("narrative"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
});

export type VaersReportRecord = typeof vaersReports.$inferSelect;
export type NewVaersReportRecord = typeof vaersReports.$inferInsert;