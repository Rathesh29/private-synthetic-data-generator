import React from 'react';
import { ShieldAlert, ShieldCheck } from 'lucide-react';

export const PrivacyBudgetGauge = ({ 
  maxBudget = 10.0, 
  spent = 0.0, 
  remaining = 10.0, 
  utilizationPct = 0.0,
  delta = 1e-5
}) => {
  const getBarColor = (pct) => {
    if (pct < 50) return 'bg-emerald-500';
    if (pct < 80) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  const isExhausted = remaining <= 0.01;

  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {isExhausted ? (
            <ShieldAlert className="w-5 h-5 text-rose-500" />
          ) : (
            <ShieldCheck className="w-5 h-5 text-indigo-500" />
          )}
          <h3 className="font-bold text-slate-900 dark:text-white text-base">
            Differential Privacy Budget (ε)
          </h3>
        </div>
        <span className="text-xs font-mono font-medium px-2 py-1 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
          δ = {delta}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-4 text-center">
        <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
          <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400">Total Cap</p>
          <p className="text-lg font-bold text-slate-900 dark:text-white mt-0.5">ε = {maxBudget.toFixed(1)}</p>
        </div>
        <div className="p-3 rounded-xl bg-indigo-50/50 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/30">
          <p className="text-[11px] font-medium text-indigo-600 dark:text-indigo-400">Total Spent</p>
          <p className="text-lg font-bold text-indigo-600 dark:text-indigo-400 mt-0.5">ε = {spent.toFixed(2)}</p>
        </div>
        <div className="p-3 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/30 border border-emerald-100 dark:border-emerald-900/30">
          <p className="text-[11px] font-medium text-emerald-600 dark:text-emerald-400">Remaining</p>
          <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">ε = {remaining.toFixed(2)}</p>
        </div>
      </div>

      {/* Progress track */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 font-medium">
          <span>Budget Utilization</span>
          <span>{utilizationPct.toFixed(1)}%</span>
        </div>
        <div className="h-2.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
          <div 
            className={`h-full transition-all duration-500 ${getBarColor(utilizationPct)}`}
            style={{ width: `${Math.min(100, utilizationPct)}%` }}
          />
        </div>
      </div>

      {isExhausted && (
        <div className="mt-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/40 text-xs text-rose-700 dark:text-rose-300">
          Privacy budget depleted. Further DP-SGD runs are blocked to guarantee mathematical bounded loss.
        </div>
      )}
    </div>
  );
};
