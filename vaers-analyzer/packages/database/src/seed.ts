import * as dotenv from 'dotenv';
import * as path from 'path';
import * as fs from 'fs';

// Load environment variables from .env file
dotenv.config({ path: path.join(__dirname, '..', '.env') });

import { db } from './db-connection';
import { VaersReportRepository } from './repositories/vaers-reports';
import { FdaReportRepository } from './repositories/fda-reports';
import { SymptomMappingRepository } from './repositories/symptom-mappings';
import type { VaersRawData } from '@vaers/types';

// Types for the JSON data files
interface SymptomMappingData {
  vaers_symptom: string;
  fda_adverse_events: string[];
}

interface FdaReportData {
  filename: string;
  vax_type: string;
  vax_name: string;
  vax_manu: string;
  extraction_success: boolean;
  adverse_events: string[];
  study_type: string;
  source_section: string;
  controlled_trial_text: string;
}

interface VaersSubsetData {
  VAERS_ID: number;
  RECVDATE: string;
  STATE: string;
  AGE_YRS: number | null;
  SEX: string;
  SYMPTOM_TEXT: string;
  DIED: string | null;
  L_THREAT: string | null;
  ER_VISIT: string | null;
  HOSPITAL: string | null;
  DISABLE: string | null;
  RECOVD: string | null;
  VAX_DATE: string;
  ONSET_DATE: string;
  NUMDAYS: number | null;
  VAX_TYPE_list: string[];
  VAX_MANU_list: string[];
  VAX_NAME_list: string[];
  VAX_DOSE_SERIES_list: string[];
  VAX_ROUTE_list: string[];
  VAX_SITE_list: string[];
  symptom_list: string[];
}

async function seed() {
  const environment = process.env.NODE_ENV || 'development';
  console.log(`🌱 Starting database seed for ${environment.toUpperCase()} environment...`);

  // Safety check for production
  if (environment === 'production') {
    const confirmProd = process.env.SEED_PRODUCTION_CONFIRM;
    if (confirmProd !== 'true') {
      console.log('⚠️  Production seeding requires SEED_PRODUCTION_CONFIRM=true environment variable');
      console.log('   This prevents accidental data modification in production.');
      process.exit(1);
    }
    console.log('✅ Production seeding confirmed');
  }

  try {
    // Initialize repositories
    const reportRepo = new VaersReportRepository();
    const fdaReportRepo = new FdaReportRepository();
    const symptomMappingRepo = new SymptomMappingRepository();

    // Load data files
    const jsonDataPath = path.join(__dirname, '..', '..', '..', '..', 'json_data');
    
    console.log('📂 Loading data files...');
    
    // Load symptom mappings
    const symptomMappingsPath = path.join(jsonDataPath, 'symptom_mappings.json');
    const symptomMappingsData: SymptomMappingData[] = JSON.parse(fs.readFileSync(symptomMappingsPath, 'utf8'));
    
    // Load FDA reports
    const fdaReportsPath = path.join(jsonDataPath, 'fda_reports.json');
    const fdaReportsData: FdaReportData[] = JSON.parse(fs.readFileSync(fdaReportsPath, 'utf8'));
    
    // For VAERS data, we'll process it in batches due to its size
    const vaersSubsetPath = path.join(jsonDataPath, 'vaers_subset.json');
    console.log('📊 Reading VAERS subset data (this may take a moment)...');
    const vaersSubsetData: VaersSubsetData[] = JSON.parse(fs.readFileSync(vaersSubsetPath, 'utf8'));

    // 1. Seed symptom mappings
    console.log(`📊 Importing ${symptomMappingsData.length} symptom mappings...`);
    let symptomMappingsImported = 0;
    const symptomMappingErrors: string[] = [];

    for (const mapping of symptomMappingsData) {
      try {
        await symptomMappingRepo.insert({
          vaersSymptom: mapping.vaers_symptom,
          fdaAdverseEvents: mapping.fda_adverse_events
        });
        symptomMappingsImported++;
      } catch (error) {
        symptomMappingErrors.push(`Failed to import symptom mapping ${mapping.vaers_symptom}: ${error}`);
      }
    }

    console.log(`✅ Successfully imported ${symptomMappingsImported} symptom mappings`);
    if (symptomMappingErrors.length > 0) {
      console.log(`⚠️  ${symptomMappingErrors.length} symptom mapping errors (showing first 5):`);
      symptomMappingErrors.slice(0, 5).forEach(error => console.log(`   - ${error}`));
    }

    // 2. Seed FDA reports
    console.log(`📊 Importing ${fdaReportsData.length} FDA reports...`);
    let fdaImported = 0;
    const fdaErrors: string[] = [];

    for (const fdaItem of fdaReportsData) {
      try {
        await fdaReportRepo.insert({
          vaccineName: fdaItem.vax_name,
          manufacturer: fdaItem.vax_manu,
          adverseEvents: fdaItem.adverse_events,
          pdfFile: fdaItem.filename
        });
        fdaImported++;
      } catch (error) {
        fdaErrors.push(`Failed to import FDA report ${fdaItem.filename}: ${error}`);
      }
    }

    console.log(`✅ Successfully imported ${fdaImported} FDA reports`);
    if (fdaErrors.length > 0) {
      console.log(`⚠️  ${fdaErrors.length} FDA import errors (showing first 5):`);
      fdaErrors.slice(0, 5).forEach(error => console.log(`   - ${error}`));
    }

    // 3. Seed VAERS reports
    console.log(`📊 Importing ${vaersSubsetData.length} VAERS reports...`);
    let vaersImported = 0;
    const vaersErrors: string[] = [];
    const batchSize = 100; // Process in batches for better performance
    
    for (let i = 0; i < vaersSubsetData.length; i += batchSize) {
      const batch = vaersSubsetData.slice(i, i + batchSize);
      console.log(`   Processing batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(vaersSubsetData.length / batchSize)}...`);
      
      for (const vaersItem of batch) {
        try {
          await reportRepo.insert({
            vaersId: vaersItem.VAERS_ID,
            recvDate: vaersItem.RECVDATE,
            state: vaersItem.STATE,
            ageYrs: vaersItem.AGE_YRS?.toString() || null,
            sex: vaersItem.SEX,
            symptomText: vaersItem.SYMPTOM_TEXT,
            died: vaersItem.DIED,
            lThreat: vaersItem.L_THREAT,
            erVisit: vaersItem.ER_VISIT,
            hospital: vaersItem.HOSPITAL,
            disable: vaersItem.DISABLE,
            recovd: vaersItem.RECOVD,
            vaxDate: vaersItem.VAX_DATE,
            onsetDate: vaersItem.ONSET_DATE,
            numDays: vaersItem.NUMDAYS?.toString() || null,
            vaxTypeList: vaersItem.VAX_TYPE_list,
            vaxManuList: vaersItem.VAX_MANU_list,
            vaxNameList: vaersItem.VAX_NAME_list,
            vaxDoseSeriesList: vaersItem.VAX_DOSE_SERIES_list,
            vaxRouteList: vaersItem.VAX_ROUTE_list,
            vaxSiteList: vaersItem.VAX_SITE_list,
            symptomList: vaersItem.symptom_list
          });
          vaersImported++;
        } catch (error) {
          vaersErrors.push(`Failed to import VAERS report ${vaersItem.VAERS_ID}: ${error}`);
        }
      }
    }

    console.log(`✅ Successfully imported ${vaersImported} VAERS reports`);
    if (vaersErrors.length > 0) {
      console.log(`⚠️  ${vaersErrors.length} VAERS import errors (showing first 5):`);
      vaersErrors.slice(0, 5).forEach(error => console.log(`   - ${error}`));
    }

    // Log final statistics
    const reports = await db.query.vaersReports.findMany();
    const fdaReports = await db.query.fdaReports.findMany();
    const symptomMappings = await db.query.symptomMappings.findMany();

    console.log('\n📈 Database Statistics:');
    console.log(`   - Total VAERS Reports: ${reports.length}`);
    console.log(`   - Total FDA Reports: ${fdaReports.length}`);
    console.log(`   - Total Symptom Mappings: ${symptomMappings.length}`);

    // Show sample data
    console.log('\n📋 Sample VAERS Report:');
    if (reports.length > 0 && reports[0]) {
      const sampleReport = reports[0];
      console.log(`   - VAERS ID: ${sampleReport.vaersId}`);
      console.log(`   - State: ${sampleReport.state}`);
      console.log(`   - Age: ${sampleReport.ageYrs}`);
      console.log(`   - Vaccines: ${sampleReport.vaxTypeList.length}`);
      console.log(`   - Symptoms: ${sampleReport.symptomList.length}`);
    }

    console.log('\n📋 Sample FDA Report:');
    if (fdaReports.length > 0) {
      const sampleFdaReport = fdaReports[0];
      if (sampleFdaReport) {
        console.log(`   - Vaccine Name: ${sampleFdaReport.vaccineName}`);
        console.log(`   - Manufacturer: ${sampleFdaReport.manufacturer}`);
        console.log(`   - PDF File: ${sampleFdaReport.pdfFile}`);
        console.log(`   - Adverse Events: ${sampleFdaReport.adverseEvents.length}`);
      }
    }

    console.log('\n📋 Sample Symptom Mapping:');
    if (symptomMappings.length > 0) {
      const sampleMapping = symptomMappings[0];
      if (sampleMapping) {
        console.log(`   - VAERS Symptom: ${sampleMapping.vaersSymptom}`);
        console.log(`   - FDA Adverse Events: ${sampleMapping.fdaAdverseEvents.length}`);
      }
    }

    console.log('\n✨ Database seeding completed!');
    process.exit(0);
  } catch (error) {
    console.error('❌ Error seeding database:', error);
    process.exit(1);
  }
}

// Run the seed function
seed();