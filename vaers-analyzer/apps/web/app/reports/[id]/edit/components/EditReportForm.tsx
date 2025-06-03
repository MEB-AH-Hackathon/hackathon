"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { updateReport } from '../../../../actions/reports';
import { VaccineInputs, type VaccineInput } from '../../../new/components/VaccineInputs';
import { SymptomInputs } from '../../../new/components/SymptomInputs';
import type { VaersReport } from '@vaers/types';

interface EditReportFormProps {
  report: VaersReport;
}

export function EditReportForm({ report }: EditReportFormProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize form state with existing report values
  const [vaersId, setVaersId] = useState(report.vaersId);
  const [state, setState] = useState(report.state || '');
  const [ageYrs, setAgeYrs] = useState(report.ageYrs?.toString() || '');
  const [sex, setSex] = useState(report.sex || '');
  const [symptomText, setSymptomText] = useState(report.symptomText || '');
  const [vaxDate, setVaxDate] = useState(report.vaxDate ? new Date(report.vaxDate).toISOString().split('T')[0] : '');
  const [onsetDate, setOnsetDate] = useState(report.onsetDate ? new Date(report.onsetDate).toISOString().split('T')[0] : '');
  const [recvDate, setRecvDate] = useState(report.recvDate ? new Date(report.recvDate).toISOString().split('T')[0] : '');

  const [died, setDied] = useState(report.died || false);
  const [lThreat, setLThreat] = useState(report.lThreat || false);
  const [erVisit, setErVisit] = useState(report.erVisit || false);
  const [hospital, setHospital] = useState(report.hospital || false);
  const [disable, setDisable] = useState(report.disable || false);
  const [recovd, setRecovd] = useState<VaersReport['recovd']>(report.recovd || 'unknown');

  const [vaccines, setVaccines] = useState<VaccineInput[]>(
    report.vaccines.length > 0
      ? report.vaccines.map((v, i) => ({
          id: `vaccine-${i + 1}`,
          vaxType: v.vaxType || '',
          vaxManufacturer: v.vaxManufacturer || '',
          vaxName: v.vaxName || '',
          vaxDoseSeries: v.vaxDoseSeries || '',
          vaxRoute: v.vaxRoute || '',
          vaxSite: v.vaxSite || ''
        }))
      : [
          {
            id: 'vaccine-1',
            vaxType: '',
            vaxManufacturer: '',
            vaxName: '',
            vaxDoseSeries: '',
            vaxRoute: '',
            vaxSite: ''
          }
        ]
  );

  const [symptoms, setSymptoms] = useState<string[]>(report.symptoms.map(s => s.symptomName));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await updateReport(report.id, {
        vaersId,
        state: state || undefined,
        ageYrs: ageYrs ? parseFloat(ageYrs) : undefined,
        sex: (sex as 'male' | 'female' | 'unknown') || undefined,
        symptomText: symptomText || undefined,
        died,
        lThreat,
        erVisit,
        hospital,
        disable,
        recovd: recovd || undefined,
        vaxDate: vaxDate ? new Date(vaxDate) : undefined,
        onsetDate: onsetDate ? new Date(onsetDate) : undefined,
        recvDate: recvDate ? new Date(recvDate) : undefined,
        vaccines: vaccines.map(v => ({
          id: 0,
          reportId: report.id,
          vaxType: v.vaxType || undefined,
          vaxManufacturer: v.vaxManufacturer || undefined,
          vaxName: v.vaxName || undefined,
          vaxDoseSeries: v.vaxDoseSeries || undefined,
          vaxRoute: v.vaxRoute || undefined,
          vaxSite: v.vaxSite || undefined,
          createdAt: new Date()
        })),
        symptoms: symptoms.map(s => ({
          id: 0,
          reportId: report.id,
          symptomName: s,
          validationStatus: 'unvalidated',
          createdAt: new Date()
        }))
      });
      router.push(`/reports/${report.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update report');
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Basic Information</h2>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label htmlFor="vaersId" className="block text-sm font-medium text-gray-700 dark:text-gray-300">VAERS ID</label>
            <input
              type="text"
              id="vaersId"
              value={vaersId}
              onChange={(e) => setVaersId(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <div>
            <label htmlFor="state" className="block text-sm font-medium text-gray-700 dark:text-gray-300">State</label>
            <input
              type="text"
              id="state"
              value={state}
              onChange={(e) => setState(e.target.value.toUpperCase().slice(0, 2))}
              maxLength={2}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <div>
            <label htmlFor="age" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Age (years)</label>
            <input
              type="number"
              id="age"
              value={ageYrs}
              onChange={(e) => setAgeYrs(e.target.value)}
              step="0.01"
              min="0"
              max="120"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <div>
            <label htmlFor="sex" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Sex</label>
            <select
              id="sex"
              value={sex}
              onChange={(e) => setSex(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="">Select</option>
              <option value="female">Female</option>
              <option value="male">Male</option>
              <option value="unknown">Unknown</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Important Dates</h2>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          <div>
            <label htmlFor="vaxDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Vaccination Date</label>
            <input
              type="date"
              id="vaxDate"
              value={vaxDate}
              onChange={(e) => setVaxDate(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <div>
            <label htmlFor="onsetDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Symptom Onset Date</label>
            <input
              type="date"
              id="onsetDate"
              value={onsetDate}
              onChange={(e) => setOnsetDate(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <div>
            <label htmlFor="recvDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Report Received Date</label>
            <input
              type="date"
              id="recvDate"
              value={recvDate}
              onChange={(e) => setRecvDate(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <VaccineInputs vaccines={vaccines} onChange={setVaccines} />
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <SymptomInputs symptoms={symptoms} onChange={setSymptoms} />
        <div className="mt-6">
          <label htmlFor="symptomText" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Symptom Narrative</label>
          <textarea
            id="symptomText"
            rows={4}
            value={symptomText}
            onChange={(e) => setSymptomText(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Outcomes</h2>
        <div className="space-y-4">
          <div className="flex flex-wrap gap-4">
            {[
              { id: 'died', label: 'Death', value: died, setter: setDied },
              { id: 'lThreat', label: 'Life Threatening', value: lThreat, setter: setLThreat },
              { id: 'erVisit', label: 'ER Visit', value: erVisit, setter: setErVisit },
              { id: 'hospital', label: 'Hospitalized', value: hospital, setter: setHospital },
              { id: 'disable', label: 'Disability', value: disable, setter: setDisable },
            ].map(({ id, label, value, setter }) => (
              <label key={id} className="flex items-center">
                <input
                  type="checkbox"
                  checked={value}
                  onChange={(e) => setter(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">{label}</span>
              </label>
            ))}
          </div>

          <div>
            <label htmlFor="recovd" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Recovery Status</label>
            <select
              id="recovd"
              value={recovd || ''}
              onChange={(e) => setRecovd(e.target.value as VaersReport['recovd'])}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="">Select</option>
              <option value="yes">Yes - Recovered</option>
              <option value="no">No - Not Recovered</option>
              <option value="unknown">Unknown</option>
            </select>
          </div>
        </div>
      </div>

      <div className="flex justify-end gap-4">
        <button
          type="button"
          onClick={() => router.push(`/reports/${report.id}`)}
          disabled={loading}
          className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Updating...' : 'Save Changes'}
        </button>
      </div>
    </form>
  );
}
