import React from 'react';
import type { ExplainResponse } from '../../services/types';
import { SourceCitationCard } from './SourceCitationCard';
import { BookOpen, UserCheck, RefreshCw, AlertCircle } from 'lucide-react';

interface AIExplanationSectionProps {
  explanation: ExplainResponse | null;
  isLoading: boolean;
  error: string | null;
  onRefresh: () => void;
  pumpName?: string;
}

export const AIExplanationSection: React.FC<AIExplanationSectionProps> = ({
  explanation,
  isLoading,
  error,
  onRefresh,
  pumpName,
}) => {
  if (isLoading) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-8 shadow-xl text-center">
        <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 flex items-center justify-center mx-auto mb-4 animate-spin">
          <RefreshCw className="w-6 h-6" />
        </div>
        <h4 className="text-lg font-bold text-slate-100 mb-2">
          Generating Technical Sales Engineer Explanation...
        </h4>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          Querying ChromaDB vector store for <span className="text-cyan-300 font-bold">{pumpName || 'pump'}</span> manufacturer PDF datasheets & synthesizing technical context...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-slate-900/60 border border-rose-500/30 rounded-3xl p-6 shadow-xl text-slate-300">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-rose-400">
            <AlertCircle className="w-5 h-5" />
            <h4 className="font-bold text-sm">AI Technical Explanation Error</h4>
          </div>
          <button
            onClick={onRefresh}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 flex items-center gap-1.5 cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Retry
          </button>
        </div>
        <p className="text-xs text-rose-300 bg-rose-950/40 p-3 rounded-xl border border-rose-800/40 font-mono-code">
          {error}
        </p>
      </div>
    );
  }

  if (!explanation) return null;

  return (
    <div className="bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 border border-cyan-500/40 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 p-0.5 shadow-md shadow-cyan-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <UserCheck className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-slate-100">
                Technical Sales Engineer Recommendation Rationale
              </h3>
              <span className="text-[10px] font-bold uppercase tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2 py-0.5 rounded-full">
                RAG Datasheet Backed
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Customer-ready explanation generated using verified manufacturer performance documents.
            </p>
          </div>
        </div>

        <button
          onClick={onRefresh}
          className="text-xs text-slate-400 hover:text-cyan-400 bg-slate-950 hover:bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-800 transition-colors flex items-center gap-1.5 cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Regenerate</span>
        </button>
      </div>

      {/* Main Narrative Content */}
      <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed space-y-3 bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80">
        {explanation.answer.split('\n\n').map((paragraph, idx) => (
          <p key={idx}>{paragraph}</p>
        ))}
      </div>

      {/* Manufacturer Datasheet Citations */}
      {explanation.sources && explanation.sources.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <BookOpen className="w-4 h-4 text-cyan-400" />
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Retrieved Manufacturer Datasheet Citations ({explanation.sources.length})
            </h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {explanation.sources.map((src, idx) => (
              <SourceCitationCard key={idx} citation={src} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
