import type { VaersReport } from '@vaers/types';
import { ReportListItem } from './ReportListItem';
import { Card, CardContent } from '../../../components/ui';

interface ReportListProps {
  reports: VaersReport[];
}

export function ReportList({ reports }: ReportListProps) {
  if (reports.length === 0) {
    return (
      <Card variant="elevated" size="large" className="text-center">
        <CardContent className="p-12">
          <p className="text-stone-500 dark:text-stone-400 text-lg">
            No reports found. Try adjusting your filters or create a new report.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card variant="default" size="large">
      <div className="divide-y divide-stone-200 dark:divide-stone-700">
        {reports.map((report) => (
          <ReportListItem key={report.id} report={report} />
        ))}
      </div>
    </Card>
  );
}