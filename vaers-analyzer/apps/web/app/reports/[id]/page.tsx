import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getReportById } from '../../actions/reports';
import { ReportDetails } from './components/ReportDetails';
import { AnalyzeButton } from './components/AnalyzeButton';

export default async function ReportPage({
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
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <Link
          href="/reports"
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
        >
          <svg className="mr-1 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Reports
        </Link>
        
        <div className="mt-4 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-light text-gray-900 dark:text-white">
              VAERS Report Details
            </h1>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Review adverse event report and analyze with AI
            </p>
          </div>
          
          <div className="flex space-x-3">
            <AnalyzeButton reportId={report.id} />
            
            <Link
              href={`/reports/${report.id}/edit`}
              className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg className="mr-2 -ml-1 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Edit
            </Link>
          </div>
        </div>
      </div>

      <ReportDetails report={report} />
      
      {/* Disclaimer */}
      <div className="mt-8 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
              Important Notice About VAERS Data
            </h3>
            <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
              <p>
                VAERS reports are unverified and may contain errors, omissions, or coincidental events. 
                Reports do not establish causation between vaccines and adverse events. 
                This tool is for analysis purposes only and should not be used for medical decisions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}