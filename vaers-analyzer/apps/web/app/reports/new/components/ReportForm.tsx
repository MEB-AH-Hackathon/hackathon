"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createReport } from '../../../actions/reports';
import { VaccineInputs, type VaccineInput } from './VaccineInputs';
import { SymptomInputs } from './SymptomInputs';
import { ExampleReports } from './ExampleReports';
import type { VaersReport, VaersRawData } from '@vaers/types';

export function ReportForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form state
  const [vaersId, setVaersId] = useState('');
  const [state, setState] = useState('');
  const [ageYrs, setAgeYrs] = useState('');
  const [sex, setSex] = useState('');
  const [symptomText, setSymptomText] = useState('');
  const [vaxDate, setVaxDate] = useState('');
  const [onsetDate, setOnsetDate] = useState('');
  const [recvDate, setRecvDate] = useState('');
  
  // Outcome flags
  const [died, setDied] = useState(false);
  const [lThreat, setLThreat] = useState(false);
  const [erVisit, setErVisit] = useState(false);
  const [hospital, setHospital] = useState(false);
  const [disable, setDisable] = useState(false);
  const [recovd, setRecovd] = useState<'Y' | 'N' | 'U' | ''>('');
  
  // Arrays
  const [vaccines, setVaccines] = useState<VaccineInput[]>([
    {
      id: 'vaccine-1',
      vaxType: '',
      vaxManufacturer: '',
      vaxName: '',
      vaxDoseSeries: '',
      vaxRoute: '',
      vaxSite: ''
    }
  ]);
  const [symptoms, setSymptoms] = useState<string[]>([]);

  const handleExampleSelect = (report: VaersReport) => {
    // Fill form with example data
    setVaersId(`NEW-${Date.now()}`); // Generate new ID
    setState(report.state || '');
    setAgeYrs(report.ageYrs?.toString() || '');
    setSex(report.sex || '');
    setSymptomText(report.symptomText || '');
    setVaxDate(report.vaxDate ? new Date(report.vaxDate).toISOString().split('T')[0] : '');
    setOnsetDate(report.onsetDate ? new Date(report.onsetDate).toISOString().split('T')[0] : '');
    setRecvDate(report.recvDate ? new Date(report.recvDate).toISOString().split('T')[0] : '');
    
    // Outcomes
    setDied(report.died || false);
    setLThreat(report.lThreat || false);
    setErVisit(report.erVisit || false);
    setHospital(report.hospital || false);
    setDisable(report.disable || false);
    setRecovd(report.recovd || '');
    
    // Vaccines
    if (report.vaccines.length > 0) {
      setVaccines(
        report.vaccines.map((v, i) => ({
          id: `vaccine-${i + 1}`,
          vaxType: v.vaxType || '',
          vaxManufacturer: v.vaxManufacturer || '',
          vaxName: v.vaxName || '',
          vaxDoseSeries: v.vaxDoseSeries || '',
          vaxRoute: v.vaxRoute || '',
          vaxSite: v.vaxSite || ''
        }))
      );
    }
    
    // Symptoms
    setSymptoms(report.symptoms.map(s => s.symptomName));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Convert form data to VaersRawData format
      const rawData: VaersRawData = {
        VAERS_ID: vaersId || `NEW-${Date.now()}`,
        RECVDATE: recvDate || null,
        STATE: state || null,
        AGE_YRS: ageYrs ? parseFloat(ageYrs) : null,
        SEX: sex || null,
        SYMPTOM_TEXT: symptomText || null,
        DIED: died ? 'Y' : null,
        L_THREAT: lThreat ? 'Y' : null,
        ER_VISIT: erVisit ? 'Y' : null,
        HOSPITAL: hospital ? 'Y' : null,
        DISABLE: disable ? 'Y' : null,
        RECOVD: recovd || null,
        VAX_DATE: vaxDate || null,
        ONSET_DATE: onsetDate || null,
        NUMDAYS: vaxDate && onsetDate ? 
          Math.floor((new Date(onsetDate).getTime() - new Date(vaxDate).getTime()) / (1000 * 60 * 60 * 24)) : 
          null,
        VAX_TYPE_list: vaccines.map(v => v.vaxType).filter(Boolean),
        VAX_MANU_list: vaccines.map(v => v.vaxManufacturer).filter(Boolean),
        VAX_NAME_list: vaccines.map(v => v.vaxName).filter(Boolean),
        VAX_DOSE_SERIES_list: vaccines.map(v => v.vaxDoseSeries || null),
        VAX_ROUTE_list: vaccines.map(v => v.vaxRoute || null),
        VAX_SITE_list: vaccines.map(v => v.vaxSite || null),
        symptom_list: symptoms
      };

      const report = await createReport(rawData);
      router.push(`/reports/${report.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create report');
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="lg:col-span-2">
        <form onSubmit={handleSubmit} className="space-y-8">
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Basic Information */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Basic Information
            </h2>
            
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label htmlFor="vaersId" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  VAERS ID
                </label>
                <input
                  type="text"
                  id="vaersId"
                  value={vaersId}
                  onChange={(e) => setVaersId(e.target.value)}
                  placeholder="Auto-generated if empty"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div>
                <label htmlFor="state" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  State
                </label>
                <input
                  type="text"
                  id="state"
                  value={state}
                  onChange={(e) => setState(e.target.value.toUpperCase().slice(0, 2))}
                  placeholder="e.g., CA"
                  maxLength={2}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div>
                <label htmlFor="age" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Age (years)
                </label>
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
                <label htmlFor="sex" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Sex
                </label>
                <select
                  id="sex"
                  value={sex}
                  onChange={(e) => setSex(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="">Select</option>
                  <option value="F">Female</option>
                  <option value="M">Male</option>
                  <option value="U">Unknown</option>
                </select>
              </div>
            </div>
          </div>

          {/* Dates */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Important Dates
            </h2>
            
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
              <div>
                <label htmlFor="vaxDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Vaccination Date
                </label>
                <input
                  type="date"
                  id="vaxDate"
                  value={vaxDate}
                  onChange={(e) => setVaxDate(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div>
                <label htmlFor="onsetDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Symptom Onset Date
                </label>
                <input
                  type="date"
                  id="onsetDate"
                  value={onsetDate}
                  onChange={(e) => setOnsetDate(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div>
                <label htmlFor="recvDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Report Received Date
                </label>
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

          {/* Vaccines */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <VaccineInputs vaccines={vaccines} onChange={setVaccines} />
          </div>

          {/* Symptoms */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <SymptomInputs symptoms={symptoms} onChange={setSymptoms} />
            
            <div className="mt-6">
              <label htmlFor="symptomText" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Symptom Narrative
              </label>
              <textarea
                id="symptomText"
                rows={4}
                value={symptomText}
                onChange={(e) => setSymptomText(e.target.value)}
                placeholder="Describe symptoms and events in detail..."
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
          </div>

          {/* Outcomes */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Outcomes
            </h2>
            
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
                <label htmlFor="recovd" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Recovery Status
                </label>
                <select
                  id="recovd"
                  value={recovd}
                  onChange={(e) => setRecovd(e.target.value as 'Y' | 'N' | 'U' | '')}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="">Select</option>
                  <option value="Y">Yes - Recovered</option>
                  <option value="N">No - Not Recovered</option>
                  <option value="U">Unknown</option>
                </select>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating Report...' : 'Submit Report'}
            </button>
          </div>
        </form>
      </div>

      <div className="lg:col-span-1">
        <ExampleReports onSelect={handleExampleSelect} />
      </div>
    </div>
  );
}