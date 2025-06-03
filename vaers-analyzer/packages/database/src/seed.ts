import { db } from './db-connection';
import { VaersReportRepository } from './repositories/vaers-reports';
import { VaersVaccineRepository } from './repositories/vaers-vaccines';
import { VaersSymptomRepository } from './repositories/vaers-symptoms';
import { FdaReportRepository } from './repositories/fda-reports';
import { importVaersData } from './utils/data-import';
import type { VaersRawData, FdaReportItem } from '@vaers/types';
import sampleData from './seed-data/vaers-samples.json';
import fdaSampleData from './seed-data/fda-reports-samples.json';

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
    const vaccineRepo = new VaersVaccineRepository();
    const symptomRepo = new VaersSymptomRepository();
    const fdaReportRepo = new FdaReportRepository();

    // Cast the JSON data to VaersRawData array
    const vaersData = sampleData as VaersRawData[];

    // In production, you might want to use a larger or different dataset
    const recordsToImport = environment === 'production'
      ? vaersData
      : vaersData; // Same data for now, but could be different

    console.log(`📊 Importing ${recordsToImport.length} VAERS reports for ${environment}...`);

    // Import the data
    const result = await importVaersData(
      recordsToImport,
      reportRepo,
      vaccineRepo,
      symptomRepo
    );

    console.log(`✅ Successfully imported ${result.imported} reports`);

    if (result.errors.length > 0) {
      console.log('⚠️  Errors encountered:');
      result.errors.forEach(error => console.log(`   - ${error}`));
    }

    // Import FDA report data
    const fdaData = fdaSampleData as FdaReportItem[];
    console.log(`\n📊 Importing ${fdaData.length} FDA reports...`);

    let fdaImported = 0;
    const fdaErrors: string[] = [];

    for (const fdaItem of fdaData) {
      try {
        await fdaReportRepo.insert({
          filename: fdaItem.filename,
          success: fdaItem.success,
          controlledTrialText: fdaItem.data.controlled_trial_text,
          symptomsList: fdaItem.data.symptoms_list,
          studyType: fdaItem.data.study_type,
          sourceSection: fdaItem.data.source_section,
          fullPdfText: fdaItem.data.full_pdf_text,
          rawResponse: fdaItem.raw_response
        });
        fdaImported++;
      } catch (error) {
        fdaErrors.push(`Failed to import FDA report ${fdaItem.filename}: ${error}`);
      }
    }

    console.log(`✅ Successfully imported ${fdaImported} FDA reports`);

    if (fdaErrors.length > 0) {
      console.log('⚠️  FDA import errors:');
      fdaErrors.forEach(error => console.log(`   - ${error}`));
    }

    // Log some statistics
    const reports = await db.query.vaersReports.findMany();
    const vaccines = await db.query.vaersVaccines.findMany();
    const symptoms = await db.query.vaersSymptoms.findMany();
    const fdaReports = await db.query.fdaReports.findMany();

    console.log('\n📈 Database Statistics:');
    console.log(`   - Total VAERS Reports: ${reports.length}`);
    console.log(`   - Total Vaccines: ${vaccines.length}`);
    console.log(`   - Total Symptoms: ${symptoms.length}`);
    console.log(`   - Total FDA Reports: ${fdaReports.length}`);

    // Show sample data
    console.log('\n📋 Sample VAERS Report:');
    if (reports.length > 0 && reports[0]) {
      const sampleReport = await reportRepo.getReportWithDetails(reports[0].id);
      if (sampleReport) {
        console.log(`   - VAERS ID: ${sampleReport.vaersId}`);
        console.log(`   - State: ${sampleReport.state}`);
        console.log(`   - Age: ${sampleReport.ageYrs}`);
        console.log(`   - Vaccines: ${sampleReport.vaccines.length}`);
        console.log(`   - Symptoms: ${sampleReport.symptoms.length}`);
      }
    }

    console.log('\n📋 Sample FDA Report:');
    if (fdaReports.length > 0) {
      const sampleFdaReport = fdaReports[0];
      if (sampleFdaReport) {
        console.log(`   - Filename: ${sampleFdaReport.filename}`);
        console.log(`   - Study Type: ${sampleFdaReport.studyType}`);
        console.log(`   - Source Section: ${sampleFdaReport.sourceSection}`);
        console.log(`   - Symptoms: ${sampleFdaReport.symptomsList.length}`);
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