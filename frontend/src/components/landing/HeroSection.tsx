import React from 'react';
import { ArrowRight, Sparkles, Compass, CheckCircle2 } from 'lucide-react';

interface HeroSectionProps {
  onStartSizing: () => void;
  onLearnMore: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onStartSizing, onLearnMore }) => {
  return (
    <div className="relative overflow-hidden pt-12 pb-16 md:pt-20 md:pb-24">
      {/* Subtle background glow elements */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-cyan-600/15 via-blue-600/10 to-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-5xl mx-auto text-center relative z-10 px-4">
        {/* Top Badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 text-cyan-400 text-xs font-semibold mb-6 shadow-xl shadow-cyan-950/20 backdrop-blur-md">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Precision Hydraulic Calculations + Manufacturer RAG Intelligence</span>
        </div>

        {/* Primary Heading */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-100 tracking-tight leading-[1.15] mb-6">
          Find the right pump for your <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-blue-500 bg-clip-text text-transparent">water system</span>.
        </h1>

        {/* Subtitle */}
        <p className="text-lg sm:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed mb-10 font-normal">
          Hydraulic sizing powered by engineering calculations, pump performance curves, and manufacturer data.
        </p>

        {/* Primary Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <button
            onClick={onStartSizing}
            className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-600 to-blue-700 hover:from-cyan-400 hover:to-blue-600 text-white font-semibold text-base shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 flex items-center justify-center gap-3 transition-all duration-300 group cursor-pointer"
          >
            <span>Start Pump Sizing</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>

          <button
            onClick={onLearnMore}
            className="w-full sm:w-auto px-7 py-4 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-200 hover:text-white font-semibold text-base border border-slate-700/80 flex items-center justify-center gap-2 transition-all cursor-pointer"
          >
            <Compass className="w-5 h-5 text-cyan-400" />
            <span>How It Works</span>
          </button>
        </div>

        {/* Feature Highlights Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-8 border-t border-slate-800/80">
          <div className="flex items-center justify-center gap-2.5 text-xs font-medium text-slate-300 bg-slate-900/40 p-3 rounded-lg border border-slate-800/50">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Hazen-Williams Friction Loss</span>
          </div>
          <div className="flex items-center justify-center gap-2.5 text-xs font-medium text-slate-300 bg-slate-900/40 p-3 rounded-lg border border-slate-800/50">
            <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />
            <span>Borehole Sustainable Abstraction</span>
          </div>
          <div className="flex items-center justify-center gap-2.5 text-xs font-medium text-slate-300 bg-slate-900/40 p-3 rounded-lg border border-slate-800/50">
            <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0" />
            <span>PostgreSQL Curve Interpolation</span>
          </div>
        </div>
      </div>
    </div>
  );
};
