import Link from 'next/link';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  limit: number;
  total: number;
  baseUrl?: string;
}

export function Pagination({ 
  currentPage, 
  totalPages, 
  limit, 
  total,
  baseUrl = '/reports' 
}: PaginationProps) {
  const offset = (currentPage - 1) * limit;
  
  if (totalPages <= 1) return null;

  return (
    <div className="mt-6 flex items-center justify-between">
      <MobilePagination 
        currentPage={currentPage}
        totalPages={totalPages}
        limit={limit}
        baseUrl={baseUrl}
      />
      
      <DesktopPagination
        currentPage={currentPage}
        totalPages={totalPages}
        limit={limit}
        offset={offset}
        total={total}
        baseUrl={baseUrl}
      />
    </div>
  );
}

function MobilePagination({ currentPage, totalPages, limit, baseUrl }: {
  currentPage: number;
  totalPages: number;
  limit: number;
  baseUrl: string;
}) {
  return (
    <div className="flex-1 flex justify-between sm:hidden">
      {currentPage > 1 && (
        <Link
          href={`${baseUrl}?page=${currentPage - 1}&limit=${limit}`}
          className="relative inline-flex items-center px-4 py-2 border border-stone-300 dark:border-stone-600 text-sm font-medium rounded-xl text-stone-700 dark:text-stone-300 bg-white/80 dark:bg-stone-800/80 hover:bg-white dark:hover:bg-stone-800 transition-all duration-300 shadow-sm"
        >
          Previous
        </Link>
      )}
      {currentPage < totalPages && (
        <Link
          href={`${baseUrl}?page=${currentPage + 1}&limit=${limit}`}
          className="ml-3 relative inline-flex items-center px-4 py-2 border border-stone-300 dark:border-stone-600 text-sm font-medium rounded-xl text-stone-700 dark:text-stone-300 bg-white/80 dark:bg-stone-800/80 hover:bg-white dark:hover:bg-stone-800 transition-all duration-300 shadow-sm"
        >
          Next
        </Link>
      )}
    </div>
  );
}

function DesktopPagination({ 
  currentPage, 
  totalPages, 
  limit, 
  offset, 
  total,
  baseUrl 
}: {
  currentPage: number;
  totalPages: number;
  limit: number;
  offset: number;
  total: number;
  baseUrl: string;
}) {
  // Calculate page numbers to show
  const pageNumbers = getPageNumbers(currentPage, totalPages);

  return (
    <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
      <div>
        <p className="text-sm text-stone-600 dark:text-stone-400">
          Showing{' '}
          <span className="font-semibold text-stone-900 dark:text-stone-100">{offset + 1}</span>
          {' to '}
          <span className="font-semibold text-stone-900 dark:text-stone-100">
            {Math.min(offset + limit, total)}
          </span>
          {' of '}
          <span className="font-semibold text-stone-900 dark:text-stone-100">{total}</span>
          {' results'}
        </p>
      </div>
      <div>
        <nav className="relative z-0 inline-flex rounded-xl shadow-sm -space-x-px" aria-label="Pagination">
          {currentPage > 1 && (
            <Link
              href={`${baseUrl}?page=${currentPage - 1}&limit=${limit}`}
              className="relative inline-flex items-center px-3 py-2 rounded-l-xl border border-stone-300 dark:border-stone-600 bg-white/80 dark:bg-stone-800/80 text-sm font-medium text-stone-500 dark:text-stone-400 hover:bg-white dark:hover:bg-stone-800 transition-all duration-300"
            >
              <span className="sr-only">Previous</span>
              <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </Link>
          )}
          
          {pageNumbers.map((pageNum, idx) => (
            pageNum === '...' ? (
              <span
                key={`ellipsis-${idx}`}
                className="relative inline-flex items-center px-4 py-2 border border-stone-300 dark:border-stone-600 bg-white/80 dark:bg-stone-800/80 text-sm font-medium text-stone-700 dark:text-stone-300"
              >
                ...
              </span>
            ) : (
              <Link
                key={pageNum}
                href={`${baseUrl}?page=${pageNum}&limit=${limit}`}
                className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium transition-all duration-300 ${
                  pageNum === currentPage
                    ? 'z-10 bg-stone-100 dark:bg-stone-700 border-stone-400 dark:border-stone-500 text-stone-900 dark:text-stone-100'
                    : 'bg-white/80 dark:bg-stone-800/80 border-stone-300 dark:border-stone-600 text-stone-500 dark:text-stone-400 hover:bg-white dark:hover:bg-stone-800'
                }`}
              >
                {pageNum}
              </Link>
            )
          ))}
          
          {currentPage < totalPages && (
            <Link
              href={`${baseUrl}?page=${currentPage + 1}&limit=${limit}`}
              className="relative inline-flex items-center px-3 py-2 rounded-r-xl border border-stone-300 dark:border-stone-600 bg-white/80 dark:bg-stone-800/80 text-sm font-medium text-stone-500 dark:text-stone-400 hover:bg-white dark:hover:bg-stone-800 transition-all duration-300"
            >
              <span className="sr-only">Next</span>
              <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </Link>
          )}
        </nav>
      </div>
    </div>
  );
}

function getPageNumbers(currentPage: number, totalPages: number): (number | string)[] {
  const delta = 2;
  const range: number[] = [];
  const rangeWithDots: (number | string)[] = [];
  let l: number;

  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= currentPage - delta && i <= currentPage + delta)) {
      range.push(i);
    }
  }

  range.forEach((i) => {
    if (l) {
      if (i - l === 2) {
        rangeWithDots.push(l + 1);
      } else if (i - l !== 1) {
        rangeWithDots.push('...');
      }
    }
    rangeWithDots.push(i);
    l = i;
  });

  return rangeWithDots;
}