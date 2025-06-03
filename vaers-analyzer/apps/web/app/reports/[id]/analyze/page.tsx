import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getReportById } from '../../../actions/reports';

export default async function AnalyzePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const reportId = parseInt(id);
  
  if (isNaN(reportId)) {
    notFound();
  }

  const report = await getReportById(reportId);
  
  if (!report) {
    notFound();
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <Link
          href={`/reports/${reportId}`}
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
        >
          <svg className="mr-1 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Report
        </Link>
        
        <h1 className="mt-4 text-3xl font-light text-gray-900 dark:text-white">
          AI Analysis Results
        </h1>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          VAERS Report {report.vaersId} Analysis
        </p>
      </div>

      {/* Phase 2 Placeholder */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-8 text-center">
        <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 dark:bg-blue-900/30">
          <svg className="h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">
          AI Analysis Coming Soon
        </h3>
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 max-w-md mx-auto">
          This is where the AI-powered analysis will appear in Phase 2. The system will search FDA databases, 
          find similar reports, and provide a comprehensive analysis.
        </p>
        
        <div className="mt-6 bg-gray-50 dark:bg-gray-900 rounded-lg p-4 text-left">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
            Planned Features:
          </h4>
          <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            <li>• Real-time search progress visualization</li>
            <li>• FDA-validated symptom comparison</li>
            <li>• Similar VAERS report matching</li>
            <li>• Controlled trial data analysis</li>
            <li>• Structured confidence scoring</li>
            <li>• Safety signal detection</li>
          </ul>
        </div>
        
        <div className="mt-6">
          <Link
            href={`/reports/${reportId}`}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Return to Report
          </Link>
        </div>
      </div>
    </div>
  );
}