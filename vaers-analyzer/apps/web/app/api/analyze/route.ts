import { NextRequest } from 'next/server';
import { 
  VaersAnalysisPipeline, 
  LLMProvider, 
  MCPClient, 
  ReportGenerator,
  type StreamController 
} from '@vaers/analyzer';
import type { VaersReport, SymptomSeverity, ValidationStatus, Sex, RecoveryStatus, ReportStatus } from '@vaers/types';
import { 
  VaersReportRepository, 
  VaersSymptomRepository,
  VaersVaccineRepository 
} from '@vaers/database';

/**
 * POST handler for streaming analysis endpoint
 */
export async function POST(request: NextRequest) {
  try {
    const { reportId } = await request.json();
    
    if (!reportId) {
      return Response.json({ error: 'Missing reportId' }, { status: 400 });
    }

    // Initialize repositories
    const reportRepo = new VaersReportRepository();
    const symptomRepo = new VaersSymptomRepository();
    const vaccineRepo = new VaersVaccineRepository();

    // Get the report with details
    const report = await reportRepo.getReportWithDetails(reportId);
    if (!report) {
      return Response.json({ error: 'Report not found' }, { status: 404 });
    }

    // Create a ReadableStream for Server-Sent Events
    const stream = new ReadableStream({
      async start(controller) {
        const encoder = new TextEncoder();
        
        // Create stream controller that sends SSE format
        const streamController: StreamController = {
          emit: async (event: string, data: any) => {
            const message = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
            controller.enqueue(encoder.encode(message));
          }
        };

        try {
          // Initialize pipeline components
          const llm = new LLMProvider();
          const mcpClient = new MCPClient(process.env.MCP_SERVER_URL || 'http://localhost:3001');
          const pipeline = new VaersAnalysisPipeline(
            llm,
            mcpClient,
            reportRepo,
            symptomRepo,
            vaccineRepo
          );

          // Transform the report to match VaersReport type (null -> undefined)
          const vaersReport: VaersReport = {
            ...report,
            recvDate: report.recvDate || undefined,
            state: report.state || undefined,
            ageYrs: report.ageYrs ? Number(report.ageYrs) : undefined,
            sex: (report.sex as Sex) || undefined,
            symptomText: report.symptomText || undefined,
            died: report.died || undefined,
            lThreat: report.lThreat || undefined,
            erVisit: report.erVisit || undefined,
            hospital: report.hospital || undefined,
            disable: report.disable || undefined,
            recovd: (report.recovd as RecoveryStatus) || undefined,
            vaxDate: report.vaxDate || undefined,
            onsetDate: report.onsetDate || undefined,
            numDays: report.numDays || undefined,
            status: report.status as ReportStatus,
            vaccines: (report.vaccines || []).map(v => ({
              ...v,
              vaxType: v.vaxType || undefined,
              vaxManufacturer: v.vaxManufacturer || undefined,
              vaxName: v.vaxName || undefined,
              vaxDoseSeries: v.vaxDoseSeries || undefined,
              vaxRoute: v.vaxRoute || undefined,
              vaxSite: v.vaxSite || undefined
            })),
            symptoms: (report.symptoms || []).map(s => ({
              ...s,
              severity: (s.severity as SymptomSeverity) || undefined,
              validationStatus: s.validationStatus as ValidationStatus,
              fdaReference: s.fdaReference || undefined
            }))
          };

          // Run analysis
          const analysisResult = await pipeline.analyze(vaersReport, streamController);
          
          // Generate structured report
          const reportGenerator = new ReportGenerator();
          const structuredReport = reportGenerator.generateReport(analysisResult);
          
          // Send final report
          await streamController.emit('complete', structuredReport);
          
        } catch (error) {
          console.error('Analysis error:', error);
          await streamController.emit('error', { 
            message: 'Analysis failed',
            error: error instanceof Error ? error.message : 'Unknown error'
          });
        } finally {
          controller.close();
        }
      }
    });

    // Return streaming response with proper headers
    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-transform',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no', // Disable Nginx buffering
      },
    });
    
  } catch (error) {
    console.error('API error:', error);
    return Response.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}