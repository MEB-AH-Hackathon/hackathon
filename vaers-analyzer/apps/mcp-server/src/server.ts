import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { fdaTools, ToolName } from '@vaers/mcp-tools';
import { FdaReportRepository } from '@vaers/database';

const app = express();
app.use(cors());
app.use(express.json());

const fdaRepo = new FdaReportRepository();

app.post('/fda', async (req, res) => {
  const { tool, params } = req.body as { tool: ToolName; params: any };
  if (!tool || !(tool in fdaTools)) {
    return res.status(400).json({ error: 'Invalid tool' });
  }

  try {
    let result;

    switch (tool) {
      case 'searchValidatedSymptoms':
        const { vaccine, symptoms } = params;
        if (!vaccine || !symptoms) {
          return res.status(400).json({ error: 'Missing vaccine or symptoms' });
        }
        
        // Search for FDA reports containing these symptoms
        const symptomResults = await Promise.all(
          symptoms.map((symptom: string) => fdaRepo.searchByAdverseEvent(symptom))
        );
        
        // Flatten and deduplicate results
        const allResults = [...new Map(
          symptomResults.flat().map(report => [report.id, report])
        ).values()];
        
        result = {
          vaccine,
          symptoms,
          foundReports: allResults.length,
          reports: allResults.map(report => ({
            id: report.id,
            vaccineName: report.vaccineName,
            manufacturer: report.manufacturer,
            adverseEvents: report.adverseEvents,
            pdfFile: report.pdfFile
          }))
        };
        break;

      case 'getControlledTrialData':
        const { vaccine: trialVaccine, indication } = params;
        if (!trialVaccine || !indication) {
          return res.status(400).json({ error: 'Missing vaccine or indication' });
        }
        
        // Search FDA reports by vaccine name
        const trialResults = await fdaRepo.searchVaccineNames(trialVaccine);
        const filteredResults = trialResults.filter(report => 
          report.adverseEvents.some(event => 
            event.toLowerCase().includes(indication.toLowerCase())
          )
        );
        
        result = {
          vaccine: trialVaccine,
          indication,
          foundReports: filteredResults.length,
          trialData: filteredResults.map(report => ({
            id: report.id,
            vaccineName: report.vaccineName,
            manufacturer: report.manufacturer,
            adverseEvents: report.adverseEvents,
            pdfFile: report.pdfFile
          }))
        };
        break;

      default:
        return res.status(400).json({ error: 'Unknown tool' });
    }

    res.json({ tool, params, result });
  } catch (error) {
    console.error('FDA tool error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

const port = process.env.PORT || 3001;
app.listen(port, () => {
  console.log(`MCP server listening on port ${port}`);
});
