import React, { useEffect, useState } from 'react';
import { Waves, Sparkles, HelpCircle, Bot, Menu, X } from 'lucide-react';
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
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

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

  const handleNavClick = (tab: 'landing' | 'sizing' | 'results' | 'engineering') => {
    setActiveTab(tab);
    setIsMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-40 backdrop-blur-xl bg-slate-950/90 border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-2">
          {/* Logo & Branding */}
          <div
            className="flex items-center gap-2.5 cursor-pointer group shrink-0"
            onClick={() => handleNavClick('landing')}
          >
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-blue-600 to-sky-400 p-0.5 shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform duration-300">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Waves className="w-4 h-4 sm:w-5 sm:h-5 text-cyan-400 animate-pulse-subtle" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-1.5 sm:gap-2">
                <span className="font-bold text-base sm:text-lg text-slate-100 tracking-tight">
                  Kisima <span className="text-cyan-400 font-extrabold">AI</span>
                </span>
                <span className="text-[9px] sm:text-[10px] font-semibold uppercase tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-1.5 sm:px-2 py-0.5 rounded-full hidden sm:inline-block">
                  Engine
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden xl:block leading-none mt-0.5">
                Pump System Sizing
              </p>
            </div>
          </div>

          {/* Desktop Navigation Links (Visible on xl: 1280px and up) */}
          <nav className="hidden xl:flex items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800/80 shrink-0">
            <button
              onClick={() => handleNavClick('landing')}
              className={`px-3 lg:px-3.5 py-1.5 rounded-lg text-xs lg:text-sm font-medium transition-all duration-200 ${
                activeTab === 'landing'
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md shadow-cyan-500/10 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              Overview
            </button>

            <button
              onClick={() => handleNavClick('sizing')}
              className={`px-3 lg:px-3.5 py-1.5 rounded-lg text-xs lg:text-sm font-medium transition-all duration-200 ${
                activeTab === 'sizing'
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md shadow-cyan-500/10 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              Sizing
            </button>

            {hasResults && (
              <button
                onClick={() => handleNavClick('results')}
                className={`px-3 lg:px-3.5 py-1.5 rounded-lg text-xs lg:text-sm font-medium transition-all duration-200 flex items-center gap-1.5 ${
                  activeTab === 'results'
                    ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md shadow-cyan-500/10 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5 text-cyan-300" />
                <span>Recommendations</span>
              </button>
            )}

            <button
              onClick={() => handleNavClick('engineering')}
              className={`px-3 lg:px-3.5 py-1.5 rounded-lg text-xs lg:text-sm font-medium transition-all duration-200 ${
                activeTab === 'engineering'
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md shadow-cyan-500/10 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              About Engine
            </button>
          </nav>

          {/* Right Action Tools */}
          <div className="flex items-center gap-2 lg:gap-3 shrink-0">
            {/* Manufacturer AI Assistant Button (Desktop) */}
            <button
              onClick={onOpenQAModal}
              className="hidden xl:flex items-center gap-1.5 text-xs text-slate-300 bg-slate-900/80 hover:bg-slate-800 hover:text-white px-2.5 py-1.5 rounded-lg border border-slate-700/60 transition-colors"
              title="Manufacturer AI Assistant — Available Now"
            >
              <HelpCircle className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span className="hidden xl:inline">Manufacturer AI Assistant</span>
              <span className="xl:hidden">Datasheet AI</span>
              <span className="text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Live
              </span>
            </button>

            {/* Kisima AI Copilot (Coming Soon) */}
            <button
              onClick={onOpenAssistantModal}
              className="hidden xl:flex items-center gap-1.5 text-xs font-semibold bg-gradient-to-r from-blue-600/20 to-cyan-600/20 hover:from-blue-600/30 hover:to-cyan-600/30 text-cyan-300 border border-cyan-500/30 px-2.5 py-1.5 rounded-lg transition-all shadow-sm shadow-cyan-500/5"
              title="Kisima AI Copilot — Future Feature (Coming Soon)"
            >
              <Bot className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span>Copilot</span>
              <span className="text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                Soon
              </span>
            </button>

            {/* Backend Health Status Indicator */}
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
                {backendStatus === 'online' ? 'Online' : backendStatus === 'offline' ? 'Offline' : 'Checking'}
              </span>
            </div>

            {/* Responsive Menu Toggle Button (Visible below xl: 1280px) */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="xl:hidden p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
              aria-label="Toggle navigation menu"
            >
              {isMobileMenuOpen ? <X className="w-5 h-5 text-cyan-400" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Responsive Navigation Menu Dropdown (Visible below xl: 1280px) */}
      {isMobileMenuOpen && (
        <div className="xl:hidden bg-slate-950 border-b border-slate-800 px-4 py-4 space-y-3 animate-fade-in">
          <div className="space-y-1">
            <button
              onClick={() => handleNavClick('landing')}
              className={`w-full text-left px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                activeTab === 'landing'
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-semibold shadow-md'
                  : 'text-slate-300 hover:bg-slate-900'
              }`}
            >
              Overview
            </button>

            <button
              onClick={() => handleNavClick('sizing')}
              className={`w-full text-left px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                activeTab === 'sizing'
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-semibold shadow-md'
                  : 'text-slate-300 hover:bg-slate-900'
              }`}
            >
              Pump Sizing
            </button>

            {hasResults && (
              <button
                onClick={() => handleNavClick('results')}
                className={`w-full text-left px-3 py-2.5 rounded-xl text-sm font-medium transition-all flex items-center justify-between ${
                  activeTab === 'results'
                    ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-semibold shadow-md'
                    : 'text-slate-300 hover:bg-slate-900'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-cyan-300" />
                  <span>Recommendations</span>
                </div>
                <span className="text-[10px] bg-cyan-400/20 text-cyan-300 px-2 py-0.5 rounded-full font-bold">
                  Ready
                </span>
              </button>
            )}

            <button
              onClick={() => handleNavClick('engineering')}
              className={`w-full text-left px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                activeTab === 'engineering'
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-semibold shadow-md'
                  : 'text-slate-300 hover:bg-slate-900'
              }`}
            >
              About Engine
            </button>
          </div>

          <div className="pt-3 border-t border-slate-900 space-y-2">
            <button
              onClick={() => {
                setIsMobileMenuOpen(false);
                onOpenQAModal();
              }}
              className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs text-slate-200 bg-slate-900 border border-slate-800"
            >
              <div className="flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-cyan-400" />
                <span>Manufacturer AI Assistant</span>
              </div>
              <span className="text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Live
              </span>
            </button>

            <button
              onClick={() => {
                setIsMobileMenuOpen(false);
                onOpenAssistantModal();
              }}
              className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs text-cyan-300 bg-slate-900 border border-cyan-500/30"
            >
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-cyan-400" />
                <span>Kisima AI Copilot</span>
              </div>
              <span className="text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                Soon
              </span>
            </button>
          </div>
        </div>
      )}
    </header>
  );
};
