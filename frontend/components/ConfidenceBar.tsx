import React from 'react';

interface ConfidenceBarProps {
  score?: number | null; // 0.0 to 1.0
  showLabel?: boolean;
}

export const ConfidenceBar: React.FC<ConfidenceBarProps> = ({ score = 0.5, showLabel = true }) => {
  const percentage = Math.round((score || 0) * 100);

  let barColor = 'bg-emerald-500';
  let level = 'HIGH';
  if (percentage < 60) {
    barColor = 'bg-rose-500';
    level = 'LOW';
  } else if (percentage < 85) {
    barColor = 'bg-amber-500';
    level = 'MEDIUM';
  }

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex justify-between items-center mb-1 text-xs font-semibold text-slate-700">
          <span>Confidence Score</span>
          <span className="font-bold">{percentage}% ({level})</span>
        </div>
      )}
      <div className="w-full h-2.5 bg-slate-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${barColor} transition-all duration-500 ease-out rounded-full`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
