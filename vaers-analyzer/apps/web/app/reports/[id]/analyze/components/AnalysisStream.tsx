'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, IconContainer } from '../../../../../components/ui';
import type { AnalysisStep, StructuredReport } from '@vaers/analyzer';

interface AnalysisStreamProps {
  reportId: number;
}

export function AnalysisStream({ reportId }: AnalysisStreamProps) {
  const [steps, setSteps] = useState<AnalysisStep[]>([]);
  const [report, setReport] = useState<StructuredReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const startAnalysis = useCallback(async () => {
    setIsAnalyzing(true);
    setSteps([]);
    setReport(null);
    setError(null);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reportId })
      });

      if (!response.ok) {
        throw new Error('Failed to start analysis');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            const event = line.slice(7);
            const dataLine = lines[lines.indexOf(line) + 1];
            if (dataLine?.startsWith('data: ')) {
              const data = JSON.parse(dataLine.slice(6));
              
              if (event === 'step') {
                setSteps(prev => {
                  const existing = prev.findIndex(s => s.id === data.id);
                  if (existing >= 0) {
                    const updated = [...prev];
                    updated[existing] = data;
                    return updated;
                  }
                  return [...prev, data];
                });
              } else if (event === 'complete') {
                setReport(data);
                setIsAnalyzing(false);
              } else if (event === 'error') {
                setError(data.message);
                setIsAnalyzing(false);
              }
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      setIsAnalyzing(false);
    }
  }, [reportId]);

  useEffect(() => {
    startAnalysis();
  }, [startAnalysis]);

  return (
    <div className="space-y-8">
      {/* Progress Steps */}
      {steps.length > 0 && (
        <Card variant="elevated" size="xlarge">
          <CardContent className="p-8">
            <h3 className="text-xl font-semibold text-stone-900 dark:text-stone-100 mb-6">
              Analysis Progress
            </h3>
            <div className="space-y-4">
              {steps.map(step => (
                <div key={step.id} className="flex items-start space-x-4">
                  <div className="flex-shrink-0 mt-1">
                    {step.status === 'completed' && (
                      <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    )}
                    {step.status === 'in-progress' && (
                      <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center animate-pulse">
                        <div className="w-3 h-3 bg-white rounded-full"></div>
                      </div>
                    )}
                    {step.status === 'error' && (
                      <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </div>
                    )}
                    {step.status === 'pending' && (
                      <div className="w-6 h-6 bg-stone-300 dark:bg-stone-600 rounded-full"></div>
                    )}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-stone-900 dark:text-stone-100">
                      {step.title}
                    </h4>
                    {step.details && (
                      <p className="text-sm text-stone-600 dark:text-stone-400 mt-1">
                        {step.details}
                      </p>
                    )}
                    {step.error && (
                      <p className="text-sm text-red-600 dark:text-red-400 mt-1">
                        {step.error}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Card variant="elevated" size="xlarge" className="border-red-200 dark:border-red-800">
          <CardContent className="p-8">
            <div className="flex items-center space-x-4">
              <IconContainer
                variant="red"
                size="lg"
                icon={
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                }
              />
              <div>
                <h3 className="text-lg font-semibold text-red-900 dark:text-red-100">
                  Analysis Failed
                </h3>
                <p className="text-red-700 dark:text-red-300 mt-1">{error}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Final Report */}
      {report && (
        <div className="space-y-8">
          {/* Summary */}
          <Card variant="elevated" size="xlarge">
            <CardContent className="p-8">
              <h3 className="text-xl font-semibold text-stone-900 dark:text-stone-100 mb-4">
                Analysis Summary
              </h3>
              <p className="text-stone-700 dark:text-stone-300 leading-relaxed mb-6">
                {report.summary}
              </p>
              
              {/* Confidence Badge */}
              <div className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium"
                   style={{
                     backgroundColor: report.metadata.confidenceLevel === 'high' ? '#10b981' :
                                    report.metadata.confidenceLevel === 'medium' ? '#f59e0b' : '#ef4444',
                     color: 'white'
                   }}>
                {report.metadata.confidenceLevel.toUpperCase()} CONFIDENCE
              </div>
            </CardContent>
          </Card>

          {/* Disclaimer */}
          <Card variant="muted" size="xlarge">
            <CardContent className="p-6">
              <div className="flex items-start space-x-3">
                <svg className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <p className="text-sm text-stone-600 dark:text-stone-400 italic">
                  {report.disclaimer}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Report Sections */}
          {report.sections.map((section, index) => (
            <Card key={index} variant="elevated" size="xlarge">
              <CardContent className="p-8">
                <h3 className="text-xl font-semibold text-stone-900 dark:text-stone-100 mb-4">
                  {section.title}
                </h3>
                <div className="prose prose-stone dark:prose-invert max-w-none">
                  <div dangerouslySetInnerHTML={{ __html: section.content.replace(/\n/g, '<br />') }} />
                </div>
                
                {section.links && section.links.length > 0 && (
                  <div className="mt-6 pt-6 border-t border-stone-200 dark:border-stone-700">
                    <h4 className="text-sm font-medium text-stone-600 dark:text-stone-400 mb-3">
                      Related Reports
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {section.links.map((link, i) => (
                        <a
                          key={i}
                          href={`/reports?vaersId=${link.vaersId}`}
                          className="inline-flex items-center px-3 py-1 text-sm bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 rounded-lg hover:bg-stone-200 dark:hover:bg-stone-700 transition-colors"
                        >
                          {link.vaersId}
                          <span className="ml-2 text-xs text-stone-500 dark:text-stone-400">
                            {Math.round(link.similarity * 100)}%
                          </span>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}

          {/* Metadata */}
          <Card variant="default" size="xlarge">
            <CardContent className="p-6">
              <div className="flex flex-wrap gap-6 text-sm">
                <div>
                  <span className="text-stone-500 dark:text-stone-400">Analysis Date:</span>
                  <span className="ml-2 text-stone-700 dark:text-stone-300">
                    {new Date(report.metadata.analysisDate).toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-stone-500 dark:text-stone-400">Databases Searched:</span>
                  <span className="ml-2 text-stone-700 dark:text-stone-300">
                    {report.metadata.searchedDatabases.join(', ')}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Loading State */}
      {isAnalyzing && steps.length === 0 && (
        <Card variant="elevated" size="xlarge">
          <CardContent className="p-12 text-center">
            <div className="animate-spin w-12 h-12 border-4 border-stone-300 dark:border-stone-600 border-t-blue-500 rounded-full mx-auto mb-4"></div>
            <p className="text-stone-600 dark:text-stone-400">
              Initializing analysis...
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}