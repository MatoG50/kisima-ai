import React from 'react';
import { Waves, ShieldCheck, Database } from 'lucide-react';

export const AppFooter: React.FC = () => {
  return (
    <footer className="bg-slate-950 border-t border-slate-800/60 mt-auto py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Col */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center text-white">
                <Waves className="w-4 h-4" />
              </div>
              <span className="font-bold text-slate-100">Kisima AI</span>
            </div>
            <p className="text-sm text-slate-400 max-w-sm mb-4">
              AI-assisted hydraulic water pump sizing platform powered by manufacturer specifications and RAG intelligence.
            </p>
            <div className="flex items-center gap-4 text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                Hazen-Williams Hydraulic Engine
              </span>
              <span className="flex items-center gap-1.5">
                <Database className="w-4 h-4 text-cyan-400" />
                PostgreSQL Catalog
              </span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-3">Engine Standard</h4>
            <ul className="space-y-2 text-xs text-slate-400">
              <li>• ISO 9906 Hydraulic Acceptance Test</li>
              <li>• Hazen-Williams C-Factor Pipe Loss</li>
              <li>• Sustainable Borehole Yield Protection</li>
              <li>• Full Load Current (FLC) Evaluation</li>
            </ul>
          </div>

          {/* Supported Families */}
          <div>
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-3">
              Supported Pump Families
            </h4>

            <ul className="space-y-2 text-xs text-slate-400">
              <li>• <strong className="text-slate-300">DSD Series</strong> — Submersible Borehole Pumps</li>
              <li>• <strong className="text-slate-300">DS Series</strong> — Submersible Borehole Pumps</li>
              <li>• <strong className="text-slate-300">DSS Series</strong> — Submersible Borehole Pumps</li>
              <li>• <strong className="text-slate-300">DSP Series</strong> — Submersible Borehole Pumps</li>
            </ul>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-4">
          <p>© {new Date().getFullYear()} Kisima AI Engineering Platform. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <span>REST API v1.0.0</span>
            <span>RAG Vector Index v1.0</span>
            <span>PostgreSQL Database</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
