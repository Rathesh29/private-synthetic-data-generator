import React from 'react';
import { CheckCircle2, Clock, AlertTriangle, XCircle, ShieldCheck, HelpCircle } from 'lucide-react';

export const StatusBadge = ({ status }) => {
  const s = String(status || '').toUpperCase();

  switch (s) {
    case 'COMPLETED':
    case 'PROCESSED':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Completed</span>
        </span>
      );
    case 'PROCESSING':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 dark:bg-indigo-950/50 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 animate-pulse">
          <Clock className="w-3.5 h-3.5 animate-spin" />
          <span>Processing</span>
        </span>
      );
    case 'PENDING':
    case 'UPLOADED':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>{s === 'UPLOADED' ? 'Uploaded' : 'Pending'}</span>
        </span>
      );
    case 'FAILED':
    case 'ERROR':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300 border border-rose-200 dark:border-rose-800">
          <XCircle className="w-3.5 h-3.5" />
          <span>Failed</span>
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
          <HelpCircle className="w-3.5 h-3.5" />
          <span>{status}</span>
        </span>
      );
  }
};

export const GuaranteeBadge = ({ hasFormalDp }) => {
  if (hasFormalDp) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-50 text-purple-700 dark:bg-purple-950/50 dark:text-purple-300 border border-purple-200 dark:border-purple-800" title="Formal Differential Privacy with bounded sensitivity">
        <ShieldCheck className="w-3.5 h-3.5" />
        <span>Formal DP (ε, δ)</span>
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 border border-slate-200 dark:border-slate-700" title="Statistical Baseline with no formal differential privacy guarantee">
      <span>Statistical (No DP)</span>
    </span>
  );
};
