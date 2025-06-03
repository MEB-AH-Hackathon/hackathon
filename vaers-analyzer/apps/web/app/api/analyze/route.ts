import { NextRequest } from 'next/server';
import { 
  VaersAnalysisPipeline, 
  LLMProvider, 
  MCPClient, 
  ReportGenerator,
  type StreamController 
} from '@vaers/analyzer';
import type { VaersReport, ValidationStatus, Sex, RecoveryStatus, ReportStatus } from '@vaers/types';
import { 
  VaersReportRepository,
  SymptomMappingRepository,
  FdaReportRepository
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
    const symptomMappingRepo = new SymptomMappingRepository();
    const fdaReportRepo = new FdaReportRepository();

    // Get the report
    const report = await reportRepo.getById(reportId);
    if (!report) {
      return Response.json({ error: 'Report not found' }, { status: 404 });
    }

    // Create a ReadableStream for Server-Sent Events
    const stream = new ReadableStream({
      async start(controller) {
        const encoder = new TextEncoder();
        
        // Create stream controller that sends SSE format
        const streamController: StreamController = {
          emit: async (event: string, data: unknown) => {
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
            symptomMappingRepo,
            fdaReportRepo
          );

          // Transform the report to match VaersReport type
          const vaersReport: VaersReport = {
            ...report,
            vaersId: String(report.vaersId),
            recvDate: report.recvDate ? new Date(report.recvDate) : undefined,
            state: report.state || undefined,
            ageYrs: report.ageYrs ? Number(report.ageYrs) : undefined,
            sex: (report.sex as Sex) || undefined,
            symptomText: report.symptomText || undefined,
            died: report.died || false,
            lThreat: report.lThreat || false,
            erVisit: report.erVisit || false,
            hospital: report.hospital || false,
            disable: report.disable || false,
            recovd: (report.recovd as RecoveryStatus) || undefined,
            vaxDate: report.vaxDate ? new Date(report.vaxDate) : undefined,
            onsetDate: report.onsetDate ? new Date(report.onsetDate) : undefined,
            numDays: report.numDays ? Number(report.numDays) : undefined,
            status: report.status as ReportStatus,
            vaccines: (report.vaxTypeList || []).map((type: string, i: number) => ({
              id: i,
              reportId: report.id,
              vaxType: type,
              vaxManufacturer: report.vaxManuList?.[i],
              vaxName: report.vaxNameList?.[i],
              vaxDoseSeries: report.vaxDoseSeriesList?.[i],
              vaxRoute: report.vaxRouteList?.[i],
              vaxSite: report.vaxSiteList?.[i],
              createdAt: report.createdAt
            })),
            symptoms: (report.symptomList || []).map((symptom: string, i: number) => ({
              id: i,
              reportId: report.id,
              symptomName: symptom,
              validationStatus: 'unvalidated' as ValidationStatus,
              createdAt: report.createdAt
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