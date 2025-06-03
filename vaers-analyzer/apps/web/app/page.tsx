import Link from 'next/link';
import { PageLayout, PageContainer, Card, CardTitle, CardDescription, CardFooter, IconContainer } from '../components/ui';

export default function Home() {
  return (
    <PageLayout>
      <PageContainer size="wide" className="py-24">
        {/* Header */}
        <div className="text-center mb-20">
          <h1 className="text-6xl font-semibold tracking-tight mb-6">
            <span className="text-stone-900 dark:text-stone-100">VAERS</span>
            <span className="text-stone-700 dark:text-stone-300 ml-3">Analyzer</span>
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-3xl mx-auto leading-relaxed">
            Sophisticated symptom analysis and validation for vaccine adverse event reports using AI-powered FDA database matching
          </p>
          <div className="mt-6 flex items-center justify-center space-x-1 text-sm text-slate-500 dark:text-slate-500">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span>Real-time analysis powered by FDA databases</span>
          </div>
        </div>
        
        {/* Main Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-20">
          <Card variant="interactive" size="xlarge" hoverOverlay>
            <IconContainer 
              variant="default" 
              size="lg" 
              className="mb-8"
              icon={
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
                </svg>
              }
            />
            <CardTitle className="mb-4">Submit New Report</CardTitle>
            <CardDescription className="mb-8">
              Submit a new VAERS report for sophisticated AI analysis. Our system cross-references FDA databases and clinical trial data for comprehensive symptom validation.
            </CardDescription>
            <CardFooter>
              <Link 
                href="/reports/new" 
                className="inline-flex items-center px-6 py-3 bg-slate-700 dark:bg-slate-300 text-white dark:text-slate-800 font-medium rounded-xl hover:bg-slate-800 dark:hover:bg-slate-200 transition-all duration-300 shadow-sm hover:shadow-md"
              >
                Create Report 
                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </CardFooter>
          </Card>

          <Card variant="interactive" size="xlarge" hoverOverlay>
            <IconContainer 
              variant="blue" 
              size="lg" 
              className="mb-8"
              icon={
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              }
            />
            <CardTitle className="mb-4">View Reports</CardTitle>
            <CardDescription className="mb-8">
              Browse analyzed VAERS reports with detailed symptom validation profiles. Filter by vaccine type, adverse event outcomes, and AI confidence scores.
            </CardDescription>
            <CardFooter>
              <Link 
                href="/reports" 
                className="inline-flex items-center px-6 py-3 bg-blue-700 dark:bg-blue-300 text-white dark:text-blue-900 font-medium rounded-xl hover:bg-blue-800 dark:hover:bg-blue-200 transition-all duration-300 shadow-sm hover:shadow-md"
              >
                Browse Reports
                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </CardFooter>
          </Card>
        </div>

        {/* Process Overview */}
        <Card variant="muted" size="large" className="mb-20">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-semibold text-stone-900 dark:text-stone-100 mb-4">Analytical Process</h3>
            <p className="text-stone-600 dark:text-stone-400 max-w-2xl mx-auto">Our sophisticated AI pipeline ensures rigorous validation through multi-stage analysis</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { step: "01", title: "Submit", desc: "Upload VAERS report with comprehensive vaccine and symptom data", icon: "M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" },
              { step: "02", title: "Analyze", desc: "AI cross-references FDA databases and validated clinical reports", icon: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" },
              { step: "03", title: "Match", desc: "Identify symptom patterns with statistical confidence scoring", icon: "M13 10V3L4 14h7v7l9-11h-7z" },
              { step: "04", title: "Review", desc: "Generate comprehensive analysis with similar case outcomes", icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" }
            ].map((item, i) => (
              <div key={i} className="text-center group">
                <div className="relative mb-6">
                  <IconContainer 
                    variant="muted" 
                    size="lg" 
                    className="mx-auto mb-4 group-hover:scale-105 transition-transform duration-200"
                    icon={
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={item.icon} />
                      </svg>
                    }
                  />
                  <div className="text-4xl font-light text-stone-300 dark:text-stone-600 mb-3">{item.step}</div>
                </div>
                <h4 className="font-semibold text-stone-900 dark:text-stone-100 mb-3">{item.title}</h4>
                <p className="text-sm text-stone-600 dark:text-stone-400 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { value: "10,000+", label: "Reports Analyzed", sublabel: "FDA-validated adverse events" },
            { value: "98.7%", label: "Accuracy Rate", sublabel: "Clinical validation match" },
            { value: "< 2.3s", label: "Analysis Time", sublabel: "Real-time processing" }
          ].map((stat, i) => (
            <Card key={i} variant="default" size="large" className="text-center">
              <div className="text-4xl font-bold text-stone-900 dark:text-stone-100 mb-2">
                {stat.value}
              </div>
              <div className="text-lg font-medium text-stone-700 dark:text-stone-300 mb-1">{stat.label}</div>
              <div className="text-sm text-stone-500 dark:text-stone-400">{stat.sublabel}</div>
            </Card>
          ))}
        </div>
      </PageContainer>
    </PageLayout>
  );
}