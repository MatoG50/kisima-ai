import React from 'react';
import type { RecommendedPump } from '../../services/types';

interface AlternativeCardProps {
  pump: RecommendedPump;
  index: number;
}

export const AlternativeCard: React.FC<AlternativeCardProps> = ({ pump, index }) => {
  const formattedScore = (pump.suitability_score > 1 ? pump.suitability_score : pump.suitability_score * 100).toFixed(0);
  const formattedOperatingEta = (pump.operating_efficiency_percent > 1 ? pump.operating_efficiency_percent : pump.operating_efficiency_percent * 100).toFixed(1);

  return (
    <div className="bg-slate-900/60 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 transition-all duration-300">
      <div className="flex items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded-lg bg-slate-800 text-slate-300 text-xs font-mono-code font-bold flex items-center justify-center border border-slate-700">
            #{index + 2}
          </span>
          <span className="text-xs uppercase font-bold tracking-wider text-slate-400">
            ALTERNATIVE CANDIDATE
          </span>
        </div>
        <span className="text-xs font-mono-code text-slate-400 bg-slate-950 px-2.5 py-0.5 rounded-full border border-slate-800">
          Match Score: {formattedScore}%
        </span>
      </div>

      <div className="mb-4">
        <h4 className="text-xl font-bold text-slate-100 uppercase">
          {pump.pump_name}
        </h4>
        <p className="text-xs text-slate-400 font-mono-code mt-0.5">
          {pump.motor_kw} kW | {pump.phase_option} | {pump.discharge_size_in}" Outlet
        </p>
      </div>

      <div className="grid grid-cols-3 gap-2 bg-slate-950/80 p-3 rounded-xl border border-slate-800 text-xs mb-3">
        <div>
          <span className="text-slate-400 block text-[10px]">Duty Flow</span>
          <span className="font-mono-code font-bold text-cyan-300">{pump.design_flow_m3h} m³/h</span>
        </div>
        <div>
          <span className="text-slate-400 block text-[10px]">Head @ Duty</span>
          <span className="font-mono-code font-bold text-blue-300">{pump.pump_head_at_design_flow_m} m</span>
        </div>
        <div>
          <span className="text-slate-400 block text-[10px]">Efficiency</span>
          <span className="font-mono-code font-bold text-emerald-400">{formattedOperatingEta}%</span>
        </div>
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-400">
        <span>Head Margin: +{pump.head_margin_m} m</span>
        <span>Max Depth: {pump.max_depth_m} m</span>
      </div>
    </div>
  );
};
