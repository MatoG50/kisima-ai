import React from 'react';
import { Gauge, Database, Sparkles, ArrowUpRight } from 'lucide-react';

interface ValuePropsSectionProps {
  onStartSizing: () => void;
}

export const ValuePropsSection: React.FC<ValuePropsSectionProps> = ({ onStartSizing }) => {
  return (
    <div className="py-12 border-t border-slate-800/60">
      <div className="max-w-6xl mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-100 mb-3">
            Built for Precision Engineering & Reliability
          </h2>
          <p className="text-slate-400 text-sm max-w-2xl mx-auto">
            Combining deterministic hydraulic physics calculations with AI retrieval over verified manufacturer datasheets.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 hover:border-cyan-500/40 transition-all duration-300 group glow-card">
            <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Gauge className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-semibold text-slate-100 mb-2">
              Engineering-Based Sizing
            </h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Calculates total dynamic head (TDH), Hazen-Williams friction loss, and pipe velocity. Protects boreholes by enforcing sustainable yield abstraction limits.
            </p>
          </div>

          {/* Card 2 */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 hover:border-blue-500/40 transition-all duration-300 group glow-card">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Database className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-semibold text-slate-100 mb-2">
              Manufacturer-Backed Catalog
            </h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Evaluates candidate pumps against verified H-Q performance curves stored in PostgreSQL. Recommends the optimal pump plus viable alternatives.
            </p>
          </div>

          {/* Card 3 */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 hover:border-indigo-500/40 transition-all duration-300 group glow-card">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-semibold text-slate-100 mb-2">
              AI Technical Explanations
            </h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Retrieves authentic PDF datasheet snippets using RAG to generate clear, customer-ready explanations without altering hydraulic physics results.
            </p>
          </div>
        </div>

        {/* CTA banner */}
        <div className="mt-12 bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 border border-slate-800 rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <h4 className="text-xl font-bold text-slate-100 mb-1">Ready to size a pump?</h4>
            <p className="text-sm text-slate-400">Select Borehole or Well installation to calculate hydraulic requirements.</p>
          </div>
          <button
            onClick={onStartSizing}
            className="shrink-0 px-6 py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-sm shadow-md shadow-cyan-500/20 flex items-center gap-2 transition-all cursor-pointer"
          >
            <span>Launch Sizing Workspace</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
