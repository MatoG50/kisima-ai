import React from 'react';
import type { HydraulicResult } from '../../services/types';
import { Activity } from 'lucide-react';

interface HydraulicResultsProps {
  hydraulic: HydraulicResult;
}

export const HydraulicResults: React.FC<HydraulicResultsProps> = ({ hydraulic }) => {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 flex items-center justify-center">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">
              Hydraulic Head & Pipe Friction Calculation Summary
            </h3>
            <p className="text-xs text-slate-400">
              Hazen-Williams friction loss calculation results based on design flow & pipe velocity.
            </p>
          </div>
        </div>
        <span className="text-xs font-mono-code bg-cyan-950 text-cyan-300 px-3 py-1 rounded-full border border-cyan-800/60 font-semibold">
          TDH = {hydraulic.total_dynamic_head_m} m
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Metric 1 */}
        <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">Static Lift Head</span>
          <span className="text-2xl font-extrabold font-mono-code text-slate-100">
            {hydraulic.static_head_m} <span className="text-xs text-slate-400 font-normal">m</span>
          </span>
          <span className="text-[11px] text-slate-400 block mt-1">Water level depth to outlet elevation</span>
        </div>

        {/* Metric 2 */}
        <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">Riser Pipe Friction</span>
          <span className="text-2xl font-extrabold font-mono-code text-cyan-400">
            +{hydraulic.riser_friction_m} <span className="text-xs text-slate-400 font-normal">m</span>
          </span>
          <span className="text-[11px] text-slate-400 block mt-1">
            {hydraulic.riser_length_m}m riser ({hydraulic.riser_pipe_quantity} x {hydraulic.standard_riser_length_m}m {hydraulic.riser_material})
          </span>
        </div>

        {/* Metric 3 */}
        <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">Delivery Pipeline Friction</span>
          <span className="text-2xl font-extrabold font-mono-code text-blue-400">
            +{hydraulic.delivery_friction_m} <span className="text-xs text-slate-400 font-normal">m</span>
          </span>
          <span className="text-[11px] text-slate-400 block mt-1">
            {hydraulic.delivery_length_m}m pipeline ({hydraulic.delivery_material})
          </span>
        </div>
      </div>

      {/* Detailed Technical Specs Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950/40 p-4 rounded-2xl border border-slate-800/60 text-xs">
        <div>
          <span className="text-slate-400 block">Pipe Diameter</span>
          <span className="font-mono-code font-bold text-slate-200">{hydraulic.pipe_diameter_in} inch</span>
        </div>
        <div>
          <span className="text-slate-400 block">Flow Velocity</span>
          <span className={`font-mono-code font-bold ${hydraulic.velocity_m_s > 2.5 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {hydraulic.velocity_m_s} m/s
          </span>
        </div>
        <div>
          <span className="text-slate-400 block">Standard Riser Specs</span>
          <span className="font-mono-code font-bold text-slate-200">{hydraulic.riser_pipe_quantity} x 3m Pipes</span>
        </div>
        <div>
          <span className="text-slate-400 block">Formula Standard</span>
          <span className="font-mono-code font-bold text-cyan-300">Hazen-Williams C=150</span>
        </div>
      </div>
    </div>
  );
};
