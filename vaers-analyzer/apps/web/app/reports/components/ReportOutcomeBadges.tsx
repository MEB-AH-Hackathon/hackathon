import type { VaersReport } from '@vaers/types';
import { Badge } from '../../../components/ui';

interface ReportOutcomeBadgesProps {
  report: VaersReport;
}

export function ReportOutcomeBadges({ report }: ReportOutcomeBadgesProps) {
  return (
    <div className="ml-2 flex-shrink-0 flex">
      {report.died && (
        <Badge variant="death" className="ml-2">Death</Badge>
      )}
      {report.lThreat && (
        <Badge variant="lifeThreat" className="ml-2">Life Threat</Badge>
      )}
      {report.hospital && (
        <Badge variant="hospital" className="ml-2">Hospitalized</Badge>
      )}
      {report.erVisit && (
        <Badge variant="emergency" className="ml-2">ER Visit</Badge>
      )}
      {report.disable && (
        <Badge variant="disability" className="ml-2">Disability</Badge>
      )}
    </div>
  );
}