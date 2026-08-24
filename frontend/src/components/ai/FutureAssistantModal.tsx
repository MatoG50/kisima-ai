import React from 'react';
import { Bot, X, ArrowRight, CheckCircle2 } from 'lucide-react';

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
        {/* Glow */}
        <div className="absolute top-0 right-0 w-60 h-60 bg-gradient-to-tr from-cyan-500/10 via-blue-500/10 to-transparent rounded-full blur-3xl pointer-events-none" />

        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-xl hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title */}
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
              <span className="text-[10px] uppercase font-extrabold tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 px-2 py-0.5 rounded-full">
                Preview Roadmap
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Conversational Natural Language Hydraulic Parameter Assistant
            </p>
          </div>
        </div>

        {/* Explanation Banner */}
        <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800 space-y-4 mb-6">
          <div className="text-xs text-slate-300 space-y-2">
            <p className="font-semibold text-slate-100">
              How the upcoming AI Conversational Assistant works:
            </p>
            <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 font-mono-code text-[11px] text-cyan-300 space-y-1.5">
              <p className="text-slate-400">User: "I need a pump for my 80m deep borehole with 12m³/h yield."</p>
              <p className="text-cyan-300">AI: "Got it! Extracting PWL=45m, PSD=60m, Yield=12m³/h..."</p>
            </div>
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-900 text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Converts natural language dialogue into structured engineering parameters.</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />
              <span>Calls the authoritative deterministic backend calculation engine.</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0" />
              <span>Protects against invented engineering numbers.</span>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between gap-3">
          <span className="text-xs text-slate-400">
            Use the current hydraulic workspace form to enter exact parameters today.
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
