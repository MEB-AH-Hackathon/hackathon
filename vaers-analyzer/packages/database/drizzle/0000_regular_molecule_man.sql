CREATE TYPE "public"."report_status" AS ENUM('new', 'validated', 'pending_validation', 'rejected');--> statement-breakpoint
CREATE TYPE "public"."symptom_severity" AS ENUM('mild', 'moderate', 'severe', 'life_threatening');--> statement-breakpoint
CREATE TYPE "public"."validation_status" AS ENUM('validated', 'unvalidated', 'disputed');--> statement-breakpoint
CREATE TABLE "vaers_reports" (
	"id" serial PRIMARY KEY NOT NULL,
	"vaers_id" varchar(50) NOT NULL,
	"recv_date" date,
	"state" varchar(2),
	"age_yrs" numeric(5, 2),
	"sex" varchar(1),
	"symptom_text" text,
	"died" boolean,
	"l_threat" boolean,
	"er_visit" boolean,
	"hospital" boolean,
	"disable" boolean,
	"recovd" varchar(1),
	"vax_date" date,
	"onset_date" date,
	"num_days" integer,
	"status" "report_status" DEFAULT 'new' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "vaers_reports_vaers_id_unique" UNIQUE("vaers_id")
);
--> statement-breakpoint
CREATE TABLE "vaers_symptoms" (
	"id" serial PRIMARY KEY NOT NULL,
	"report_id" integer NOT NULL,
	"symptom_name" text NOT NULL,
	"severity" "symptom_severity",
	"validation_status" "validation_status" DEFAULT 'unvalidated' NOT NULL,
	"fda_reference" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "vaers_vaccines" (
	"id" serial PRIMARY KEY NOT NULL,
	"report_id" integer NOT NULL,
	"vax_type" varchar(50),
	"vax_manufacturer" text,
	"vax_name" text,
	"vax_dose_series" varchar(20),
	"vax_route" varchar(20),
	"vax_site" varchar(20),
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "symptom_analogies" (
	"id" serial PRIMARY KEY NOT NULL,
	"symptom_id" integer NOT NULL,
	"similar_report_id" integer NOT NULL,
	"similarity_score" numeric(5, 4) NOT NULL,
	"validation_status" "validation_status" DEFAULT 'unvalidated' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fda_reports" (
	"id" serial PRIMARY KEY NOT NULL,
	"filename" text NOT NULL,
	"success" boolean DEFAULT true NOT NULL,
	"controlled_trial_text" text NOT NULL,
	"symptoms_list" jsonb NOT NULL,
	"study_type" text,
	"source_section" text,
	"full_pdf_text" text NOT NULL,
	"raw_response" text NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "vaers_symptoms" ADD CONSTRAINT "vaers_symptoms_report_id_vaers_reports_id_fk" FOREIGN KEY ("report_id") REFERENCES "public"."vaers_reports"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "vaers_vaccines" ADD CONSTRAINT "vaers_vaccines_report_id_vaers_reports_id_fk" FOREIGN KEY ("report_id") REFERENCES "public"."vaers_reports"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "symptom_analogies" ADD CONSTRAINT "symptom_analogies_symptom_id_vaers_symptoms_id_fk" FOREIGN KEY ("symptom_id") REFERENCES "public"."vaers_symptoms"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "symptom_analogies" ADD CONSTRAINT "symptom_analogies_similar_report_id_vaers_reports_id_fk" FOREIGN KEY ("similar_report_id") REFERENCES "public"."vaers_reports"("id") ON DELETE cascade ON UPDATE no action;