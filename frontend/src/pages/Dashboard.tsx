// frontend/src/pages/Dashboard.tsx
import { useNavigate } from 'react-router-dom';
import { Plus, FileText, Activity, Calendar, User, TrendingUp } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useStudies } from '../hooks/useStudies';
import { formatPatientName, formatMRN, formatModality } from '../utils/formatting';
import { formatDate } from '../utils/date';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { data: recentStudies, isLoading } = useStudies({ page: 1, page_size: 5 });

  const handleCreateStudy = () => {
    navigate('/studies/new');
  };

  const handleViewAllStudies = () => {
    navigate('/studies');
  };

  const handleViewStudy = (id: string) => {
    navigate(`/studies/${id}`);
  };

  return (
    <div className="p-6">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Welcome back, {user?.full_name || 'User'}
        </h1>
        <p className="text-gray-400">
          Medical Imaging AI Workstation
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Total Studies Card */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-blue-900/30 rounded-lg flex items-center justify-center">
              <FileText size={24} className="text-blue-400" />
            </div>
            <TrendingUp size={20} className="text-green-400" />
          </div>
          <h3 className="text-2xl font-bold text-white mb-1">
            {isLoading ? '...' : recentStudies?.total || 0}
          </h3>
          <p className="text-sm text-gray-400">Total Studies</p>
        </div>

        {/* Active Studies Card */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-green-900/30 rounded-lg flex items-center justify-center">
              <Activity size={24} className="text-green-400" />
            </div>
            <TrendingUp size={20} className="text-green-400" />
          </div>
          <h3 className="text-2xl font-bold text-white mb-1">
            {isLoading ? '...' : recentStudies?.items.filter(s => s.status === 'ready').length || 0}
          </h3>
          <p className="text-sm text-gray-400">Ready Studies</p>
        </div>

        {/* Recent Activity Card */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-purple-900/30 rounded-lg flex items-center justify-center">
              <Calendar size={24} className="text-purple-400" />
            </div>
            <TrendingUp size={20} className="text-green-400" />
          </div>
          <h3 className="text-2xl font-bold text-white mb-1">
            {isLoading ? '...' : recentStudies?.items.length || 0}
          </h3>
          <p className="text-sm text-gray-400">Recent Studies</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <button
          onClick={handleCreateStudy}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg p-6 transition-colors text-left group"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
              <Plus size={24} />
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-1">Create New Study</h3>
              <p className="text-blue-100 text-sm">Add patient and imaging data</p>
            </div>
          </div>
        </button>

        <button
          onClick={handleViewAllStudies}
          className="bg-gray-800 hover:bg-gray-700 text-white rounded-lg p-6 transition-colors text-left border border-gray-700 group"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gray-700 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
              <FileText size={24} className="text-gray-300" />
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-1">View All Studies</h3>
              <p className="text-gray-400 text-sm">Browse and search studies</p>
            </div>
          </div>
        </button>
      </div>

      {/* Recent Studies */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">Recent Studies</h2>
            <button
              onClick={handleViewAllStudies}
              className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors"
            >
              View All →
            </button>
          </div>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="md" />
          </div>
        ) : recentStudies?.items.length ? (
          <div className="divide-y divide-gray-700">
            {recentStudies.items.map((study) => (
              <div
                key={study.id}
                onClick={() => handleViewStudy(study.id)}
                className="p-4 hover:bg-gray-700/50 transition-colors cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1">
                    <div className="w-10 h-10 bg-gray-700 rounded-lg flex items-center justify-center">
                      <User size={20} className="text-gray-400" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-white font-medium mb-1">
                        {formatPatientName(study.patient_first_name, study.patient_last_name)}
                      </h3>
                      <div className="flex items-center gap-3 text-sm text-gray-400">
                        <span className="font-mono">{formatMRN(study.patient_mrn)}</span>
                        <span>•</span>
                        <span>{formatModality(study.modality)}</span>
                        <span>•</span>
                        <span>{formatDate(study.study_date)}</span>
                      </div>
                    </div>
                  </div>
                  <StatusBadge status={study.status} />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center">
            <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText size={32} className="text-gray-500" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">No studies yet</h3>
            <p className="text-gray-400 mb-4">Get started by creating your first study</p>
            <button
              onClick={handleCreateStudy}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
            >
              Create Study
            </button>
          </div>
        )}
      </div>

      {/* Feature Preview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        {/* DICOM Viewer Preview */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-blue-900/30 rounded-lg flex items-center justify-center">
              <Activity size={20} className="text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold text-white">DICOM Viewer</h3>
          </div>
          <p className="text-sm text-gray-400 mb-4">
            Advanced medical image viewing with MPR, windowing, and measurement tools
          </p>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-900/20 text-blue-400 rounded text-xs border border-blue-700/30">
            <Calendar size={14} />
            Sprint 4
          </div>
        </div>

        {/* AI Analysis Preview */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-pink-900/30 rounded-lg flex items-center justify-center">
              <Activity size={20} className="text-pink-400" />
            </div>
            <h3 className="text-lg font-semibold text-white">AI Analysis</h3>
          </div>
          <p className="text-sm text-gray-400 mb-4">
            Automated detection, segmentation, and classification of medical images
          </p>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-pink-900/20 text-pink-400 rounded text-xs border border-pink-700/30">
            <Calendar size={14} />
            Sprint 5
          </div>
        </div>

        {/* AI Copilot Preview */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-cyan-900/30 rounded-lg flex items-center justify-center">
              <Activity size={20} className="text-cyan-400" />
            </div>
            <h3 className="text-lg font-semibold text-white">AI Copilot</h3>
          </div>
          <p className="text-sm text-gray-400 mb-4">
            Interactive AI assistant for diagnosis support and clinical decision making
          </p>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-cyan-900/20 text-cyan-400 rounded text-xs border border-cyan-700/30">
            <Calendar size={14} />
            Sprint 7
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
