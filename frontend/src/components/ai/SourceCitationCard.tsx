import React, { useState } from 'react';
import type { SourceCitation } from '../../services/types';
import { FileText, ChevronDown, ChevronUp } from 'lucide-react';

interface SourceCitationCardProps {
  citation: SourceCitation;
}

export const SourceCitationCard: React.FC<SourceCitationCardProps> = ({ citation }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-slate-950/80 border border-slate-800/80 hover:border-cyan-500/40 rounded-xl p-3.5 transition-all text-xs">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center border border-cyan-500/20">
            <FileText className="w-3.5 h-3.5" />
          </div>
          <div>
            <h5 className="font-semibold text-slate-200 truncate max-w-[220px] sm:max-w-[320px]">
              {citation.document}
            </h5>
            <div className="flex items-center gap-2 text-[10px] text-slate-400 font-mono-code">
              {citation.pump_family && <span>Family: {citation.pump_family}</span>}
              {citation.page && <span>• Page {citation.page}</span>}
            </div>
          </div>
        </div>

        {citation.chunk_snippet && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-slate-400 hover:text-cyan-400 p-1 rounded-lg hover:bg-slate-900 transition-colors cursor-pointer flex items-center gap-1 text-[11px]"
          >
            <span>{isExpanded ? 'Hide Snippet' : 'View Snippet'}</span>
            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        )}
      </div>

      {isExpanded && citation.chunk_snippet && (
        <div className="mt-3 pt-3 border-t border-slate-900 text-[11px] text-slate-300 font-mono-code bg-slate-900/60 p-2.5 rounded-lg leading-relaxed border-l-2 border-cyan-500">
          "{citation.chunk_snippet}"
        </div>
      )}
    </div>
  );
};
