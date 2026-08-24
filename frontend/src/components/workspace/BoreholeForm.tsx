import React from 'react';
import { FormField } from './FormField';
import { ShieldCheck, Calculator } from 'lucide-react';
import type { RecommendationRequest } from '../../services/types';

interface BoreholeFormProps {
  formData: Partial<RecommendationRequest>;
  onChange: (updates: Partial<RecommendationRequest>) => void;
  errors: Record<string, string>;
}

export const BoreholeForm: React.FC<BoreholeFormProps> = ({
  formData,
  onChange,
  errors,
}) => {
  const yieldM3h = formData.yield_m3h ?? 10;
  const pwlM = formData.pwl_m ?? 40;
  const psdM = formData.psd_m ?? 60;
  const destElev = formData.destination_elevation_m ?? 0;

  // Real-time live estimate metrics for user feedback
  const estStaticHead = pwlM + destElev;
  const estRiserQty = Math.ceil(psdM / 3.0);
  const sustainableMaxFlow = yieldM3h * 0.75; // 75% yield limit rule visualization

  return (
    <div className="space-y-6">
      {/* Borehole Protection Alert Banner */}
      <div className="bg-slate-900/80 border border-cyan-500/30 rounded-2xl p-4 flex items-start gap-3 shadow-md shadow-cyan-950/10">
        <ShieldCheck className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
        <div>
          <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
            Sustainable Borehole Abstraction Protection Active
          </h4>
          <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">
            The backend automatically safeguards your borehole by limiting design flow to <strong className="text-cyan-300 font-mono-code">75% of tested yield</strong> (or 60% for high-flow boreholes).
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Borehole Yield */}
        <FormField
          id="yield_m3h"
          label="Borehole Tested Yield"
          value={formData.yield_m3h ?? ''}
          onChange={(val) => onChange({ yield_m3h: val === '' ? undefined : parseFloat(val) })}
          placeholder="e.g. 10.0"
          unit="m³/h"
          helpText="Maximum tested continuous water yield from borehole pumping test report."
          error={errors.yield_m3h}
          min={0.1}
        />

        {/* Customer Requested Flow */}
        <FormField
          id="customer_requested_flow_m3h"
          label="Customer Required Flow"
          value={formData.customer_requested_flow_m3h ?? ''}
          onChange={(val) => onChange({ customer_requested_flow_m3h: val === '' ? undefined : parseFloat(val) })}
          placeholder="Optional (Defaults to sustainable yield)"
          unit="m³/h"
          isOptional={true}
          helpText="Specific flow required. If unassigned, backend selects optimal flow based on yield."
          error={errors.customer_requested_flow_m3h}
        />

        {/* PWL */}
        <FormField
          id="pwl_m"
          label="Pumping Water Level (PWL)"
          value={formData.pwl_m ?? ''}
          onChange={(val) => onChange({ pwl_m: val === '' ? undefined : parseFloat(val) })}
          placeholder="e.g. 40.0"
          unit="m"
          helpText="The pumping water level depth below ground used for calculating vertical static lift."
          error={errors.pwl_m}
          min={0}
        />

        {/* PSD */}
        <FormField
          id="psd_m"
          label="Pump Setting Depth (PSD)"
          value={formData.psd_m ?? ''}
          onChange={(val) => onChange({ psd_m: val === '' ? undefined : parseFloat(val) })}
          placeholder="e.g. 60.0"
          unit="m"
          helpText="The pump installation depth below ground. Determines riser pipe length and motor depth rating."
          error={errors.psd_m}
          min={0}
        />

        {/* Delivery Distance */}
        <FormField
          id="delivery_distance_m"
          label="Delivery Pipe Distance"
          value={formData.delivery_distance_m ?? ''}
          onChange={(val) => onChange({ delivery_distance_m: val === '' ? 0 : parseFloat(val) })}
          placeholder="0.0"
          unit="m"
          isOptional={true}
          helpText="Horizontal distance from borehole head to storage tank or discharge point."
          error={errors.delivery_distance_m}
          min={0}
        />

        {/* Destination Elevation */}
        <FormField
          id="destination_elevation_m"
          label="Destination Elevation Above Ground"
          value={formData.destination_elevation_m ?? ''}
          onChange={(val) => onChange({ destination_elevation_m: val === '' ? 0 : parseFloat(val) })}
          placeholder="0.0"
          unit="m"
          isOptional={true}
          helpText="Additional height of tank stand or uphill ground elevation above borehole head."
          error={errors.destination_elevation_m}
          min={0}
        />
      </div>

      {/* Live Engineering Summary Preview */}
      <div className="bg-slate-950/60 border border-slate-800 rounded-2xl p-4">
        <div className="flex items-center gap-2 mb-3">
          <Calculator className="w-4 h-4 text-cyan-400" />
          <h5 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
            Live Engineering Parameter Preview
          </h5>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800/60">
            <span className="text-slate-400 block text-[11px]">Static Lift</span>
            <span className="font-mono-code font-bold text-slate-200 text-sm">{estStaticHead.toFixed(1)} m</span>
          </div>
          <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800/60">
            <span className="text-slate-400 block text-[11px]">Riser Length (PSD)</span>
            <span className="font-mono-code font-bold text-cyan-300 text-sm">{psdM.toFixed(1)} m</span>
          </div>
          <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800/60">
            <span className="text-slate-400 block text-[11px]">Est. 3m Risers</span>
            <span className="font-mono-code font-bold text-slate-200 text-sm">{estRiserQty} pipes</span>
          </div>
          <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800/60">
            <span className="text-slate-400 block text-[11px]">Sustainable Limit</span>
            <span className="font-mono-code font-bold text-emerald-400 text-sm">{sustainableMaxFlow.toFixed(1)} m³/h</span>
          </div>
        </div>
      </div>
    </div>
  );
};
