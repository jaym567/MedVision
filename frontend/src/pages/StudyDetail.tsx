// frontend/src/pages/StudyDetail.tsx
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Calendar, Activity, FileText, Brain, Stethoscope, MessageSquare } from 'lucide-react';
import { useStudy } from '../hooks/useStudy';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorState from '../components/ErrorState';
import StatusBadge from '../components/StatusBadge';
import { formatPatientName, formatMRN, formatModality } from '../utils/formatting';
import { formatDate, formatDateTime, calculateAge } from '../utils/date';

const StudyDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: study, isLoading, error, refetch } = useStudy(id);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !study) {
    return (
      <div className="p-6">
        <ErrorState
          title="Failed to load study"
          message={error?.message || 'Study not found'}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  const patientAge = study.patient?.date_of_birth
    ? calculateAge(study.patient.date_of_birth)
    : 'Unknown';

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/studies')}
          className="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors"
        >
          <ArrowLeft size={18} />
          Back to Studies
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">
              {study.patient
                ? formatPatientName(study.patient.first_name, study.patient.last_name)
                : 'Unknown Patient'}
            </h1>
            <p className="text-gray-400 mt-1">
              {formatModality(study.modality)} Study • {formatDate(study.study_date)}
            </p>
          </div>
          <StatusBadge status={study.status} />
        </div>
      </div>

      {/* Three-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Sidebar - Patient & Study Info */}
        <div className="lg:col-span-3 space-y-6">
          {/* Patient Summary Card */}
          {study.patient && (
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center gap-2 mb-4">
                <User size={18} className="text-blue-400" />
                <h2 className="text-lg font-semibold text-white">Patient Information</h2>
              </div>
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-gray-400 uppercase">Name</p>
                  <p className="text-sm text-white font-medium">
                    {formatPatientName(study.patient.first_name, study.patient.last_name)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-400 uppercase">MRN</p>
                  <p className="text-sm text-white font-mono">
                    {formatMRN(study.patient.mrn)}
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-xs text-gray-400 uppercase">Age</p>
                    <p className="text-sm text-white">{patientAge} years</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400 uppercase">Sex</p>
                    <p className="text-sm text-white">
                      {study.patient.sex === 'M' ? 'Male' : study.patient.sex === 'F' ? 'Female' : 'Other'}
                    </p>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-gray-400 uppercase">Date of Birth</p>
                  <p className="text-sm text-white">{formatDate(study.patient.date_of_birth)}</p>
                </div>
                {study.patient.medical_history && (
                  <div>
                    <p className="text-xs text-gray-400 uppercase">Medical History</p>
                    <p className="text-sm text-gray-300 whitespace-pre-wrap">
                      {study.patient.medical_history}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Study Details Card */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center gap-2 mb-4">
              <Activity size={18} className="text-green-400" />
              <h2 className="text-lg font-semibold text-white">Study Details</h2>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-gray-400 uppercase">Modality</p>
                <p className="text-sm text-white font-medium">
                  {formatModality(study.modality)}
                </p>
              </div>
              {study.body_part && (
                <div>
                  <p className="text-xs text-gray-400 uppercase">Body Part</p>
                  <p className="text-sm text-white">{study.body_part}</p>
                </div>
              )}
              {study.study_description && (
                <div>
                  <p className="text-xs text-gray-400 uppercase">Description</p>
                  <p className="text-sm text-gray-300">{study.study_description}</p>
                </div>
              )}
              <div>
                <p className="text-xs text-gray-400 uppercase">Study Date</p>
                <p className="text-sm text-white">{formatDate(study.study_date)}</p>
              </div>
              {study.accession_number && (
                <div>
                  <p className="text-xs text-gray-400 uppercase">Accession Number</p>
                  <p className="text-sm text-white font-mono">{study.accession_number}</p>
                </div>
              )}
              {study.created_by_user && (
                <div>
                  <p className="text-xs text-gray-400 uppercase">Created By</p>
                  <p className="text-sm text-white">{study.created_by_user.full_name}</p>
                  <p className="text-xs text-gray-500">{study.created_by_user.email}</p>
                </div>
              )}
              <div>
                <p className="text-xs text-gray-400 uppercase">Created</p>
                <p className="text-sm text-gray-300">{formatDateTime(study.created_at)}</p>
              </div>
              {study.updated_at && (
                <div>
                  <p className="text-xs text-gray-400 uppercase">Last Updated</p>
                  <p className="text-sm text-gray-300">{formatDateTime(study.updated_at)}</p>
                </div>
              )}
            </div>
          </div>

          {/* Metadata Card */}
          {study.metadata_json && Object.keys(study.metadata_json).length > 0 && (
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center gap-2 mb-4">
                <FileText size={18} className="text-purple-400" />
                <h2 className="text-lg font-semibold text-white">Metadata</h2>
              </div>
              <pre className="text-xs text-gray-300 overflow-x-auto bg-gray-900 rounded p-3 border border-gray-700">
                {JSON.stringify(study.metadata_json, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Center - DICOM Viewer Placeholder */}
        <div className="lg:col-span-6">
          <div className="bg-gray-800 rounded-lg p-8 border border-gray-700 h-full min-h-[600px] flex items-center justify-center">
            <div className="text-center">
              <div className="w-20 h-20 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
                <Activity size={40} className="text-gray-500" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">DICOM Viewer</h3>
              <p className="text-gray-400 mb-4">
                Image viewing and manipulation tools
              </p>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-900/20 text-blue-400 rounded-md border border-blue-700/30">
                <Calendar size={16} />
                <span className="text-sm font-medium">Coming in Sprint 4</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar - AI Results, Reports, Copilot */}
        <div className="lg:col-span-3 space-y-6">
          {/* AI Analysis Placeholder */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center gap-2 mb-4">
              <Brain size={18} className="text-pink-400" />
              <h2 className="text-lg font-semibold text-white">AI Analysis</h2>
            </div>
            <div className="text-center py-6">
              <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
                <Brain size={24} className="text-gray-500" />
              </div>
              <p className="text-sm text-gray-400 mb-3">
                Automated detection and classification
              </p>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-pink-900/20 text-pink-400 rounded text-xs border border-pink-700/30">
                <Calendar size={14} />
                Sprint 5
              </div>
            </div>
          </div>

          {/* Reports Placeholder */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center gap-2 mb-4">
              <Stethoscope size={18} className="text-yellow-400" />
              <h2 className="text-lg font-semibold text-white">Reports</h2>
            </div>
            <div className="text-center py-6">
              <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
                <Stethoscope size={24} className="text-gray-500" />
              </div>
              <p className="text-sm text-gray-400 mb-3">
                Diagnostic reports and findings
              </p>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-yellow-900/20 text-yellow-400 rounded text-xs border border-yellow-700/30">
                <Calendar size={14} />
                Sprint 6
              </div>
            </div>
          </div>

          {/* AI Copilot Placeholder */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center gap-2 mb-4">
              <MessageSquare size={18} className="text-cyan-400" />
              <h2 className="text-lg font-semibold text-white">AI Copilot</h2>
            </div>
            <div className="text-center py-6">
              <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
                <MessageSquare size={24} className="text-gray-500" />
              </div>
              <p className="text-sm text-gray-400 mb-3">
                Interactive AI assistance
              </p>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-cyan-900/20 text-cyan-400 rounded text-xs border border-cyan-700/30">
                <Calendar size={14} />
                Sprint 7
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudyDetail;
