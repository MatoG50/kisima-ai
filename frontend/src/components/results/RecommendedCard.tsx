import React from 'react';
import type { RecommendedPump, RecommendationResponse } from '../../services/types';
import { AbstractionBadge } from './AbstractionBadge';
import { Award, Sparkles, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';

interface RecommendedCardProps {
  recommendation: RecommendationResponse;
  onExplain: () => void;
  isExplaining?: boolean;
}

export const RecommendedCard: React.FC<RecommendedCardProps> = ({
  recommendation,
  onExplain,
  isExplaining = false,
}) => {
  const pump: RecommendedPump | undefined = recommendation.recommended_pump;

  if (!pump) return null;

  const pumpFamily = pump.pump_name?.split(' ')[0] || 'Submersible';

  return (
    <div className="bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 border-2 border-cyan-500/60 rounded-3xl p-6 sm:p-8 shadow-2xl shadow-cyan-950/40 relative overflow-hidden">
      {/* Background ambient glow */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header Tag */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6 relative z-10">
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-cyan-500 text-slate-950 text-xs font-extrabold uppercase tracking-wider shadow-md shadow-cyan-500/20">
            <Award className="w-4 h-4" />
            PRIMARY RECOMMENDATION
          </span>
          <AbstractionBadge
            status={recommendation.abstraction_status}
            warnings={recommendation.warnings}
          />
        </div>

        {/* Suitability Score */}
        <div className="flex items-center gap-2 bg-slate-950/80 px-3 py-1.5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400">Match Score:</span>
          <span className="font-mono-code font-bold text-emerald-400 text-sm">
            {(pump.suitability_score * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Main Pump Identifier */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center mb-8 relative z-10 border-b border-slate-800/80 pb-6">
        <div className="lg:col-span-2">
          <div className="text-xs uppercase tracking-wider text-cyan-400 font-bold mb-1">
            {pumpFamily} Series Submersible Pump
          </div>
          <h3 className="text-3xl sm:text-4xl font-extrabold text-slate-100 tracking-tight uppercase">
            {pump.pump_name}
          </h3>
          <p className="text-sm text-slate-400 mt-1 font-mono-code">
            Model ID: <span className="text-slate-200">{pump.pump_id}</span> | Motor Power: <span className="text-cyan-300 font-bold">{pump.motor_kw} kW</span> | Phase: <span className="text-slate-200">{pump.phase_option}</span>
          </p>
        </div>

        {/* Big Highlights Callout */}
        <div className="flex items-center justify-start lg:justify-end gap-6 bg-slate-950/60 p-4 rounded-2xl border border-slate-800">
          <div className="text-left">
            <span className="text-xs text-slate-400 block uppercase font-medium">Design Flow</span>
            <span className="text-2xl font-extrabold font-mono-code text-cyan-400">
              {pump.design_flow_m3h} <span className="text-xs text-slate-400 font-normal">m³/h</span>
            </span>
          </div>
          <div className="h-8 w-px bg-slate-800" />
          <div className="text-left">
            <span className="text-xs text-slate-400 block uppercase font-medium">Required TDH</span>
            <span className="text-2xl font-extrabold font-mono-code text-blue-400">
              {pump.required_tdh_m} <span className="text-xs text-slate-400 font-normal">m</span>
            </span>
          </div>
        </div>
      </div>

      {/* Grid Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8 relative z-10">
        <div className="bg-slate-950/70 p-4 rounded-2xl border border-slate-800/80">
          <span className="text-xs text-slate-400 block mb-1">Operating Efficiency</span>
          <span className="text-xl font-bold font-mono-code text-emerald-400">
            {pump.operating_efficiency_percent}%
          </span>
          <span className="text-[10px] text-slate-400 block mt-1">BEP Max: {pump.bep_efficiency_percent}%</span>
        </div>

        <div className="bg-slate-950/70 p-4 rounded-2xl border border-slate-800/80">
          <span className="text-xs text-slate-400 block mb-1">Pump Head @ Duty</span>
          <span className="text-xl font-bold font-mono-code text-cyan-300">
            {pump.pump_head_at_design_flow_m} m
          </span>
          <span className="text-[10px] text-slate-400 block mt-1">H-Q Curve Intersect</span>
        </div>

        <div className="bg-slate-950/70 p-4 rounded-2xl border border-slate-800/80">
          <span className="text-xs text-slate-400 block mb-1">Head Margin</span>
          <span className="text-xl font-bold font-mono-code text-blue-300">
            +{pump.head_margin_m} m
          </span>
          <span className="text-[10px] text-slate-400 block mt-1">Safety Reserve Head</span>
        </div>

        <div className="bg-slate-950/70 p-4 rounded-2xl border border-slate-800/80">
          <span className="text-xs text-slate-400 block mb-1">Discharge Size</span>
          <span className="text-xl font-bold font-mono-code text-slate-200">
            {pump.discharge_size_in}" <span className="text-xs font-normal">NPT/BSP</span>
          </span>
          <span className="text-[10px] text-slate-400 block mt-1">Max Depth: {pump.max_depth_m}m</span>
        </div>
      </div>

      {/* Warnings Banner if any returned */}
      {recommendation.warnings && recommendation.warnings.length > 0 && (
        <div className="mb-6 bg-amber-950/30 border border-amber-500/30 rounded-2xl p-4 text-xs text-amber-300 flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold">Engineering Operational Notes:</span>
            {recommendation.warnings.map((warn, idx) => (
              <p key={idx}>• {warn}</p>
            ))}
          </div>
        </div>
      )}

      {/* Action Button for AI Technical Explanation */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800/80 relative z-10">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Hydraulically verified against manufacturer H-Q curve data</span>
        </div>

        <button
          onClick={onExplain}
          disabled={isExplaining}
          className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-sm shadow-lg shadow-cyan-500/25 flex items-center justify-center gap-2.5 transition-all cursor-pointer disabled:opacity-50"
        >
          <Sparkles className="w-4 h-4 text-cyan-200 animate-pulse" />
          <span>{isExplaining ? 'Generating AI Explanation...' : 'Explain This Recommendation'}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
