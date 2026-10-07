import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Database, 
  UploadCloud, 
  Sparkles, 
  ShieldCheck, 
  Cpu, 
  FileBarChart, 
  History, 
  Sliders, 
  Lock
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Datasets', path: '/datasets', icon: Database },
  { name: 'Upload Data', path: '/upload', icon: UploadCloud, roles: ['ADMIN', 'HR_ANALYST'] },
  { name: 'Generate Data', path: '/generate', icon: Sparkles, roles: ['ADMIN', 'HR_ANALYST'] },
  { name: 'Privacy Budget', path: '/privacy', icon: ShieldCheck },
  { name: 'Model Management', path: '/models', icon: Cpu },
  { name: 'Reports & Exports', path: '/reports', icon: FileBarChart },
  { name: 'Audit Logs', path: '/audit', icon: History, roles: ['ADMIN'] },
];

export const Sidebar = ({ isOpen, onClose }) => {
  const { user } = useAuth();

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      <aside className={`
        fixed top-0 bottom-0 left-0 z-50 w-64 bg-white dark:bg-slate-900 
        border-r border-slate-200 dark:border-slate-800 flex flex-col 
        transition-transform duration-300 ease-in-out
        lg:translate-x-0 ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {/* Brand header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-800 gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-slate-900 dark:text-white text-base leading-tight tracking-tight">
              Privacy<span className="text-indigo-600 dark:text-indigo-400">Synthetics</span>
            </h1>
            <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400">Enterprise HR Engine</p>
          </div>
        </div>

        {/* Navigation list */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-1.5">
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 px-3 pb-2">
            Main Navigation
          </div>
          
          {navItems.map((item) => {
            if (item.roles && (!user || (user.role !== 'ADMIN' && !item.roles.includes(user.role)))) {
              return null;
            }
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                end={item.path === '/'}
                className={({ isActive }) => `
                  flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150
                  ${isActive 
                    ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 shadow-sm border border-indigo-100 dark:border-indigo-900/50' 
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-100'}
                `}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </div>

        {/* Privacy Notice Banner */}
        <div className="p-4 m-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 text-xs">
          <div className="flex items-center gap-1.5 font-semibold text-emerald-600 dark:text-emerald-400 mb-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>DP Engine Active</span>
          </div>
          <p className="text-slate-500 dark:text-slate-400 text-[11px] leading-relaxed">
            Rényi DP-SGD active. Raw employee IDs stripped by default.
          </p>
        </div>
      </aside>
    </>
  );
};
