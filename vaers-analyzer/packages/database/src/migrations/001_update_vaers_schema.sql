-- Migration to update VAERS schema to match actual data format
-- WARNING: This migration will drop existing data. Backup before running!

-- Drop existing tables (CASCADE will drop dependent tables)
DROP TABLE IF EXISTS symptom_analogies CASCADE;
DROP TABLE IF EXISTS vaers_symptoms CASCADE;
DROP TABLE IF EXISTS vaers_reports CASCADE;

-- Drop existing enums
DROP TYPE IF EXISTS report_status CASCADE;
DROP TYPE IF EXISTS symptom_severity CASCADE;
DROP TYPE IF EXISTS validation_status CASCADE;

-- Create enums
CREATE TYPE report_status AS ENUM ('new', 'validated', 'pending_validation', 'rejected');
CREATE TYPE symptom_severity AS ENUM ('mild', 'moderate', 'severe', 'life_threatening');
CREATE TYPE validation_status AS ENUM ('validated', 'unvalidated', 'disputed');

-- Create updated vaers_reports table with outcome flags
CREATE TABLE vaers_reports (
    id SERIAL PRIMARY KEY,
    vaers_id VARCHAR(50) NOT NULL UNIQUE,
    recv_date DATE,
    state VARCHAR(2),
    age_yrs NUMERIC(5, 2),
    sex VARCHAR(1) CHECK (sex IN ('F', 'M', 'U')),
    symptom_text TEXT,
    died BOOLEAN,
    l_threat BOOLEAN,
    er_visit BOOLEAN,
    hospital BOOLEAN,
    disable BOOLEAN,
    recovd VARCHAR(1) CHECK (recovd IN ('Y', 'N', 'U')),
    vax_date DATE,
    onset_date DATE,
    num_days INTEGER,
    status report_status NOT NULL DEFAULT 'new',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create vaccines table for multiple vaccines per report
CREATE TABLE vaers_vaccines (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES vaers_reports(id) ON DELETE CASCADE,
    vax_type VARCHAR(50),
    vax_manufacturer TEXT,
    vax_name TEXT,
    vax_dose_series VARCHAR(20),
    vax_route VARCHAR(20),
    vax_site VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create symptoms table
CREATE TABLE vaers_symptoms (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES vaers_reports(id) ON DELETE CASCADE,
    symptom_name TEXT NOT NULL,
    severity symptom_severity,
    validation_status validation_status NOT NULL DEFAULT 'unvalidated',
    fda_reference TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create symptom analogies table
CREATE TABLE symptom_analogies (
    id SERIAL PRIMARY KEY,
    symptom_id INTEGER NOT NULL REFERENCES vaers_symptoms(id) ON DELETE CASCADE,
    similar_report_id INTEGER NOT NULL REFERENCES vaers_reports(id) ON DELETE CASCADE,
    similarity_score NUMERIC(5, 4) NOT NULL,
    validation_status validation_status NOT NULL DEFAULT 'unvalidated',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_vaers_reports_vaers_id ON vaers_reports(vaers_id);
CREATE INDEX idx_vaers_reports_status ON vaers_reports(status);
CREATE INDEX idx_vaers_reports_vax_date ON vaers_reports(vax_date);
CREATE INDEX idx_vaers_reports_outcomes ON vaers_reports(died, l_threat, er_visit, hospital, disable);

CREATE INDEX idx_vaers_vaccines_report_id ON vaers_vaccines(report_id);
CREATE INDEX idx_vaers_vaccines_vax_type ON vaers_vaccines(vax_type);
CREATE INDEX idx_vaers_vaccines_manufacturer ON vaers_vaccines(vax_manufacturer);

CREATE INDEX idx_vaers_symptoms_report_id ON vaers_symptoms(report_id);
CREATE INDEX idx_vaers_symptoms_validation ON vaers_symptoms(validation_status);

CREATE INDEX idx_symptom_analogies_symptom_id ON symptom_analogies(symptom_id);
CREATE INDEX idx_symptom_analogies_similar_report ON symptom_analogies(similar_report_id);