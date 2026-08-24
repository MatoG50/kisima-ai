import React from 'react';
import type { RejectionSummary as RejectionSummaryType } from '../../services/types';
import { Layers } from 'lucide-react';

interface RejectionSummaryProps {
  summary?: RejectionSummaryType;
}

export const RejectionSummaryCard: React.FC<RejectionSummaryProps> = ({ summary }) => {
  if (!summary) return null;

  return (
    <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-4 text-xs">
      <div className="flex items-center justify-between mb-3">
        <span className="font-bold text-slate-300 flex items-center gap-1.5">
          <Layers className="w-4 h-4 text-cyan-400" />
          Catalog Evaluation Audit
        </span>
        <span className="font-mono-code text-slate-400">
          {summary.viable_candidates_count} / {summary.total_candidates_evaluated} Viable Candidates
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
          <span className="text-slate-400 block text-[10px]">Evaluated</span>
          <span className="font-mono-code font-bold text-slate-200">{summary.total_candidates_evaluated}</span>
        </div>
        <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
          <span className="text-slate-400 block text-[10px]">Depth Exceeded</span>
          <span className="font-mono-code font-bold text-rose-400">{summary.rejected_depth_exceeded}</span>
        </div>
        <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
          <span className="text-slate-400 block text-[10px]">Insufficient Head</span>
          <span className="font-mono-code font-bold text-amber-400">{summary.rejected_insufficient_head}</span>
        </div>
        <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
          <span className="text-slate-400 block text-[10px]">Out of Curve Range</span>
          <span className="font-mono-code font-bold text-slate-400">{summary.rejected_out_of_range}</span>
        </div>
      </div>
    </div>
  );
};
