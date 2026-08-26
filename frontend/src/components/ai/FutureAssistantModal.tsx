import React from 'react';
import { Bot, X, ArrowRight, CheckCircle2, User, Clock } from 'lucide-react';

interface FutureAssistantModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLaunchForm: () => void;
}

export const FutureAssistantModal: React.FC<FutureAssistantModalProps> = ({
  isOpen,
  onClose,
  onLaunchForm,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-xl w-full p-6 shadow-2xl relative overflow-hidden">
        {/* Glow Background */}
        <div className="absolute top-0 right-0 w-60 h-60 bg-gradient-to-tr from-cyan-500/10 via-blue-500/10 to-transparent rounded-full blur-3xl pointer-events-none" />

        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-xl hover:bg-slate-800 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-cyan-500 p-0.5 shadow-lg shadow-cyan-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
              <Bot className="w-6 h-6 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-slate-100">
                Kisima AI Copilot
              </h3>
              <span className="inline-flex items-center gap-1 text-[10px] uppercase font-extrabold tracking-wider bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded-full">
                <Clock className="w-3 h-3" />
                Coming Soon
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Natural-Language Hydraulic Parameter Collection (Future Feature)
            </p>
          </div>
        </div>

        {/* Purpose Explanation & Dialogue Demonstration */}
        <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800 space-y-4 mb-6">
          <p className="text-xs text-slate-300 leading-relaxed">
            The future <strong>Kisima AI Copilot</strong> will allow customers to describe their water supply requirements conversationally. It will extract provided parameters, ask for missing engineering inputs, and pass validated inputs to the deterministic calculation engine.
          </p>

          <div className="space-y-2">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
              Planned Dialogue Flow Example:
            </span>
            <div className="bg-slate-900/90 p-4 rounded-xl border border-slate-800/80 space-y-3 text-xs">
              {/* User message */}
              <div className="flex items-start gap-2 text-slate-200">
                <User className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-cyan-400 block text-[10px] uppercase">You</span>
                  <p className="italic text-slate-300">"I need a pump for my borehole with a yield of 12 m³/h."</p>
                </div>
              </div>

              <div className="h-px bg-slate-800/80" />

              {/* Kisima AI message */}
              <div className="flex items-start gap-2 text-slate-200">
                <Bot className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-cyan-400 block text-[10px] uppercase">Kisima AI</span>
                  <p className="text-slate-200">
                    "Got it. I've captured a borehole yield of 12 m³/h. What is the pumping water level (PWL)?"
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-900 text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Converts natural language dialogue into structured engineering parameters</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />
              <span>Calls the authoritative deterministic calculation engine</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0" />
              <span>Prevents invented engineering values</span>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between gap-3">
          <span className="text-xs text-slate-400">
            Use the current hydraulic workspace form to size pumps today.
          </span>
          <button
            onClick={() => {
              onClose();
              onLaunchForm();
            }}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-bold shadow-md shadow-cyan-500/20 flex items-center gap-2 transition-all cursor-pointer shrink-0"
          >
            <span>Open Sizing Form</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
