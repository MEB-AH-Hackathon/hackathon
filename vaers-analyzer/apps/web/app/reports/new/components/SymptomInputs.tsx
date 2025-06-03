"use client";

import { useState } from 'react';

interface SymptomInputsProps {
  symptoms: string[];
  onChange: (symptoms: string[]) => void;
}

// Common VAERS symptoms for autocomplete
const COMMON_SYMPTOMS = [
  'Injection site pain',
  'Injection site erythema',
  'Injection site swelling',
  'Pyrexia',
  'Fatigue',
  'Headache',
  'Myalgia',
  'Arthralgia',
  'Chills',
  'Nausea',
  'Dizziness',
  'Lymphadenopathy',
  'Rash',
  'Urticaria',
  'Pruritus',
  'Dyspnoea',
  'Chest pain',
  'Palpitations',
  'Syncope',
  'Anaphylactic reaction'
];

export function SymptomInputs({ symptoms, onChange }: SymptomInputsProps) {
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);

  const filteredSuggestions = COMMON_SYMPTOMS.filter(
    symptom => 
      symptom.toLowerCase().includes(inputValue.toLowerCase()) &&
      !symptoms.includes(symptom)
  );

  const addSymptom = (symptom: string) => {
    if (symptom && !symptoms.includes(symptom)) {
      onChange([...symptoms, symptom]);
      setInputValue('');
      setShowSuggestions(false);
    }
  };

  const removeSymptom = (symptom: string) => {
    onChange(symptoms.filter(s => s !== symptom));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && inputValue) {
      e.preventDefault();
      addSymptom(inputValue);
    }
  };

  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Symptoms (MedDRA Terms)
      </label>
      
      <div className="relative">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            onKeyDown={handleKeyDown}
            placeholder="Type symptom or select from list"
            className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
          <button
            type="button"
            onClick={() => addSymptom(inputValue)}
            disabled={!inputValue}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Add
          </button>
        </div>
        
        {showSuggestions && filteredSuggestions.length > 0 && (
          <div className="absolute z-10 mt-1 w-full bg-white dark:bg-gray-800 shadow-lg rounded-md border border-gray-200 dark:border-gray-700 max-h-60 overflow-auto">
            {filteredSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => addSymptom(suggestion)}
                className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>

      {symptoms.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {symptoms.map((symptom) => (
            <span
              key={symptom}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200"
            >
              {symptom}
              <button
                type="button"
                onClick={() => removeSymptom(symptom)}
                className="ml-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}