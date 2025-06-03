import type { VaersReport } from '@vaers/types';
import { ReportOutcomeBadges } from '../../components/ReportOutcomeBadges';

interface ReportDetailsProps {
  report: VaersReport;
}

export function ReportDetails({ report }: ReportDetailsProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white">
            VAERS Report {report.vaersId}
          </h2>
          <ReportOutcomeBadges report={report} />
        </div>
        
        <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Patient</dt>
            <dd className="mt-1 text-sm text-gray-900 dark:text-white">
              {report.ageYrs ? `${report.ageYrs} years` : 'Age unknown'}
              {report.sex && ` • ${report.sex === 'F' ? 'Female' : report.sex === 'M' ? 'Male' : 'Unknown'}`}
              {report.state && ` • ${report.state}`}
            </dd>
          </div>
          
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Key Dates</dt>
            <dd className="mt-1 text-sm text-gray-900 dark:text-white">
              {report.vaxDate && (
                <div>Vaccinated: {new Date(report.vaxDate).toLocaleDateString()}</div>
              )}
              {report.onsetDate && (
                <div>Onset: {new Date(report.onsetDate).toLocaleDateString()}</div>
              )}
              {report.numDays !== null && report.numDays !== undefined && (
                <div className="text-xs text-gray-600 dark:text-gray-400">
                  ({report.numDays} days after vaccination)
                </div>
              )}
            </dd>
          </div>
          
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Recovery Status</dt>
            <dd className="mt-1 text-sm text-gray-900 dark:text-white">
              {report.recovd === 'Y' ? 'Recovered' : 
               report.recovd === 'N' ? 'Not Recovered' : 
               report.recovd === 'U' ? 'Unknown' : 'Not Specified'}
            </dd>
          </div>
          
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Report Status</dt>
            <dd className="mt-1">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                report.status === 'validated' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                report.status === 'new' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                report.status === 'pending_validation' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
              }`}>
                {report.status}
              </span>
            </dd>
          </div>
        </dl>
      </div>

      {/* Vaccines */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Vaccines Administered ({report.vaccines.length})
        </h3>
        <div className="space-y-4">
          {report.vaccines.map((vaccine, index) => (
            <div key={vaccine.id} className="border-l-4 border-blue-500 pl-4">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                Vaccine {index + 1}: {vaccine.vaxType || 'Unknown Type'}
              </h4>
              <dl className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {vaccine.vaxManufacturer && (
                  <div>Manufacturer: {vaccine.vaxManufacturer}</div>
                )}
                {vaccine.vaxName && (
                  <div>Name: {vaccine.vaxName}</div>
                )}
                {vaccine.vaxDoseSeries && (
                  <div>Dose: {vaccine.vaxDoseSeries}</div>
                )}
                {vaccine.vaxRoute && (
                  <div>Route: {vaccine.vaxRoute}</div>
                )}
                {vaccine.vaxSite && (
                  <div>Site: {vaccine.vaxSite}</div>
                )}
              </dl>
            </div>
          ))}
        </div>
      </div>

      {/* Symptoms */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Reported Symptoms ({report.symptoms.length})
        </h3>
        
        {report.symptoms.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-2">
              {report.symptoms.map((symptom) => (
                <span
                  key={symptom.id}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200"
                >
                  {symptom.symptomName}
                  {symptom.severity && (
                    <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                      ({symptom.severity})
                    </span>
                  )}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {report.symptomText && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
              Symptom Narrative
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
              {report.symptomText}
            </p>
          </div>
        )}
      </div>

      {/* Metadata */}
      <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 text-xs text-gray-500 dark:text-gray-400">
        <div>Created: {new Date(report.createdAt).toLocaleString()}</div>
        <div>Last Updated: {new Date(report.updatedAt).toLocaleString()}</div>
        {report.recvDate && (
          <div>Report Received: {new Date(report.recvDate).toLocaleDateString()}</div>
        )}
      </div>
    </div>
  );
}