import type { VaersReport } from '@vaers/types';
import { ReportListItem } from './ReportListItem';

interface ReportListProps {
  reports: VaersReport[];
}

export function ReportList({ reports }: ReportListProps) {
  if (reports.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow rounded-md p-6 text-center">
        <p className="text-gray-500 dark:text-gray-400">
          No reports found. Try adjusting your filters or create a new report.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
      <ul className="divide-y divide-gray-200 dark:divide-gray-700">
        {reports.map((report) => (
          <ReportListItem key={report.id} report={report} />
        ))}
      </ul>
    </div>
  );
}