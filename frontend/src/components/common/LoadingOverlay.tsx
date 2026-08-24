import React from 'react';
import { Waves, Activity } from 'lucide-react';

interface LoadingOverlayProps {
  message?: string;
  subtext?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  message = "Evaluating pump performance...",
  subtext = "Querying PostgreSQL catalog, interpolating H-Q curves & calculating Hazen-Williams friction loss...",
}) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-12 text-center shadow-2xl backdrop-blur-md max-w-xl mx-auto my-8">
      <div className="relative w-20 h-20 mx-auto mb-6">
        {/* Animated outer ring */}
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-500 animate-spin opacity-40 blur-sm" />
        <div className="absolute inset-1 bg-slate-950 rounded-[14px] flex items-center justify-center border border-cyan-500/50">
          <Waves className="w-8 h-8 text-cyan-400 animate-pulse" />
        </div>
      </div>

      <h3 className="text-xl font-bold text-slate-100 mb-2">
        {message}
      </h3>
      <p className="text-xs text-slate-400 leading-relaxed max-w-md mx-auto mb-6">
        {subtext}
      </p>

      <div className="inline-flex items-center gap-2 text-xs font-mono-code text-cyan-400 bg-cyan-950/60 px-4 py-1.5 rounded-full border border-cyan-800/60">
        <Activity className="w-3.5 h-3.5 animate-pulse" />
        <span>Executing Hazen-Williams Hydraulic Engine</span>
      </div>
    </div>
  );
};
