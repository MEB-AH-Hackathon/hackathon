import Link from 'next/link';

export function SiteHeader() {
  return (
    <header className="border-b border-stone-200 dark:border-stone-700 bg-white/80 dark:bg-stone-900/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-stone-900 dark:bg-stone-100 rounded-lg flex items-center justify-center">
                <span className="text-white dark:text-stone-900 font-bold text-sm">V</span>
              </div>
              <span className="font-semibold text-stone-900 dark:text-stone-100">VAERS Analyzer</span>
            </Link>
          </div>
          <nav className="flex items-center space-x-6">
            <Link 
              href="/reports" 
              className="text-stone-600 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100 transition-colors"
            >
              Reports
            </Link>
            <Link 
              href="/reports/new" 
              className="bg-stone-900 dark:bg-stone-100 text-white dark:text-stone-900 px-4 py-2 rounded-lg font-medium hover:bg-stone-800 dark:hover:bg-stone-200 transition-colors"
            >
              New Report
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}