import React from 'react';
import { ShieldCheck, AlertTriangle, ShieldAlert, CheckCircle2 } from 'lucide-react';

interface AbstractionBadgeProps {
  status?: string;
  warnings?: string[];
}

export const AbstractionBadge: React.FC<AbstractionBadgeProps> = ({ status, warnings = [] }) => {
  if (!status && warnings.length === 0) return null;

  const normalizedStatus = status?.toUpperCase() || 'SUSTAINABLE';

  if (normalizedStatus === 'SUSTAINABLE') {
    return (
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
        <ShieldCheck className="w-3.5 h-3.5" />
        <span>Sustainable Abstraction Rate</span>
      </div>
    );
  }

  if (normalizedStatus === 'HIGH_ABSTRACTION') {
    return (
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold">
        <AlertTriangle className="w-3.5 h-3.5" />
        <span>High Abstraction Rate Warning</span>
      </div>
    );
  }

  if (normalizedStatus === 'EXCEEDS_YIELD') {
    return (
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold">
        <ShieldAlert className="w-3.5 h-3.5" />
        <span>Exceeds Tested Yield Capacity</span>
      </div>
    );
  }

  return (
    <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold">
      <CheckCircle2 className="w-3.5 h-3.5" />
      <span>{normalizedStatus}</span>
    </div>
  );
};
