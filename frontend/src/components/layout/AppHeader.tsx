import React, { useEffect, useState } from 'react';
import { Waves, Sparkles, HelpCircle, Bot } from 'lucide-react';
import { api } from '../../services/api';

interface AppHeaderProps {
  activeTab: 'landing' | 'sizing' | 'results' | 'engineering';
  setActiveTab: (tab: 'landing' | 'sizing' | 'results' | 'engineering') => void;
  hasResults: boolean;
  onOpenQAModal: () => void;
  onOpenAssistantModal: () => void;
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  activeTab,
  setActiveTab,
  hasResults,
  onOpenQAModal,
  onOpenAssistantModal,
}) => {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    let isMounted = true;
    const checkConnection = async () => {
      try {
        const res = await api.checkHealth();
        if (isMounted) {
          setBackendStatus(res.status === 'ok' ? 'online' : 'offline');
        }
      } catch {
        if (isMounted) {
          setBackendStatus('offline');
        }
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="sticky top-0 z-40 backdrop-blur-xl bg-slate-950/80 border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Branding */}
          <div 
            className="flex items-center gap-3 cursor-pointer group"
            onClick={() => setActiveTab('landing')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-blue-600 to-sky-400 p-0.5 shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform duration-300">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Waves className="w-5 h-5 text-cyan-400 animate-pulse-subtle" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-slate-100 tracking-tight">Kisima <span className="text-cyan-400 font-extrabold">AI</span></span>
                <span className="text-[10px] font-semibold uppercase tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2 py-0.5 rounded-full">
                  Hydraulic Engine
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">Solar Pump & Water System Sizing</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1.5 rounded-xl border border-slate-800/60">
            <button
              onClick={() => setActiveTab('landing')}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                activeTab === 'landing'
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md shadow-cyan-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('sizing')}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                activeTab === 'sizing'
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md shadow-cyan-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              Pump Sizing
            </button>
            {hasResults && (
              <button
                onClick={() => setActiveTab('results')}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-1.5 ${
                  activeTab === 'results'
                    ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5 text-cyan-300" />
                Recommendations
              </button>
            )}
            <button
              onClick={() => setActiveTab('engineering')}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                activeTab === 'engineering'
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md shadow-cyan-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              About Engine
            </button>
          </nav>

          {/* Right Action Tools */}
          <div className="flex items-center gap-3">
            {/* Datasheet Q&A Button */}
            <button
              onClick={onOpenQAModal}
              className="hidden lg:flex items-center gap-1.5 text-xs text-slate-300 bg-slate-900/80 hover:bg-slate-800 hover:text-white px-3 py-1.5 rounded-lg border border-slate-700/60 transition-colors"
              title="Search RAG Datasheets"
            >
              <HelpCircle className="w-3.5 h-3.5 text-cyan-400" />
              <span>Datasheet Q&A</span>
            </button>

            {/* AI Assistant Future Button */}
            <button
              onClick={onOpenAssistantModal}
              className="flex items-center gap-1.5 text-xs font-semibold bg-gradient-to-r from-blue-600/20 to-cyan-600/20 hover:from-blue-600/30 hover:to-cyan-600/30 text-cyan-300 border border-cyan-500/30 px-3 py-1.5 rounded-lg transition-all shadow-sm shadow-cyan-500/5"
            >
              <Bot className="w-4 h-4 text-cyan-400" />
              <span className="hidden sm:inline">AI Copilot</span>
            </button>

            {/* Health Status Indicator */}
            <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
              <div 
                className={`w-2.5 h-2.5 rounded-full ${
                  backendStatus === 'online'
                    ? 'bg-emerald-500 shadow-sm shadow-emerald-500/80 animate-pulse'
                    : backendStatus === 'offline'
                    ? 'bg-rose-500'
                    : 'bg-amber-500 animate-ping'
                }`} 
                title={`Backend API ${backendStatus}`}
              />
              <span className="text-[11px] text-slate-400 font-medium hidden xl:inline">
                {backendStatus === 'online' ? 'Engine Online' : backendStatus === 'offline' ? 'Engine Offline' : 'Connecting...'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
