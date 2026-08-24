import React from 'react';
import type { RecommendationResponse } from '../../services/types';

interface EngineeringSummaryProps {
  recommendation: RecommendationResponse;
}

export const EngineeringSummary: React.FC<EngineeringSummaryProps> = ({ recommendation }) => {
  const pump = recommendation.recommended_pump;
  if (!pump) return null;

  const flow = recommendation.design_flow_m3h || pump.design_flow_m3h;
  const tdh = pump.required_tdh_m;
  const headAtDuty = pump.pump_head_at_design_flow_m;
  const efficiency = pump.operating_efficiency_percent;

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 shadow-xl">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-slate-100 mb-1">
          Why this pump?
        </h3>
        <p className="text-xs text-slate-400">
          Engineering selection breakdown explaining how operating conditions map to manufacturer pump curves.
        </p>
      </div>

      {/* Visual Step-by-Step Chain */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 relative mb-6">
        {/* Step 1 */}
        <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-400 text-xs font-mono-code font-bold flex items-center justify-center">
                1
              </span>
              <span className="text-[10px] text-slate-400 font-mono-code uppercase">Design Flow</span>
            </div>
            <h5 className="text-base font-bold text-slate-100 font-mono-code">
              {flow} m³/h
            </h5>
            <p className="text-[11px] text-slate-400 mt-1">
              Determined from sustainable yield protection.
            </p>
          </div>
        </div>

        {/* Step 2 */}
        <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 text-xs font-mono-code font-bold flex items-center justify-center">
                2
              </span>
              <span className="text-[10px] text-slate-400 font-mono-code uppercase">Required TDH</span>
            </div>
            <h5 className="text-base font-bold text-slate-100 font-mono-code">
              {tdh} m
            </h5>
            <p className="text-[11px] text-slate-400 mt-1">
              Sum of static lift & pipe friction losses.
            </p>
          </div>
        </div>

        {/* Step 3 */}
        <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="w-5 h-5 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-mono-code font-bold flex items-center justify-center">
                3
              </span>
              <span className="text-[10px] text-slate-400 font-mono-code uppercase">Curve Duty Point</span>
            </div>
            <h5 className="text-base font-bold text-slate-100 font-mono-code">
              {headAtDuty} m @ {efficiency}% Eff.
            </h5>
            <p className="text-[11px] text-slate-400 mt-1">
              Manufacturer H-Q performance intersection.
            </p>
          </div>
        </div>

        {/* Step 4 */}
        <div className="bg-gradient-to-tr from-cyan-950/40 via-slate-950 to-slate-950 p-4 rounded-2xl border border-cyan-500/40 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-mono-code font-bold flex items-center justify-center">
                4
              </span>
              <span className="text-[10px] text-cyan-400 font-mono-code uppercase font-bold">Selected Pump</span>
            </div>
            <h5 className="text-base font-extrabold text-cyan-300 uppercase">
              {pump.pump_name}
            </h5>
            <p className="text-[11px] text-slate-300 mt-1">
              Optimal suitability score & head reserve (+{pump.head_margin_m}m).
            </p>
          </div>
        </div>
      </div>

      {/* Narrative rationale */}
      <div className="bg-slate-950/40 p-4 rounded-2xl border border-slate-800 text-xs text-slate-300 leading-relaxed">
        <strong className="text-slate-100">Engineering Recommendation Summary: </strong>
        The <span className="text-cyan-300 font-bold">{pump.pump_name}</span> ({pump.motor_kw} kW) was evaluated against candidate models. At the duty point of <span className="font-mono-code text-cyan-300">{flow} m³/h</span> and <span className="font-mono-code text-blue-300">{tdh} m TDH</span>, it delivers an operating head of <span className="font-mono-code text-slate-200">{headAtDuty} m</span> at <span className="font-mono-code text-emerald-400">{efficiency}% efficiency</span>, providing a safe head reserve margin of <span className="font-mono-code text-cyan-300">{pump.head_margin_m} m</span>.
      </div>
    </div>
  );
};
