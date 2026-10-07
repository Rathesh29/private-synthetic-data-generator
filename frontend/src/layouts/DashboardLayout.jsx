import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { Navbar } from '../components/Navbar';

export const DashboardLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col transition-colors">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="lg:pl-64 flex flex-col flex-1">
        <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
        
        <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full">
          <Outlet />
        </main>

        <footer className="py-4 px-8 border-t border-slate-200 dark:border-slate-800 text-center text-xs text-slate-400 dark:text-slate-500">
          Private Synthetic Data Generator for HR Records &bull; Enterprise Differential Privacy Suite &bull; Mathematical Guarantee Protected
        </footer>
      </div>
    </div>
  );
};
