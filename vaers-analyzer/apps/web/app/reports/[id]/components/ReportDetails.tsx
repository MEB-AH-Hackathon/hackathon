import type { VaersReport } from '@vaers/types';
import { ReportOutcomeBadges } from '../../components/ReportOutcomeBadges';

interface ReportDetailsProps {
  report: VaersReport;
}

export function ReportDetails({ report }: ReportDetailsProps) {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm shadow-lg rounded-3xl p-8 border border-slate-200/50 dark:border-slate-700/50">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-slate-600 to-slate-700 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-sm">ID</span>
            </div>
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">
              Report {report.vaersId}
            </h2>
          </div>
          <ReportOutcomeBadges report={report} />
        </div>
        
        <dl className="grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-2">
          <div className="bg-gradient-to-br from-slate-50 to-white dark:from-slate-800 dark:to-slate-700 p-4 rounded-2xl border border-slate-200/50 dark:border-slate-600/50">
            <dt className="text-sm font-semibold text-slate-600 dark:text-slate-400 mb-2">Patient Demographics</dt>
            <dd className="text-slate-900 dark:text-slate-100">
              <div className="space-y-1">
                <div className="text-lg font-medium">
                  {report.ageYrs ? `${report.ageYrs} years` : 'Age unknown'}
                </div>
                <div className="text-sm text-slate-600 dark:text-slate-400">
                  {report.sex && `${report.sex === 'female' ? 'Female' : report.sex === 'male' ? 'Male' : 'Unknown'}`}
                  {report.state && ` • ${report.state}`}
                </div>
              </div>
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
              {report.recovd === 'yes' ? 'Recovered' : 
               report.recovd === 'no' ? 'Not Recovered' : 
               report.recovd === 'unknown' ? 'Unknown' : 'Not Specified'}
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
      <div className="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm shadow-lg rounded-3xl p-8 border border-slate-200/50 dark:border-slate-700/50">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          </div>
          <h3 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">
            Vaccines Administered ({report.vaccines.length})
          </h3>
        </div>
        <div className="space-y-6">
          {report.vaccines.map((vaccine, index) => (
            <div key={vaccine.id} className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-2xl p-6 border-l-4 border-blue-500">
              <h4 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3">
                Vaccine {index + 1}: {vaccine.vaxType || 'Unknown Type'}
              </h4>
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
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
      <div className="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm shadow-lg rounded-3xl p-8 border border-slate-200/50 dark:border-slate-700/50">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-pink-600 rounded-xl flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">
            Reported Symptoms ({report.symptoms.length})
          </h3>
        </div>
        
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