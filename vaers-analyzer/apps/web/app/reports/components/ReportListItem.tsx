import Link from 'next/link';
import type { VaersReport } from '@vaers/types';
import { ReportOutcomeBadges } from './ReportOutcomeBadges';

interface ReportListItemProps {
  report: VaersReport;
}

export function ReportListItem({ report }: ReportListItemProps) {
  return (
    <div>
      <Link
        href={`/reports/${report.id}`}
        className="block hover:bg-stone-50/50 dark:hover:bg-stone-800/50 px-6 py-6 transition-all duration-300 group"
      >
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-stone-700 dark:text-stone-300 truncate group-hover:text-stone-900 dark:group-hover:text-stone-100 transition-colors">
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
    </div>
  );
}

function ReportMetadata({ report }: { report: VaersReport }) {
  return (
    <div className="mt-3 sm:flex sm:justify-between">
      <div className="sm:flex">
        <p className="flex items-center text-sm text-stone-500 dark:text-stone-400">
          {report.ageYrs && `${report.ageYrs} years`}
          {report.sex && ` • ${report.sex}`}
          {report.state && ` • ${report.state}`}
        </p>
      </div>
      <div className="mt-2 flex items-center text-sm text-stone-500 dark:text-stone-400 sm:mt-0">
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
    <div className="mt-3">
      <p className="text-sm text-stone-600 dark:text-stone-300 font-medium">
        {vaccineTypes}
      </p>
    </div>
  );
}

function SymptomPreview({ symptomText }: { symptomText?: string | null }) {
  if (!symptomText) return null;
  
  return (
    <div className="mt-3">
      <p className="text-sm text-stone-500 dark:text-stone-400 line-clamp-2 leading-relaxed">
        {symptomText}
      </p>
    </div>
  );
}