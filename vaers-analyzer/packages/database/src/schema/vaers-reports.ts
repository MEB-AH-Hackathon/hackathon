import { serial, integer, text, timestamp, date, pgTable, pgEnum, varchar, numeric, boolean, jsonb } from "drizzle-orm/pg-core";
import { REPORT_STATUS } from '@vaers/types';

export const reportStatus = pgEnum("report_status", REPORT_STATUS as unknown as [string, ...string[]]);
export const sexEnum = pgEnum("sex_enum", ["male", "female", "unknown"]);
export const recovdEnum = pgEnum("recovd_enum", ["yes", "no", "unknown"]);

export const vaersReports = pgTable("vaers_reports", {
  id: serial("id").primaryKey(),
  vaersId: integer("vaers_id").notNull().unique(),
  recvDate: varchar("recv_date", { length: 10 }), // MM/DD/YYYY format
  state: varchar("state", { length: 2 }),
  ageYrs: numeric("age_yrs", { precision: 5, scale: 2 }),
  sex: sexEnum("sex"),
  symptomText: text("symptom_text"),
  died: boolean("died").notNull().default(false),
  lThreat: boolean("l_threat").notNull().default(false),
  erVisit: boolean("er_visit").notNull().default(false),
  hospital: boolean("hospital").notNull().default(false),
  disable: boolean("disable").notNull().default(false),
  recovd: recovdEnum("recovd"),
  vaxDate: varchar("vax_date", { length: 10 }), // Date string
  onsetDate: varchar("onset_date", { length: 10 }), // Date string
  numDays: numeric("num_days", { precision: 10, scale: 1 }),
  vaxTypeList: jsonb("vax_type_list").$type<string[]>().notNull().default([]),
  vaxManuList: jsonb("vax_manu_list").$type<string[]>().notNull().default([]),
  vaxNameList: jsonb("vax_name_list").$type<string[]>().notNull().default([]),
  vaxDoseSeriesList: jsonb("vax_dose_series_list").$type<string[]>().notNull().default([]),
  vaxRouteList: jsonb("vax_route_list").$type<string[]>().notNull().default([]),
  vaxSiteList: jsonb("vax_site_list").$type<string[]>().notNull().default([]),
  symptomList: jsonb("symptom_list").$type<string[]>().notNull(),
  status: reportStatus("status").notNull().default("new"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
});

export type VaersReportRecord = typeof vaersReports.$inferSelect;
export type NewVaersReportRecord = typeof vaersReports.$inferInsert;