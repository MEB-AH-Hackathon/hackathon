import { MCPClient } from '../mcp-client';
import { LLMProvider } from './llm-provider';
import { 
  VaersReportRepository, 
  VaersSymptomRepository,
  VaersVaccineRepository 
} from '@vaers/database';
import type { VaersReport } from '@vaers/types';
import type { 
  StreamController, 
  AnalysisStep, 
  ExtractedInfo, 
  FDASearchResult,
  SimilarReport,
  AnalysisResult 
} from '../types';

export class VaersAnalysisPipeline {
  constructor(
    private llm: LLMProvider,
    private mcpClient: MCPClient,
    private reportRepo: VaersReportRepository,
    private symptomRepo: VaersSymptomRepository,
    private vaccineRepo: VaersVaccineRepository
  ) {}

  async analyze(report: VaersReport, stream: StreamController): Promise<AnalysisResult> {
    // Step 1: Extract key information
    await stream.emit('step', {
      id: 1,
      title: 'Extracting vaccine and symptom information',
      status: 'in-progress'
    } as AnalysisStep);

    let extracted: ExtractedInfo;
    try {
      const reportText = `
        Patient: ${report.ageYrs || 'Unknown'} years old, ${report.sex || 'Unknown'} sex
        Vaccines: ${report.vaccines?.map(v => `${v.vaxType} (${v.vaxManufacturer})`).join(', ') || 'Unknown'}
        Symptoms: ${report.symptomText || ''}
        Outcomes: 
        - Died: ${report.died ? 'Yes' : 'No'}
        - Life Threatening: ${report.lThreat ? 'Yes' : 'No'}
        - Hospitalized: ${report.hospital ? 'Yes' : 'No'}
        - Disabled: ${report.disable ? 'Yes' : 'No'}
        - ER Visit: ${report.erVisit ? 'Yes' : 'No'}
        Days to onset: ${report.numDays || 'Unknown'}
      `;

      const llmExtracted = await this.llm.extractKeyInformation(reportText);
      
      extracted = {
        vaccines: llmExtracted.vaccines || report.vaccines?.map(v => ({
          type: v.vaxType,
          manufacturer: v.vaxManufacturer,
          dose: v.vaxDoseSeries || undefined
        })) || [],
        symptoms: llmExtracted.symptoms || [],
        outcomes: {
          died: report.died || false,
          lifeThreatening: report.lThreat || false,
          hospitalized: report.hospital || false,
          disabled: report.disable || false,
          emergencyRoom: report.erVisit || false
        },
        onsetDays: report.numDays,
        patientInfo: {
          age: report.ageYrs,
          sex: report.sex
        }
      };

      await stream.emit('step', {
        id: 1,
        title: 'Extracting vaccine and symptom information',
        status: 'completed',
        details: `Found ${extracted.vaccines.length} vaccines and ${extracted.symptoms.length} symptoms`
      } as AnalysisStep);
    } catch (error) {
      await stream.emit('step', {
        id: 1,
        title: 'Extracting vaccine and symptom information',
        status: 'error',
        error: 'Failed to extract information'
      } as AnalysisStep);
      throw error;
    }

    // Step 2: Search FDA database
    await stream.emit('step', {
      id: 2,
      title: 'Searching FDA validated data',
      status: 'in-progress'
    } as AnalysisStep);

    let fdaResults: FDASearchResult[] = [];
    try {
      for (const vaccine of extracted.vaccines) {
        const result = await this.mcpClient.call('searchValidatedSymptoms', {
          vaccine: vaccine.type,
          symptoms: extracted.symptoms
        }) as any;

        if (result?.result) {
          fdaResults.push(result.result);
        }
      }

      await stream.emit('step', {
        id: 2,
        title: 'Searching FDA validated data',
        status: 'completed',
        details: `Found ${fdaResults.reduce((acc, r) => acc + r.foundReports, 0)} FDA reports`
      } as AnalysisStep);
    } catch (error) {
      await stream.emit('step', {
        id: 2,
        title: 'Searching FDA validated data',
        status: 'error',
        error: 'Failed to search FDA database'
      } as AnalysisStep);
    }

    // Step 3: Find similar reports
    await stream.emit('step', {
      id: 3,
      title: 'Finding similar VAERS reports',
      status: 'in-progress'
    } as AnalysisStep);

    let similarReports: SimilarReport[] = [];
    try {
      // Search for reports with similar symptoms
      const searchTerms = await this.llm.findRelevantSearchTerms(extracted);
      const symptomMatches = new Map<string, Set<string>>();

      for (const term of searchTerms) {
        const reports = await this.symptomRepo.findReportsBySymptom(term);
        for (const report of reports) {
          if (!symptomMatches.has(report.vaersId)) {
            symptomMatches.set(report.vaersId, new Set());
          }
          symptomMatches.get(report.vaersId)!.add(term);
        }
      }

      // Calculate similarity scores
      const reportScores = Array.from(symptomMatches.entries())
        .map(([vaersId, matchedTerms]) => ({
          vaersId,
          matchedSymptoms: Array.from(matchedTerms),
          similarityScore: matchedTerms.size / searchTerms.length
        }))
        .filter(r => r.vaersId !== report.vaersId)
        .sort((a, b) => b.similarityScore - a.similarityScore)
        .slice(0, 10);

      // Get full report details for top matches
      for (const scoreData of reportScores) {
        const fullReport = await this.reportRepo.getByVaersId(scoreData.vaersId);
        if (fullReport) {
          const reportWithDetails = await this.reportRepo.getReportWithDetails(fullReport.id);
          if (reportWithDetails) {
            similarReports.push({
              vaersId: scoreData.vaersId,
              similarityScore: scoreData.similarityScore,
              matchedSymptoms: scoreData.matchedSymptoms,
              vaccines: reportWithDetails.vaccines.map(v => v.vaxType || '').filter(Boolean),
              outcomes: [
                reportWithDetails.died && 'Death',
                reportWithDetails.lThreat && 'Life Threatening',
                reportWithDetails.hospital && 'Hospitalized',
                reportWithDetails.disable && 'Disabled',
                reportWithDetails.erVisit && 'ER Visit'
              ].filter(Boolean) as string[]
            });
          }
        }
      }

      await stream.emit('step', {
        id: 3,
        title: 'Finding similar VAERS reports',
        status: 'completed',
        details: `Found ${similarReports.length} similar reports`
      } as AnalysisStep);
    } catch (error) {
      await stream.emit('step', {
        id: 3,
        title: 'Finding similar VAERS reports',
        status: 'error',
        error: 'Failed to find similar reports'
      } as AnalysisStep);
    }

    // Step 4: Generate analysis
    await stream.emit('step', {
      id: 4,
      title: 'Generating comprehensive analysis',
      status: 'in-progress'
    } as AnalysisStep);

    try {
      const analysis = await this.llm.generateAnalysis({
        report,
        fdaResults,
        similarReports
      });

      await stream.emit('step', {
        id: 4,
        title: 'Generating comprehensive analysis',
        status: 'completed'
      } as AnalysisStep);

      return {
        report,
        extractedInfo: extracted,
        fdaResults,
        similarReports,
        overallConfidence: analysis.overallConfidence || 'low',
        recommendations: analysis.recommendations || []
      };
    } catch (error) {
      await stream.emit('step', {
        id: 4,
        title: 'Generating comprehensive analysis',
        status: 'error',
        error: 'Failed to generate analysis'
      } as AnalysisStep);
      throw error;
    }
  }
}