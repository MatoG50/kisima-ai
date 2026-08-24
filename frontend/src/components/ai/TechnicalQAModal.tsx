import React, { useState } from 'react';
import { api } from '../../services/api';
import type { AskResponse } from '../../services/types';
import { SourceCitationCard } from './SourceCitationCard';
import { HelpCircle, X, Search, RefreshCw, BookOpen, AlertCircle } from 'lucide-react';

interface TechnicalQAModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultPumpId?: string;
}

export const TechnicalQAModal: React.FC<TechnicalQAModalProps> = ({
  isOpen,
  onClose,
  defaultPumpId,
}) => {
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || question.length < 3) return;

    setIsLoading(true);
    setError(null);
    try {
      const res = await api.askAIQuestion({
        question: question.trim(),
        pump_id: defaultPumpId,
      });
      setResponse(res);
    } catch (err: any) {
      setError(err.message || 'Failed to search datasheet knowledge base.');
    } finally {
      setIsLoading(false);
    }
  };

  const sampleQuestions = [
    "What is the maximum immersion depth rating for DSD pumps?",
    "How does the Hazen-Williams friction loss formula affect pipe size choice?",
    "What electrical phase options are available for Dayliff solar pumps?",
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-2xl w-full p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-xl hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 flex items-center justify-center">
            <HelpCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">
              Manufacturer Datasheet RAG Q&A
            </h3>
            <p className="text-xs text-slate-400">
              Ask technical questions about pump specifications, curves, and engineering standards.
            </p>
          </div>
        </div>

        {/* Search Input Form */}
        <form onSubmit={handleSearch} className="mb-6">
          <div className="relative">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. What is the efficiency range of DSD08 pumps?"
              className="w-full pl-4 pr-12 py-3 bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-2xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20"
            />
            <button
              type="submit"
              disabled={isLoading || !question.trim()}
              className="absolute right-2 top-2 px-3 py-1.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-semibold disabled:opacity-50 cursor-pointer flex items-center gap-1"
            >
              {isLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
              <span>Search</span>
            </button>
          </div>

          {/* Quick sample chips */}
          <div className="flex flex-wrap gap-1.5 mt-3 text-[11px]">
            <span className="text-slate-400">Try asking:</span>
            {sampleQuestions.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setQuestion(q)}
                className="text-cyan-400/90 hover:text-cyan-300 bg-slate-950 px-2 py-0.5 rounded-lg border border-slate-800 hover:border-cyan-800 transition-colors"
              >
                "{q.slice(0, 32)}..."
              </button>
            ))}
          </div>
        </form>

        {/* Error message */}
        {error && (
          <div className="bg-rose-950/40 border border-rose-800/40 p-3.5 rounded-2xl text-xs text-rose-300 flex items-center gap-2 mb-4">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Result Area */}
        {response && (
          <div className="space-y-4 pt-4 border-t border-slate-800">
            <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800 text-xs text-slate-200 leading-relaxed">
              <span className="text-cyan-400 font-bold block mb-1">Answer from RAG Index:</span>
              <p className="whitespace-pre-line">{response.answer}</p>
            </div>

            {response.sources && response.sources.length > 0 && (
              <div>
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
                  Datasheet Citations ({response.sources.length})
                </h4>
                <div className="space-y-2">
                  {response.sources.map((src, idx) => (
                    <SourceCitationCard key={idx} citation={src} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
