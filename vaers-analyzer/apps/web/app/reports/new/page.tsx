import Link from 'next/link';
import { ReportForm } from './components/ReportForm';

export default function NewReportPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
        
        <h1 className="mt-4 text-3xl font-light text-gray-900 dark:text-white">
          Submit New VAERS Report
        </h1>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Enter vaccine adverse event information for AI-powered analysis
        </p>
      </div>

      <ReportForm />
    </div>
  );
}