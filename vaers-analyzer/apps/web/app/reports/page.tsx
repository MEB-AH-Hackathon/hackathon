import { getReports } from '../actions/reports';
import { ReportsHeader } from './components/ReportsHeader';
import { ReportList } from './components/ReportList';
import { Pagination } from './components/Pagination';

export default async function ReportsPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string; limit?: string }>;
}) {
  const params = await searchParams;
  const page = parseInt(params.page || '1');
  const limit = parseInt(params.limit || '20');
  const offset = (page - 1) * limit;

  const { reports, pagination } = await getReports(limit, offset);
  const totalPages = Math.ceil(pagination.total / limit);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <ReportsHeader />
      <ReportList reports={reports} />
      <Pagination
        currentPage={page}
        totalPages={totalPages}
        limit={limit}
        total={pagination.total}
      />
    </div>
  );
}