import { serial, integer, text, timestamp, date, pgTable, pgEnum, varchar, numeric, boolean } from "drizzle-orm/pg-core";
import { REPORT_STATUS } from '@vaers/types';

export const reportStatus = pgEnum("report_status", REPORT_STATUS as unknown as [string, ...string[]]);

export const vaersReports = pgTable("vaers_reports", {
  id: serial("id").primaryKey(),
  vaersId: varchar("vaers_id", { length: 50 }).notNull().unique(),
  recvDate: date("recv_date", { mode: 'date' }),
  state: varchar("state", { length: 2 }),
  ageYrs: numeric("age_yrs", { precision: 5, scale: 2 }),
  sex: varchar("sex", { length: 1 }),
  symptomText: text("symptom_text"),
  died: boolean("died"),
  lThreat: boolean("l_threat"),
  erVisit: boolean("er_visit"),
  hospital: boolean("hospital"),
  disable: boolean("disable"),
  recovd: varchar("recovd", { length: 1 }), // Y/N/U
  vaxDate: date("vax_date", { mode: 'date' }),
  onsetDate: date("onset_date", { mode: 'date' }),
  numDays: integer("num_days"),
  status: reportStatus("status").notNull().default("new"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
});

export type VaersReportRecord = typeof vaersReports.$inferSelect;
export type NewVaersReportRecord = typeof vaersReports.$inferInsert;