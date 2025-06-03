"use client";

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { PageHeader, Card, CardContent, IconContainer, Input, Select, Label } from '../../../components/ui';
import type { ReportFilters } from '../../actions/reports';

interface ReportsHeaderProps {
  totalReports: number;
  reportsWithOutcomes: number;
  recentReports: number;
  filters: ReportFilters;
  limit: number;
}

export function ReportsHeader({ totalReports, reportsWithOutcomes, recentReports, filters, limit }: ReportsHeaderProps) {
  const router = useRouter();
  const [search, setSearch] = useState(filters.search ?? "");
  const [vaccineType, setVaccineType] = useState(filters.vaccineType ?? "");
  const [outcome, setOutcome] = useState(filters.outcome ?? "");
  const [dateRange, setDateRange] = useState(filters.dateRange ?? "");

  useEffect(() => {
    const timeout = setTimeout(() => {
      const params = new URLSearchParams();
      if (search) params.set('search', search);
      if (vaccineType) params.set('vaccineType', vaccineType);
      if (outcome) params.set('outcome', outcome);
      if (dateRange) params.set('dateRange', dateRange);
      params.set('page', '1');
      params.set('limit', String(limit));
      router.push(`/reports?${params.toString()}`);
    }, 300);

    return () => clearTimeout(timeout);
  }, [search, vaccineType, outcome, dateRange, limit, router]);
  return (
    <div className="mb-12">
      <PageHeader
        title="VAERS Reports"
        subtitle="Live analysis dashboard"
        description="Browse and analyze FDA-validated vaccine adverse event reports with AI-powered symptom correlation"
        icon={
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        }
        iconVariant="blue"
        actions={
          <Link
            href="/reports/new"
            className="inline-flex items-center px-6 py-3 bg-stone-700 dark:bg-stone-300 text-white dark:text-stone-800 font-medium rounded-xl hover:bg-stone-800 dark:hover:bg-stone-200 transition-all duration-300 shadow-sm hover:shadow-md"
          >
            <svg className="mr-2 -ml-1 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Submit New Report
          </Link>
        }
      />
      
      {/* Real Statistics */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <Card variant="default" size="large">
          <CardContent className="p-6">
            <div className="flex items-center">
              <IconContainer
                variant="blue"
                size="default"
                className="mr-4"
                icon={
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                }
              />
              <div>
                <p className="text-2xl font-bold text-stone-900 dark:text-stone-100">{totalReports.toLocaleString()}</p>
                <p className="text-sm text-stone-600 dark:text-stone-400">Total Reports</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="default" size="large">
          <CardContent className="p-6">
            <div className="flex items-center">
              <IconContainer
                variant="amber"
                size="default"
                className="mr-4"
                icon={
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.172 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                }
              />
              <div>
                <p className="text-2xl font-bold text-stone-900 dark:text-stone-100">{reportsWithOutcomes.toLocaleString()}</p>
                <p className="text-sm text-stone-600 dark:text-stone-400">With Adverse Outcomes</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="default" size="large">
          <CardContent className="p-6">
            <div className="flex items-center">
              <IconContainer
                variant="green"
                size="default"
                className="mr-4"
                icon={
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                }
              />
              <div>
                <p className="text-2xl font-bold text-stone-900 dark:text-stone-100">{recentReports.toLocaleString()}</p>
                <p className="text-sm text-stone-600 dark:text-stone-400">Recent (30 days)</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Real Filters and Search */}
      <Card variant="default" size="large">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Label className="mb-2">Search Reports</Label>
              <Input
                type="text"
                placeholder="VAERS ID, symptoms..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div>
              <Label className="mb-2">Vaccine Type</Label>
              <Select value={vaccineType} onChange={(e) => setVaccineType(e.target.value)}>
                <option value="">All Types</option>
                <option value="covid19">COVID-19</option>
                <option value="flu">Influenza</option>
                <option value="mmr">MMR</option>
                <option value="other">Other</option>
              </Select>
            </div>
            <div>
              <Label className="mb-2">Outcome</Label>
              <Select value={outcome} onChange={(e) => setOutcome(e.target.value)}>
                <option value="">All Outcomes</option>
                <option value="recovered">Recovered</option>
                <option value="hospitalized">Hospitalized</option>
                <option value="serious">Serious</option>
              </Select>
            </div>
            <div>
              <Label className="mb-2">Date Range</Label>
              <Select value={dateRange} onChange={(e) => setDateRange(e.target.value)}>
                <option value="">All Time</option>
                <option value="7days">Last 7 days</option>
                <option value="30days">Last 30 days</option>
                <option value="90days">Last 90 days</option>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}