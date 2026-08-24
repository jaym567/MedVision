// frontend/src/components/SafetyNotice.tsx
/**
 * Safety notice banner for medical data warning
 */

import { AlertTriangle } from 'lucide-react';

interface SafetyNoticeProps {
  className?: string;
}

export default function SafetyNotice({ className = '' }: SafetyNoticeProps) {
  return (
    <div
      className={`
        bg-yellow-900/20 border border-yellow-600/50 rounded-lg p-4
        flex items-start gap-3
        ${className}
      `}
      role="alert"
    >
      <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
      <div className="text-sm">
        <p className="font-semibold text-yellow-500 mb-1">
          ⚠️ Research Use Only - Mock Data
        </p>
        <p className="text-yellow-200/90">
          This platform is for research and educational purposes only.
          <strong className="font-medium"> Do not enter real patient information or PHI.</strong>
          {' '}Use mock/de-identified data only.
        </p>
      </div>
    </div>
  );
}
