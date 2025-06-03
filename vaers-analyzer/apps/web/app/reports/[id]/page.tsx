import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getReportById } from '../../actions/reports';
import { ReportDetails } from './components/ReportDetails';
import { AnalyzeButton } from './components/AnalyzeButton';
import { PageLayout, PageContainer, PageHeader } from '../../../components/ui';

export default async function ReportPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const reportId = parseInt(id);
  
  if (isNaN(reportId)) {
    notFound();
  }

  const report = await getReportById(reportId);
  
  if (!report) {
    notFound();
  }

  return (
    <PageLayout>
      <PageContainer size="wide" className="py-12">
        <div className="mb-8">
          <Link
            href="/reports"
            className="inline-flex items-center text-stone-600 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100 transition-colors group mb-6"
          >
            <svg className="mr-2 h-5 w-5 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Reports
          </Link>
        </div>

        <PageHeader
          title="Report Analysis"
          subtitle={`VAERS ID: ${report.vaersId} • Ready for AI analysis`}
          description="Comprehensive adverse event analysis with FDA database cross-referencing and symptom validation"
          icon={
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          }
          iconVariant="green"
          actions={
            <div className="flex space-x-4">
              <AnalyzeButton reportId={report.id} />
              
              <Link
                href={`/reports/${report.id}/edit`}
                className="inline-flex items-center px-4 py-2 border border-stone-300 dark:border-stone-600 rounded-xl shadow-sm text-sm font-medium text-stone-700 dark:text-stone-300 bg-white/80 dark:bg-stone-800/80 backdrop-blur-sm hover:bg-white dark:hover:bg-stone-800 transition-all duration-300"
              >
                <svg className="mr-2 -ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit Report
              </Link>
            </div>
          }
        />

        <ReportDetails report={report} />
        
        {/* Enhanced Disclaimer */}
        <div className="mt-12 bg-gradient-to-br from-stone-50 to-slate-50 dark:from-stone-900/20 dark:to-slate-900/20 border border-stone-200 dark:border-stone-700 rounded-2xl p-6 backdrop-blur-sm">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-gradient-to-br from-stone-500 to-slate-600 rounded-xl flex items-center justify-center">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.172 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-stone-800 dark:text-stone-200 mb-2">
                Important Medical Disclaimer
              </h3>
              <div className="text-stone-700 dark:text-stone-300 space-y-2">
                <p className="leading-relaxed">
                  VAERS reports represent unverified adverse events following vaccination and may contain inaccuracies, omissions, or coincidental occurrences. These reports do not establish causal relationships between vaccines and adverse events.
                </p>
                <p className="text-sm font-medium">
                  This analytical tool is designed for research and educational purposes only. Do not use this information for medical decisions without consulting qualified healthcare professionals.
                </p>
              </div>
            </div>
          </div>
        </div>
      </PageContainer>
    </PageLayout>
  );
}