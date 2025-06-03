import Link from 'next/link';

export function ReportsHeader() {
  return (
    <div className="sm:flex sm:items-center sm:justify-between mb-8">
      <div>
        <h1 className="text-3xl font-light text-gray-900 dark:text-white">
          VAERS Reports
        </h1>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Browse and analyze vaccine adverse event reports
        </p>
      </div>
      <div className="mt-4 sm:mt-0">
        <Link
          href="/reports/new"
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
        >
          <svg className="mr-2 -ml-1 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
          Submit New Report
        </Link>
      </div>
    </div>
  );
}