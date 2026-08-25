// frontend/src/pages/Studies.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, ChevronLeft, ChevronRight } from 'lucide-react';
import { useStudies } from '../hooks/useStudies';
import { StudyModality, StudyStatus, StudyFilters } from '../types/study';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import StatusBadge from '../components/StatusBadge';
import { formatPatientName, formatMRN, formatModality } from '../utils/formatting';
import { formatDate } from '../utils/date';

const Studies: React.FC = () => {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<StudyFilters>({
    page: 1,
    page_size: 10,
  });

  const { data, isLoading, error, refetch } = useStudies(filters);

  const handleFilterChange = (key: keyof StudyFilters, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value || undefined,
      page: 1, // Reset to first page on filter change
    }));
  };

  const handlePageChange = (newPage: number) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
  };

  const handleCreateStudy = () => {
    navigate('/studies/new');
  };

  const handleViewStudy = (id: string) => {
    navigate(`/studies/${id}`);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <ErrorState
          title="Failed to load studies"
          message={error.message || 'An error occurred while loading studies'}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  const hasFilters = filters.modality || filters.status || filters.patient_name;
  const isEmpty = !data?.items.length;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Studies</h1>
          <p className="text-gray-400 mt-1">
            {data?.total || 0} total studies
          </p>
        </div>
        <button
          onClick={handleCreateStudy}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <Plus size={18} />
          Create Study
        </button>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6 border border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Patient Name Search */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Patient Name
            </label>
            <input
              type="text"
              value={filters.patient_name || ''}
              onChange={(e) => handleFilterChange('patient_name', e.target.value)}
              placeholder="Search by name..."
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Modality Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Modality
            </label>
            <select
              value={filters.modality || ''}
              onChange={(e) => handleFilterChange('modality', e.target.value)}
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Modalities</option>
              {Object.values(StudyModality).map((modality) => (
                <option key={modality} value={modality}>
                  {formatModality(modality)}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Status
            </label>
            <select
              value={filters.status || ''}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Statuses</option>
              {Object.values(StudyStatus).map((status) => (
                <option key={status} value={status}>
                  {status.charAt(0) + status.slice(1).toLowerCase()}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Table or Empty State */}
      {isEmpty ? (
        <EmptyState
          title={hasFilters ? 'No studies found' : 'No studies yet'}
          message={
            hasFilters
              ? 'Try adjusting your filters to find studies'
              : 'Get started by creating your first study'
          }
          action={
            !hasFilters
              ? {
                  label: 'Create Study',
                  onClick: handleCreateStudy,
                }
              : undefined
          }
        />
      ) : (
        <>
          {/* Table */}
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Patient
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      MRN
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Modality
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Body Part
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Study Date
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {data?.items.map((study) => (
                    <tr
                      key={study.id}
                      className="hover:bg-gray-700/50 transition-colors cursor-pointer"
                      onClick={() => handleViewStudy(study.id)}
                    >
                      <td className="px-4 py-3 text-sm text-white">
                        {formatPatientName(
                          study.patient_first_name,
                          study.patient_last_name
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-300">
                        {formatMRN(study.patient_mrn)}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-300">
                        {formatModality(study.modality)}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-300">
                        {study.body_part_examined || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-300">
                        {formatDate(study.study_date)}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <StatusBadge status={study.status} />
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleViewStudy(study.id);
                          }}
                          className="text-blue-400 hover:text-blue-300 font-medium"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          {data && data.pages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <div className="text-sm text-gray-400">
                Page {data.page} of {data.pages}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handlePageChange(data.page - 1)}
                  disabled={data.page === 1}
                  className="flex items-center gap-1 px-3 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <ChevronLeft size={18} />
                  Previous
                </button>
                <button
                  onClick={() => handlePageChange(data.page + 1)}
                  disabled={data.page === data.pages}
                  className="flex items-center gap-1 px-3 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Next
                  <ChevronRight size={18} />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Studies;
