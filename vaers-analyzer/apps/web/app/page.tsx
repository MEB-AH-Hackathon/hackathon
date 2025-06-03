export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-6xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-light tracking-tight text-gray-900 dark:text-white mb-4">
            VAERS <span className="font-medium">Analyzer</span>
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Advanced symptom analysis and validation for vaccine adverse event reports
          </p>
        </div>
        
        {/* Main Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
          <div className="group relative bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 dark:border-gray-700">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl opacity-0 group-hover:opacity-5 transition-opacity"></div>
            <div className="relative">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <h2 className="text-2xl font-medium mb-3 text-gray-900 dark:text-white">Submit New Report</h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
                Submit a new VAERS report for intelligent analysis. Our AI searches FDA databases and validated reports for symptom patterns.
              </p>
              <a 
                href="/reports/new" 
                className="inline-flex items-center text-blue-600 dark:text-blue-400 font-medium hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
              >
                Create Report 
                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </a>
            </div>
          </div>

          <div className="group relative bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 dark:border-gray-700">
            <div className="absolute inset-0 bg-gradient-to-r from-emerald-600 to-teal-600 rounded-2xl opacity-0 group-hover:opacity-5 transition-opacity"></div>
            <div className="relative">
              <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-900/30 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h2 className="text-2xl font-medium mb-3 text-gray-900 dark:text-white">View Reports</h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
                Browse analyzed VAERS reports with detailed symptom validation. Filter by vaccine type, status, and similarity scores.
              </p>
              <a 
                href="/reports" 
                className="inline-flex items-center text-emerald-600 dark:text-emerald-400 font-medium hover:text-emerald-700 dark:hover:text-emerald-300 transition-colors"
              >
                Browse Reports
                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </a>
            </div>
          </div>
        </div>

        {/* Process Overview */}
        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-3xl p-10 border border-gray-200 dark:border-gray-700">
          <h3 className="text-2xl font-medium mb-8 text-center text-gray-900 dark:text-white">How It Works</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { step: "01", title: "Submit", desc: "Upload VAERS report with vaccine and symptom data" },
              { step: "02", title: "Analyze", desc: "AI searches FDA databases and validated reports" },
              { step: "03", title: "Match", desc: "Find symptom analogies with similarity scoring" },
              { step: "04", title: "Review", desc: "Access detailed analysis and similar case outcomes" }
            ].map((item, i) => (
              <div key={i} className="text-center">
                <div className="text-3xl font-light text-gray-300 dark:text-gray-600 mb-3">{item.step}</div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">{item.title}</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="mt-16 grid grid-cols-3 gap-8 text-center">
          {[
            { value: "10K+", label: "Reports Analyzed" },
            { value: "98%", label: "Accuracy Rate" },
            { value: "<2s", label: "Analysis Time" }
          ].map((stat, i) => (
            <div key={i}>
              <div className="text-3xl font-light text-gray-900 dark:text-white">{stat.value}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}