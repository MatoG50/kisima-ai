import React from 'react';
import { Waves, Droplet, CheckCircle2 } from 'lucide-react';
import type { ApplicationType } from '../../services/types';

interface ApplicationSelectorProps {
  selectedApp: ApplicationType;
  onSelectApp: (app: ApplicationType) => void;
}

export const ApplicationSelector: React.FC<ApplicationSelectorProps> = ({
  selectedApp,
  onSelectApp,
}) => {
  return (
    <div className="mb-8">
      <div className="text-center mb-6">
        <h2 className="text-xl sm:text-2xl font-bold text-slate-100 mb-1">
          Where will the pump be used?
        </h2>
        <p className="text-sm text-slate-400">
          Select your installation application mode to configure the required hydraulic input parameters.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-3xl mx-auto">
        {/* Borehole Card */}
        <div
          onClick={() => onSelectApp('borehole')}
          className={`relative cursor-pointer rounded-2xl p-6 border-2 transition-all duration-300 ${selectedApp === 'borehole'
              ? 'bg-gradient-to-b from-cyan-950/40 via-slate-900 to-slate-900 border-cyan-500 shadow-xl shadow-cyan-500/10 ring-1 ring-cyan-500/50'
              : 'bg-slate-900/50 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/80'
            }`}
        >
          {selectedApp === 'borehole' && (
            <div className="absolute top-4 right-4 text-cyan-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          )}
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${selectedApp === 'borehole'
              ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
              : 'bg-slate-800 text-slate-400 border border-slate-700'
            }`}>
            <Waves className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-100 mb-1">BOREHOLE</h3>
          <p className="text-xs text-slate-400 leading-relaxed mb-3">
            For submersible borehole water supply applications. Accounts for yield, pumping water level, and static water level.
          </p>
          <div className="flex items-center gap-2">
            <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${selectedApp === 'borehole'
                ? 'bg-cyan-500/20 text-cyan-300'
                : 'bg-slate-800 text-slate-400'
              }`}>
              DS Series Focus
            </span>
            <span className="text-xs text-emerald-400 font-medium">Sustainable Abstraction Protection</span>
          </div>
        </div>

        {/* Well Card */}
        <div
          onClick={() => onSelectApp('well')}
          className={`relative cursor-pointer rounded-2xl p-6 border-2 transition-all duration-300 ${selectedApp === 'well'
              ? 'bg-gradient-to-b from-blue-950/40 via-slate-900 to-slate-900 border-blue-500 shadow-xl shadow-blue-500/10 ring-1 ring-blue-500/50'
              : 'bg-slate-900/50 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/80'
            }`}
        >
          {selectedApp === 'well' && (
            <div className="absolute top-4 right-4 text-blue-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          )}
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${selectedApp === 'well'
              ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
              : 'bg-slate-800 text-slate-400 border border-slate-700'
            }`}>
            <Droplet className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-100 mb-1">WELL</h3>
          <p className="text-xs text-slate-400 leading-relaxed mb-3">
            For shallow well or surface water extraction. Calculates required head based on static elevation lift.
          </p>
          <div className="flex items-center gap-2">
            <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${selectedApp === 'well'
                ? 'bg-blue-500/20 text-blue-300'
                : 'bg-slate-800 text-slate-400'
              }`}>
              DSD Series Focus
            </span>
            <span className="text-xs text-slate-400 font-medium">Static Head Direct Lift</span>
          </div>
        </div>
      </div>
    </div>
  );
};
