import type { VaersReport } from '@vaers/types';

interface ReportOutcomeBadgesProps {
  report: VaersReport;
}

export function ReportOutcomeBadges({ report }: ReportOutcomeBadgesProps) {
  return (
    <div className="ml-2 flex-shrink-0 flex">
      {report.died && (
        <OutcomeBadge type="death" label="Death" />
      )}
      {report.lThreat && (
        <OutcomeBadge type="lifeThreat" label="Life Threat" />
      )}
      {report.hospital && (
        <OutcomeBadge type="hospital" label="Hospitalized" />
      )}
      {report.erVisit && (
        <OutcomeBadge type="emergency" label="ER Visit" />
      )}
      {report.disable && (
        <OutcomeBadge type="disability" label="Disability" />
      )}
    </div>
  );
}

interface OutcomeBadgeProps {
  type: 'death' | 'lifeThreat' | 'hospital' | 'emergency' | 'disability';
  label: string;
}

function OutcomeBadge({ type, label }: OutcomeBadgeProps) {
  const styles = {
    death: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    lifeThreat: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    hospital: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    emergency: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
    disability: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  };

  return (
    <span className={`ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${styles[type]}`}>
      {label}
    </span>
  );
}