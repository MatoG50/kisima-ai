import React from 'react';
import { Info, AlertCircle } from 'lucide-react';

interface FormFieldProps {
  id: string;
  label: string;
  value: number | string;
  onChange: (val: string) => void;
  placeholder?: string;
  unit?: string;
  isOptional?: boolean;
  helpText?: string;
  error?: string;
  min?: number;
  step?: string | number;
}

export const FormField: React.FC<FormFieldProps> = ({
  id,
  label,
  value,
  onChange,
  placeholder = '0.0',
  unit,
  isOptional = false,
  helpText,
  error,
  min = 0,
  step = 'any',
}) => {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between">
        <label htmlFor={id} className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
          <span>{label}</span>
          {isOptional && (
            <span className="text-[10px] text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded font-normal uppercase">
              Optional
            </span>
          )}
        </label>
        {unit && (
          <span className="text-[11px] font-mono-code text-cyan-400 bg-cyan-950/40 border border-cyan-800/40 px-2 py-0.5 rounded">
            {unit}
          </span>
        )}
      </div>

      <div className="relative">
        <input
          id={id}
          type="number"
          min={min}
          step={step}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className={`w-full px-3.5 py-2.5 bg-slate-950 border rounded-xl text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 transition-all font-mono-code ${
            error
              ? 'border-rose-500/80 focus:ring-rose-500/30'
              : 'border-slate-800 focus:border-cyan-500 focus:ring-cyan-500/20 hover:border-slate-700'
          }`}
        />
      </div>

      {helpText && !error && (
        <p className="text-[11px] text-slate-400 flex items-start gap-1 mt-0.5 leading-snug">
          <Info className="w-3.5 h-3.5 text-cyan-400/80 shrink-0 mt-0.5" />
          <span>{helpText}</span>
        </p>
      )}

      {error && (
        <p className="text-[11px] text-rose-400 flex items-center gap-1 mt-0.5 font-medium">
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          <span>{error}</span>
        </p>
      )}
    </div>
  );
};
