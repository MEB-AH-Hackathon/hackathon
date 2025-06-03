import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getReportById } from '../../actions/reports';
import { PageLayout, PageContainer, PageHeader } from '@repo/ui';
import { EditReportForm } from './components/EditReportForm';

export default async function EditReportPage({
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
          title="Edit Report"
          subtitle={`VAERS ID: ${report.vaersId}`}
          description="Update vaccine adverse event report details"
          icon={
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          }
          iconVariant="green"
        />

        <EditReportForm report={report} />
      </PageContainer>
    </PageLayout>
  );
}
