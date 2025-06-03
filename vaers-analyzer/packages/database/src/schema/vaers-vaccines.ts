import { serial, integer, text, timestamp, pgTable, varchar } from "drizzle-orm/pg-core";
import { vaersReports } from './vaers-reports';

export const vaersVaccines = pgTable("vaers_vaccines", {
  id: serial("id").primaryKey(),
  reportId: integer("report_id").notNull().references(() => vaersReports.id, { onDelete: 'cascade' }),
  vaxType: varchar("vax_type", { length: 50 }),
  vaxManufacturer: text("vax_manufacturer"),
  vaxName: text("vax_name"),
  vaxDoseSeries: varchar("vax_dose_series", { length: 20 }),
  vaxRoute: varchar("vax_route", { length: 20 }),
  vaxSite: varchar("vax_site", { length: 20 }),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export type VaersVaccineRecord = typeof vaersVaccines.$inferSelect;
export type NewVaersVaccineRecord = typeof vaersVaccines.$inferInsert;