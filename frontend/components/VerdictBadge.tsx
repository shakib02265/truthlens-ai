import React from 'react';

interface VerdictBadgeProps {
  verdict?: string | null;
  size?: 'sm' | 'md' | 'lg';
}

export const VerdictBadge: React.FC<VerdictBadgeProps> = ({ verdict = 'UNVERIFIED', size = 'md' }) => {
  const v = (verdict || 'UNVERIFIED').toUpperCase();

  let colorClasses = 'bg-slate-100 text-slate-700 border-slate-300';
  if (v.includes('TRUE') && !v.includes('MOSTLY FALSE') && !v.includes('PARTIALLY')) {
    colorClasses = 'bg-emerald-50 text-emerald-700 border-emerald-300';
  } else if (v.includes('MISLEADING') || v.includes('PARTIALLY')) {
    colorClasses = 'bg-amber-50 text-amber-800 border-amber-300';
  } else if (v.includes('FALSE')) {
    colorClasses = 'bg-rose-50 text-rose-700 border-rose-300';
  } else if (v.includes('INSUFFICIENT') || v.includes('UNVERIFIED')) {
    colorClasses = 'bg-gray-100 text-gray-700 border-gray-300';
  }

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs font-semibold',
    md: 'px-3 py-1 text-sm font-bold',
    lg: 'px-4 py-1.5 text-base font-extrabold',
  }[size];

  return (
    <span className={`inline-flex items-center rounded-full border shadow-sm ${colorClasses} ${sizeClasses}`}>
      {v}
    </span>
  );
};
