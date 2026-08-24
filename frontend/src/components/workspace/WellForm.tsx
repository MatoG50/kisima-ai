import React from 'react';
import { FormField } from './FormField';
import { Info, Droplets } from 'lucide-react';
import type { RecommendationRequest } from '../../services/types';

interface WellFormProps {
  formData: Partial<RecommendationRequest>;
  onChange: (updates: Partial<RecommendationRequest>) => void;
  errors: Record<string, string>;
}

export const WellForm: React.FC<WellFormProps> = ({
  formData,
  onChange,
  errors,
}) => {
  const pumpFamily = formData.default_pump_family || 'DSD';

  return (
    <div className="space-y-6">
      {/* Well Mode Banner */}
      <div className="bg-slate-900/80 border border-blue-500/30 rounded-2xl p-4 flex items-start gap-3 shadow-md shadow-blue-950/10">
        <Droplets className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
        <div>
          <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
            Well & Surface Water Submersible Mode
          </h4>
          <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">
            Well sizing evaluates static elevation head and delivery pipe friction without borehole draw-down abstraction rules. Default candidate family is <strong className="text-blue-300 font-mono-code">DSD Series</strong>.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Static Head */}
        <FormField
          id="static_head_m"
          label="Static Head (Vertical Lift)"
          value={formData.static_head_m ?? ''}
          onChange={(val) => onChange({ static_head_m: val === '' ? undefined : parseFloat(val) })}
          placeholder="e.g. 30.0"
          unit="m"
          helpText="Total vertical height difference between the water source level and the discharge outlet."
          error={errors.static_head_m}
          min={0}
        />

        {/* Customer Required Flow */}
        <FormField
          id="customer_requested_flow_m3h"
          label="Customer Required Flow"
          value={formData.customer_requested_flow_m3h ?? ''}
          onChange={(val) => onChange({ customer_requested_flow_m3h: val === '' ? undefined : parseFloat(val) })}
          placeholder="Optional (e.g. 5.0)"
          unit="m³/h"
          isOptional={true}
          helpText="Desired operating flow rate. If left empty, backend selects optimal candidate flow."
          error={errors.customer_requested_flow_m3h}
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
          helpText="Length of delivery pipeline from well outlet to storage tank."
          error={errors.delivery_distance_m}
          min={0}
        />

        {/* Candidate Pump Family */}
        <div className="flex flex-col gap-1.5">
          <label htmlFor="default_pump_family" className="text-xs font-semibold text-slate-200">
            Candidate Pump Family
          </label>
          <select
            id="default_pump_family"
            value={pumpFamily}
            onChange={(e) => onChange({ default_pump_family: e.target.value })}
            className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 focus:border-blue-500 rounded-xl text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/20 font-mono-code"
          >
            <option value="DSD">DSD Series (Default Submersible Well)</option>
            <option value="DS">DS Series (Deep Submersible)</option>
          </select>
          <p className="text-[11px] text-slate-400 flex items-center gap-1 mt-0.5">
            <Info className="w-3.5 h-3.5 text-blue-400 shrink-0" />
            <span>Select the preferred manufacturer pump series family.</span>
          </p>
        </div>
      </div>
    </div>
  );
};
