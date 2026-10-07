import React from 'react';
import { Menu, Sun, Moon, LogOut, User as UserIcon, Shield } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

export const Navbar = ({ onToggleSidebar }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const getRoleBadge = (role) => {
    switch (role) {
      case 'ADMIN':
        return <span className="bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400 border border-rose-200 dark:border-rose-900/40 px-2 py-0.5 rounded text-[11px] font-semibold">Admin</span>;
      case 'HR_ANALYST':
        return <span className="bg-indigo-100 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-900/40 px-2 py-0.5 rounded text-[11px] font-semibold">HR Analyst</span>;
      default:
        return <span className="bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700 px-2 py-0.5 rounded text-[11px] font-semibold">Viewer</span>;
    }
  };

  return (
    <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-30 flex items-center justify-between px-6 transition-colors">
      <div className="flex items-center gap-4">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 lg:hidden"
          aria-label="Toggle menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400">
          <span>Enterprise Console</span>
          <span>/</span>
          <span className="text-slate-900 dark:text-slate-200 font-semibold">Differential Privacy Suite</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Dark/Light mode toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* User Info & Role */}
        <div className="flex items-center gap-3 pl-3 border-l border-slate-200 dark:border-slate-800">
          <div className="text-right hidden sm:block">
            <div className="text-sm font-semibold text-slate-900 dark:text-slate-100 leading-tight">
              {user?.full_name || 'Guest User'}
            </div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
              {user?.email}
            </div>
          </div>

          <div className="flex items-center gap-2">
            {user?.role && getRoleBadge(user.role)}
            
            <button
              onClick={logout}
              className="p-2 rounded-lg text-slate-500 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
