import Link from 'next/link';
import { ReportForm } from './components/ReportForm';
import { PageLayout, PageContainer, PageHeader } from '../../../components/ui';

export default function NewReportPage() {
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
          title="Submit New VAERS Report"
          subtitle="Real-time analysis powered by FDA databases"
          description="Enter vaccine adverse event information for sophisticated AI-powered analysis and symptom validation"
          icon={
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
            </svg>
          }
          iconVariant="default"
        />

        <ReportForm />
      </PageContainer>
    </PageLayout>
  );
}