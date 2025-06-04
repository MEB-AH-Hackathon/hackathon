"use client";

import { useState, useEffect } from 'react';
import { getExampleReports } from '../../../actions/reports';
import type { VaersReport } from '@vaers/types';

interface ExampleReportsProps {
  onSelect: (report: VaersReport) => void;
}

export function ExampleReports({ onSelect }: ExampleReportsProps) {
  const [examples, setExamples] = useState<VaersReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getExampleReports(5)
      .then(setExamples)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
        <p className="text-sm text-gray-500 dark:text-gray-400">Loading example reports...</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 space-y-3">
      <h3 className="text-sm font-medium text-gray-900 dark:text-white">
        Or start with an example report:
      </h3>
      <div className="space-y-2">
        {examples.map((report) => (
          <button
            key={report.id}
            type="button"
            onClick={() => onSelect(report)}
            className="w-full text-left p-3 bg-white dark:bg-gray-700 rounded-md hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  VAERS ID: {report.vaersId}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {report.vaccines.map(v => v.vaxType).filter(Boolean).join(', ')} • 
                  {' '}{report.symptoms.length} symptoms
                </p>
              </div>
              <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}