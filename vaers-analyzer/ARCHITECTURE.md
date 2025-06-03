# VAERS Analyzer Architecture

## Overview

The VAERS Analyzer is an AI-powered system that helps users analyze vaccine adverse event reports by comparing them against FDA-validated data and similar historical reports.

## Core User Flow

1. **Report Input** → User enters/selects a VAERS report
2. **AI Analysis** → System searches FDA data and similar reports
3. **Live Progress** → Shows search steps in real-time
4. **Structured Report** → Presents findings with validation status

## Technical Architecture

### Frontend Structure (Next.js App Router)

```
apps/web/app/
├── reports/
│   ├── page.tsx                 # Browse all reports
│   ├── new/
│   │   └── page.tsx            # New report form
│   └── [id]/
│       ├── page.tsx            # View single report
│       └── analyze/
│           └── page.tsx        # Analysis results
├── api/
│   ├── analyze/
│   │   └── route.ts           # Streaming analysis endpoint
│   ├── reports/
│   │   ├── route.ts           # CRUD operations
│   │   └── [id]/
│   │       └── route.ts
│   └── mcp/
│       └── fda/
│           └── route.ts       # MCP server proxy
└── components/
    ├── report-form/
    │   ├── ReportForm.tsx     # Main form component
    │   ├── VaccineInput.tsx   # Multi-vaccine input
    │   └── SymptomSelector.tsx
    ├── search/
    │   ├── SearchProgress.tsx  # Real-time search UI
    │   ├── SearchStep.tsx      # Individual step display
    │   └── SearchResults.tsx
    └── analysis/
        ├── AnalysisReport.tsx  # Final report display
        ├── FdaValidation.tsx   # FDA data section
        └── RelatedReports.tsx  # Similar reports section
```

### Backend Architecture

#### 1. API Routes Structure

```typescript
// app/api/analyze/route.ts
export async function POST(request: Request) {
  const { reportId, reportData } = await request.json();
  
  // Return streaming response
  return new Response(
    new ReadableStream({
      async start(controller) {
        // Stream search steps to client
        await performAnalysis(reportData, controller);
      }
    }),
    {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    }
  );
}
```

#### 2. Analysis Pipeline

```typescript
// packages/analyzer/src/pipeline.ts
export class VaersAnalysisPipeline {
  constructor(
    private llm: LLMProvider,
    private mcpClient: MCPClient,
    private db: DatabaseClient
  ) {}

  async analyze(report: VaersReport, stream: StreamController) {
    // Step 1: Extract key information
    await stream.emit('step', {
      id: 1,
      title: 'Extracting vaccine and symptom information',
      status: 'in-progress'
    });
    
    const extracted = await this.extractKeyInfo(report);
    
    // Step 2: Search FDA database
    await stream.emit('step', {
      id: 2,
      title: 'Searching FDA validated data',
      status: 'in-progress'
    });
    
    const fdaResults = await this.searchFDA(extracted);
    
    // Step 3: Find similar reports
    await stream.emit('step', {
      id: 3,
      title: 'Finding similar VAERS reports',
      status: 'in-progress'
    });
    
    const similarReports = await this.findSimilarReports(extracted);
    
    // Step 4: Generate analysis
    await stream.emit('step', {
      id: 4,
      title: 'Generating comprehensive analysis',
      status: 'in-progress'
    });
    
    const analysis = await this.generateAnalysis({
      report,
      fdaResults,
      similarReports
    });
    
    return analysis;
  }
}
```

### MCP Server Integration

#### 1. MCP Tools Definition

```typescript
// packages/mcp-tools/src/fda-tools.ts
export const fdaTools = {
  searchValidatedSymptoms: {
    description: "Search FDA validated symptoms for a vaccine",
    parameters: {
      vaccine: { type: "string" },
      symptoms: { type: "array", items: { type: "string" } }
    }
  },
  
  getControlledTrialData: {
    description: "Get controlled trial text for deeper analysis",
    parameters: {
      vaccine: { type: "string" },
      indication: { type: "string" }
    }
  }
};
```

#### 2. MCP Client Wrapper

```typescript
// packages/analyzer/src/mcp-client.ts
export class MCPClient {
  async searchFDA(params: FDASearchParams) {
    const response = await fetch('/api/mcp/fda', {
      method: 'POST',
      body: JSON.stringify({
        tool: 'searchValidatedSymptoms',
        params
      })
    });
    
    return response.json();
  }
}
```

### Database Schema Updates

```sql
-- Add indexes for efficient vaccine searching
CREATE INDEX idx_vaccines_type_manu ON vaers_vaccines(vax_type, vax_manufacturer);
CREATE INDEX idx_symptoms_name ON vaers_symptoms(symptom_name);

-- Add full-text search on symptom text
CREATE INDEX idx_reports_symptom_text ON vaers_reports 
USING gin(to_tsvector('english', symptom_text));

-- Add similarity search capability
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_symptoms_similarity ON vaers_symptoms 
USING gin(symptom_name gin_trgm_ops);
```

### Real-time Search UI

```typescript
// components/search/SearchProgress.tsx
export function SearchProgress({ analysisId }: { analysisId: string }) {
  const [steps, setSteps] = useState<SearchStep[]>([]);
  
  useEffect(() => {
    const eventSource = new EventSource(`/api/analyze?id=${analysisId}`);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'step') {
        setSteps(prev => [...prev, data.step]);
      }
    };
    
    return () => eventSource.close();
  }, [analysisId]);
  
  return (
    <div className="space-y-4">
      {steps.map(step => (
        <SearchStep key={step.id} step={step} />
      ))}
    </div>
  );
}
```

### Report Generation

```typescript
// packages/analyzer/src/report-generator.ts
export class ReportGenerator {
  generateReport(analysis: AnalysisResult): StructuredReport {
    return {
      summary: this.generateSummary(analysis),
      disclaimer: "VAERS reports are unverified and may contain errors...",
      
      sections: [
        {
          title: "FDA Validated Information",
          content: this.formatFDAFindings(analysis.fdaResults),
          confidence: analysis.fdaResults.matchConfidence
        },
        {
          title: "Similar VAERS Reports",
          content: this.formatSimilarReports(analysis.similarReports),
          links: analysis.similarReports.map(r => ({
            vaersId: r.vaersId,
            similarity: r.similarityScore
          }))
        },
        {
          title: "Analysis Summary",
          content: this.generateAnalysisSummary(analysis),
          recommendations: analysis.recommendations
        }
      ],
      
      metadata: {
        searchedDatabases: ['FDA Labels', 'FDA Trials', 'VAERS Historical'],
        analysisDate: new Date(),
        confidenceLevel: analysis.overallConfidence
      }
    };
  }
}
```

## Implementation Steps

### Phase 1: Core Infrastructure
1. Set up report browsing and form UI
2. Implement basic CRUD operations
3. Add example reports to database

### Phase 2: MCP Integration
1. Create MCP server with FDA tools
2. Set up proxy endpoints
3. Test FDA data retrieval

### Phase 3: Analysis Pipeline
1. Implement LLM integration
2. Create analysis orchestration
3. Add streaming responses

### Phase 4: Search UI
1. Build real-time progress components
2. Implement step visualization
3. Add error handling

### Phase 5: Report Generation
1. Create structured report format
2. Build report display components
3. Add export functionality

## Key Design Decisions

1. **Streaming Architecture**: Use Server-Sent Events for real-time updates
2. **MCP for FDA Access**: Leverage MCP tools for reliable FDA data access
3. **LLM Orchestration**: Use LLM to intelligently decide which searches to perform
4. **Modular Pipeline**: Each analysis step is independent and testable
5. **Emphasis on Validation**: Always show what was searched, even if no matches found

## Security Considerations

1. Validate all user inputs
2. Rate limit analysis requests
3. Sanitize report content
4. Implement proper authentication
5. Log all FDA data access

## Performance Optimizations

1. Cache FDA search results
2. Use database indexes for similarity search
3. Implement request debouncing
4. Lazy load report details
5. Stream results as available

## Error Handling

1. Graceful MCP server failures
2. LLM timeout handling
3. Partial result display
4. User-friendly error messages
5. Automatic retry logic