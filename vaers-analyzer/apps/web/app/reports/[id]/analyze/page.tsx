import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getReportById } from '../../../actions/reports';
import { PageLayout, PageContainer, PageHeader } from '@repo/ui';
import { AnalysisStream } from './components/AnalysisStream';

export default async function AnalyzePage({
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
            href={`/reports/${reportId}`}
            className="inline-flex items-center text-stone-600 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100 transition-colors group mb-6"
          >
            <svg className="mr-2 h-5 w-5 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Report
          </Link>
        </div>

        <PageHeader
          title="AI Analysis Results"
          subtitle={`VAERS Report ${report.vaersId} Analysis`}
          description="Advanced AI-powered analysis with FDA database cross-referencing and symptom validation"
          icon={
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          }
          iconVariant="blue"
        />

        <AnalysisStream reportId={reportId} />
      </PageContainer>
    </PageLayout>
  );
}