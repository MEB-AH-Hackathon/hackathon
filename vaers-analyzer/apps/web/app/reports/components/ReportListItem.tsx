import Link from 'next/link';
import type { VaersReport } from '@vaers/types';
import { ReportOutcomeBadges } from './ReportOutcomeBadges';

interface ReportListItemProps {
  report: VaersReport;
}

export function ReportListItem({ report }: ReportListItemProps) {
  return (
    <li>
      <Link
        href={`/reports/${report.id}`}
        className="block hover:bg-gray-50 dark:hover:bg-gray-700 px-4 py-4 sm:px-6 transition-colors"
      >
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-blue-600 dark:text-blue-400 truncate">
                VAERS ID: {report.vaersId}
              </p>
              <ReportOutcomeBadges report={report} />
            </div>
            
            <ReportMetadata report={report} />
            <VaccineInfo vaccines={report.vaccines} />
            <SymptomPreview symptomText={report.symptomText} />
          </div>
        </div>
      </Link>
    </li>
  );
}

function ReportMetadata({ report }: { report: VaersReport }) {
  return (
    <div className="mt-2 sm:flex sm:justify-between">
      <div className="sm:flex">
        <p className="flex items-center text-sm text-gray-500 dark:text-gray-400">
          {report.ageYrs && `${report.ageYrs} years`}
          {report.sex && ` • ${report.sex}`}
          {report.state && ` • ${report.state}`}
        </p>
      </div>
      <div className="mt-2 flex items-center text-sm text-gray-500 dark:text-gray-400 sm:mt-0">
        <p>
          {report.vaccines.length} vaccine{report.vaccines.length !== 1 ? 's' : ''}
          {' • '}
          {report.symptoms.length} symptom{report.symptoms.length !== 1 ? 's' : ''}
        </p>
      </div>
    </div>
  );
}

function VaccineInfo({ vaccines }: { vaccines: VaersReport['vaccines'] }) {
  if (vaccines.length === 0) return null;
  
  const vaccineTypes = vaccines
    .map(v => v.vaxType)
    .filter(Boolean)
    .join(', ');
    
  if (!vaccineTypes) return null;
  
  return (
    <div className="mt-2">
      <p className="text-sm text-gray-600 dark:text-gray-300">
        {vaccineTypes}
      </p>
    </div>
  );
}

function SymptomPreview({ symptomText }: { symptomText?: string | null }) {
  if (!symptomText) return null;
  
  return (
    <div className="mt-2">
      <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
        {symptomText}
      </p>
    </div>
  );
}