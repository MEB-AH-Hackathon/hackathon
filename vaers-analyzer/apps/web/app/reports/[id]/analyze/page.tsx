import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getReportById } from '../../../actions/reports';
import { PageLayout, PageContainer, PageHeader, Card, CardContent, IconContainer } from '@repo/ui';

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
          subtitle={`VAERS Report ${report.vaersId} Analysis • Phase 2 Development`}
          description="Advanced AI-powered analysis with FDA database cross-referencing and symptom validation"
          icon={
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          }
          iconVariant="blue"
        />

        {/* Phase 2 Placeholder */}
        <Card variant="elevated" size="xlarge" className="text-center">
          <CardContent className="p-12">
            <IconContainer
              variant="blue"
              size="xl"
              className="mx-auto mb-8"
              icon={
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              }
            />
            <h3 className="text-2xl font-semibold text-stone-900 dark:text-stone-100 mb-4">
              AI Analysis Coming Soon
            </h3>
            <p className="text-stone-600 dark:text-stone-400 max-w-2xl mx-auto mb-8 leading-relaxed">
              This is where the AI-powered analysis will appear in Phase 2. The system will search FDA databases, 
              find similar reports, and provide a comprehensive analysis with statistical confidence scoring.
            </p>
            
            <Card variant="muted" size="large" className="mb-8">
              <CardContent className="p-6 text-left">
                <h4 className="text-lg font-semibold text-stone-900 dark:text-stone-100 mb-4">
                  Planned Features:
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <ul className="text-stone-600 dark:text-stone-400 space-y-2">
                    <li className="flex items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                      Real-time search progress visualization
                    </li>
                    <li className="flex items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                      FDA-validated symptom comparison
                    </li>
                    <li className="flex items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                      Similar VAERS report matching
                    </li>
                  </ul>
                  <ul className="text-stone-600 dark:text-stone-400 space-y-2">
                    <li className="flex items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                      Controlled trial data analysis
                    </li>
                    <li className="flex items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                      Structured confidence scoring
                    </li>
                    <li className="flex items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                      Safety signal detection
                    </li>
                  </ul>
                </div>
              </CardContent>
            </Card>
            
            <Link
              href={`/reports/${reportId}`}
              className="inline-flex items-center px-6 py-3 bg-stone-700 dark:bg-stone-300 text-white dark:text-stone-800 font-medium rounded-xl hover:bg-stone-800 dark:hover:bg-stone-200 transition-all duration-300 shadow-sm hover:shadow-md"
            >
              Return to Report
              <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </CardContent>
        </Card>
      </PageContainer>
    </PageLayout>
  );
}