import type { VaersReport } from '@vaers/types';
import { MCPClient } from './mcp-client';

export interface AnalysisStep {
  id: number;
  title: string;
  status: 'pending' | 'in-progress' | 'complete';
}

export class VaersAnalysisPipeline {
  constructor(private mcp: MCPClient) {}

  async analyze(report: VaersReport, onStep?: (step: AnalysisStep) => void) {
    const steps: AnalysisStep[] = [
      { id: 1, title: 'Extracting key info', status: 'pending' },
      { id: 2, title: 'Searching FDA database', status: 'pending' }
    ];

    for (const step of steps) {
      step.status = 'in-progress';
      onStep?.(step);
      // TODO: call MCP and perform analysis
      step.status = 'complete';
      onStep?.(step);
    }

    return { success: true };
  }
}
