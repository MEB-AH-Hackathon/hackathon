"use client";

import { useState } from 'react';

export interface VaccineInput {
  id: string;
  vaxType: string;
  vaxManufacturer: string;
  vaxName: string;
  vaxDoseSeries: string;
  vaxRoute: string;
  vaxSite: string;
}

interface VaccineInputsProps {
  vaccines: VaccineInput[];
  onChange: (vaccines: VaccineInput[]) => void;
}

export function VaccineInputs({ vaccines, onChange }: VaccineInputsProps) {
  const addVaccine = () => {
    onChange([
      ...vaccines,
      {
        id: `vaccine-${Date.now()}`,
        vaxType: '',
        vaxManufacturer: '',
        vaxName: '',
        vaxDoseSeries: '',
        vaxRoute: '',
        vaxSite: ''
      }
    ]);
  };

  const removeVaccine = (id: string) => {
    onChange(vaccines.filter(v => v.id !== id));
  };

  const updateVaccine = (id: string, field: keyof VaccineInput, value: string) => {
    onChange(
      vaccines.map(v => 
        v.id === id ? { ...v, [field]: value } : v
      )
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Vaccines Administered
        </label>
        <button
          type="button"
          onClick={addVaccine}
          className="text-sm text-blue-600 hover:text-blue-500"
        >
          + Add Vaccine
        </button>
      </div>

      {vaccines.map((vaccine, index) => (
        <div key={vaccine.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white">
              Vaccine {index + 1}
            </h4>
            {vaccines.length > 1 && (
              <button
                type="button"
                onClick={() => removeVaccine(vaccine.id)}
                className="text-sm text-red-600 hover:text-red-500"
              >
                Remove
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor={`${vaccine.id}-type`} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Vaccine Type
              </label>
              <input
                type="text"
                id={`${vaccine.id}-type`}
                value={vaccine.vaxType}
                onChange={(e) => updateVaccine(vaccine.id, 'vaxType', e.target.value)}
                placeholder="e.g., COVID19, FLU4"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div>
              <label htmlFor={`${vaccine.id}-manufacturer`} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Manufacturer
              </label>
              <input
                type="text"
                id={`${vaccine.id}-manufacturer`}
                value={vaccine.vaxManufacturer}
                onChange={(e) => updateVaccine(vaccine.id, 'vaxManufacturer', e.target.value)}
                placeholder="e.g., PFIZER\\BIONTECH"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div>
              <label htmlFor={`${vaccine.id}-name`} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Vaccine Name
              </label>
              <input
                type="text"
                id={`${vaccine.id}-name`}
                value={vaccine.vaxName}
                onChange={(e) => updateVaccine(vaccine.id, 'vaxName', e.target.value)}
                placeholder="e.g., COVID19 (COVID19 (PFIZER-BIONTECH))"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div>
              <label htmlFor={`${vaccine.id}-dose`} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Dose Series
              </label>
              <input
                type="text"
                id={`${vaccine.id}-dose`}
                value={vaccine.vaxDoseSeries}
                onChange={(e) => updateVaccine(vaccine.id, 'vaxDoseSeries', e.target.value)}
                placeholder="e.g., 1, 2, 3"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div>
              <label htmlFor={`${vaccine.id}-route`} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Route
              </label>
              <select
                id={`${vaccine.id}-route`}
                value={vaccine.vaxRoute}
                onChange={(e) => updateVaccine(vaccine.id, 'vaxRoute', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="">Select route</option>
                <option value="IM">IM (Intramuscular)</option>
                <option value="SC">SC (Subcutaneous)</option>
                <option value="IN">IN (Intranasal)</option>
                <option value="PO">PO (Oral)</option>
                <option value="ID">ID (Intradermal)</option>
                <option value="SYR">SYR (Syringe)</option>
              </select>
            </div>

            <div>
              <label htmlFor={`${vaccine.id}-site`} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Site
              </label>
              <select
                id={`${vaccine.id}-site`}
                value={vaccine.vaxSite}
                onChange={(e) => updateVaccine(vaccine.id, 'vaxSite', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="">Select site</option>
                <option value="LA">LA (Left Arm)</option>
                <option value="RA">RA (Right Arm)</option>
                <option value="LL">LL (Left Leg)</option>
                <option value="RL">RL (Right Leg)</option>
                <option value="UN">UN (Unknown)</option>
              </select>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}