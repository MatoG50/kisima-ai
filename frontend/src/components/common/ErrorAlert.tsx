import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorAlertProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({
  title = "Recommendation Execution Error",
  message,
  onRetry,
}) => {
  return (
    <div className="bg-slate-900 border border-rose-500/40 rounded-3xl p-6 sm:p-8 shadow-2xl max-w-2xl mx-auto my-8">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 flex items-center justify-center shrink-0">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <h3 className="text-base font-bold text-slate-100 mb-1">
            {title}
          </h3>
          <p className="text-xs text-rose-300 bg-rose-950/40 p-3.5 rounded-xl border border-rose-900/60 font-mono-code leading-relaxed mb-4">
            {message}
          </p>

          <div className="flex items-center justify-between gap-4">
            <span className="text-xs text-slate-400">
              Try adjusting required flow or reviewing depth and head parameters.
            </span>
            {onRetry && (
              <button
                onClick={onRetry}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 flex items-center gap-1.5 transition-colors cursor-pointer shrink-0"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Adjust Parameters</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
