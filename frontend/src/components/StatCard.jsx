import React from 'react';

export const StatCard = ({ title, value, subtitle, icon: Icon, color = 'indigo', trend }) => {
  const colorMap = {
    indigo: 'bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 border-indigo-100 dark:border-indigo-900/40',
    emerald: 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border-emerald-100 dark:border-emerald-900/40',
    amber: 'bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-900/40',
    purple: 'bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 border-purple-100 dark:border-purple-900/40',
    blue: 'bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 border-blue-100 dark:border-blue-900/40',
  };

  return (
    <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm transition-all hover:shadow-md">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl font-bold text-slate-900 dark:text-white mt-1.5">{value}</h3>
        </div>
        {Icon && (
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center border ${colorMap[color] || colorMap.indigo}`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>
      {subtitle && (
        <div className="mt-3 flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
          {trend && <span className="font-semibold text-emerald-600 dark:text-emerald-400">{trend}</span>}
          <span>{subtitle}</span>
        </div>
      )}
    </div>
  );
};
