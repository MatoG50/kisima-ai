import React, { useState } from 'react';
import { api } from '../../services/api';
import type { AskResponse } from '../../services/types';
import { SourceCitationCard } from './SourceCitationCard';
import { Bot, User, X, Search, RefreshCw, BookOpen, AlertCircle, Sparkles } from 'lucide-react';

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
  const [lastAskedQuestion, setLastAskedQuestion] = useState<string | null>(null);
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSearch = async (userQuery: string) => {
    const qText = userQuery.trim();
    if (!qText || qText.length < 3) return;

    setIsLoading(true);
    setError(null);
    setLastAskedQuestion(qText);

    try {
      const res = await api.askAIQuestion({
        question: qText,
        pump_id: defaultPumpId,
      });
      setResponse(res);
    } catch (err: any) {
      setError(err.message || 'Failed to query manufacturer datasheet documentation.');
    } finally {
      setIsLoading(false);
    }
  };

  const sampleQuestions = [
    "What is the maximum immersion depth?",
    "What materials are used in DSD pumps?",
    "What electrical phase options are available?",
    "What is the minimum borehole diameter?",
    "What type of liquid can this pump handle?",
    "What is the maximum liquid temperature?",
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-2xl w-full p-6 shadow-2xl relative max-h-[90vh] flex flex-col">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1.5 rounded-xl hover:bg-slate-800 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3 mb-4 pb-4 border-b border-slate-800">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 flex items-center justify-center shrink-0">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-slate-100">
                Manufacturer AI Assistant
              </h3>
              <span className="text-[10px] uppercase font-extrabold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Available Now
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Ask questions about pump specifications and manufacturer documentation.
            </p>
          </div>
        </div>

        {/* Scrollable Conversation Content Area */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-1 mb-4">
          {/* Default Welcome Banner if no response yet */}
          {!response && !isLoading && (
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-4 text-xs text-slate-300 space-y-2">
              <div className="flex items-center gap-2 text-cyan-400 font-bold">
                <Sparkles className="w-4 h-4" />
                <span>Datasheet Knowledge Assistant</span>
              </div>
              <p className="text-slate-400 leading-relaxed">
                Query manufacturer specifications directly from PDF technical documentation for Dayliff DSD, DS, DSS, and DSP pump series. Select a suggested question below or type your own question.
              </p>
            </div>
          )}

          {/* Conversational Message Thread */}
          {lastAskedQuestion && (
            <div className="space-y-3">
              {/* User Question Bubble */}
              <div className="flex items-start justify-end gap-2.5">
                <div className="bg-cyan-950/50 border border-cyan-800/60 text-slate-100 rounded-2xl rounded-tr-none px-4 py-3 text-xs max-w-[85%] shadow-sm">
                  <div className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider mb-1 flex items-center gap-1 justify-end">
                    <span>You</span>
                    <User className="w-3 h-3" />
                  </div>
                  <p>{lastAskedQuestion}</p>
                </div>
              </div>

              {/* Loading Indicator */}
              {isLoading && (
                <div className="flex items-start gap-2.5">
                  <div className="w-7 h-7 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 flex items-center justify-center shrink-0 mt-1">
                    <Bot className="w-4 h-4 animate-pulse" />
                  </div>
                  <div className="bg-slate-950 border border-slate-800 rounded-2xl rounded-tl-none px-4 py-3 text-xs text-slate-400 flex items-center gap-2">
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                    <span>Searching manufacturer datasheets...</span>
                  </div>
                </div>
              )}

              {/* AI Response Bubble */}
              {!isLoading && response && (
                <div className="flex items-start gap-2.5">
                  <div className="w-7 h-7 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 flex items-center justify-center shrink-0 mt-1">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="bg-slate-950 border border-slate-800 text-slate-200 rounded-2xl rounded-tl-none p-4 text-xs leading-relaxed max-w-[90%] space-y-3">
                    <div>
                      <div className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider mb-1">
                        Kisima AI
                      </div>
                      <p className="whitespace-pre-line">{response.answer}</p>
                    </div>

                    {/* Datasheet Sources Citation Section */}
                    {response.sources && response.sources.length > 0 && (
                      <div className="pt-3 border-t border-slate-800/80">
                        <h4 className="text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                          <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
                          Sources ({response.sources.length})
                        </h4>
                        <div className="space-y-2">
                          {response.sources.map((src, idx) => (
                            <SourceCitationCard key={idx} citation={src} />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-rose-950/40 border border-rose-800/40 p-3.5 rounded-2xl text-xs text-rose-300 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Suggested Questions Chips */}
        <div className="mb-3 pt-3 border-t border-slate-800/80">
          <span className="text-[11px] text-slate-400 block mb-2 font-medium">
            Suggested Questions:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {sampleQuestions.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setQuestion(q);
                  handleSearch(q);
                }}
                className="text-xs text-cyan-300/90 hover:text-cyan-200 bg-slate-950 hover:bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-800 hover:border-cyan-500/40 transition-all cursor-pointer text-left"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Input Form Footer */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch(question);
          }}
        >
          <div className="relative">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a technical question about pump specifications..."
              className="w-full pl-4 pr-24 py-3 bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-2xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20"
            />
            <button
              type="submit"
              disabled={isLoading || !question.trim()}
              className="absolute right-2 top-2 px-4 py-1.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-semibold disabled:opacity-50 cursor-pointer flex items-center gap-1.5 transition-all shadow-md shadow-cyan-500/20"
            >
              {isLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
              <span>Ask AI</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
