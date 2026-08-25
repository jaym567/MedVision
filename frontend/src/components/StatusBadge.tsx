// frontend/src/components/StatusBadge.tsx
import { StudyStatus } from '../types/study';

interface StatusBadgeProps {
  status: StudyStatus;
}

const statusConfig: Record<StudyStatus, { label: string; className: string }> = {
  [StudyStatus.CREATED]: {
    label: 'Created',
    className: 'bg-blue-900/50 text-blue-300 border-blue-700',
  },
  [StudyStatus.UPLOADED]: {
    label: 'Uploaded',
    className: 'bg-indigo-900/50 text-indigo-300 border-indigo-700',
  },
  [StudyStatus.PROCESSING]: {
    label: 'Processing',
    className: 'bg-yellow-900/50 text-yellow-300 border-yellow-700',
  },
  [StudyStatus.READY]: {
    label: 'Ready',
    className: 'bg-green-900/50 text-green-300 border-green-700',
  },
  [StudyStatus.FAILED]: {
    label: 'Failed',
    className: 'bg-red-900/50 text-red-300 border-red-700',
  },
  [StudyStatus.ARCHIVED]: {
    label: 'Archived',
    className: 'bg-gray-900/50 text-gray-400 border-gray-700',
  },
};

const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const config = statusConfig[status];

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.className}`}
    >
      {config.label}
    </span>
  );
};

export default StatusBadge;
