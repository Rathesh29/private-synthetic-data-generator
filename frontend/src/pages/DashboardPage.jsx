import React, { useEffect, useState } from 'react';
import { 
  Database, 
  Sparkles, 
  Cpu, 
  Users, 
  TrendingUp, 
  ShieldCheck, 
  Activity, 
  ArrowUpRight,
  PieChart as PieIcon,
  BarChart3
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  AreaChart, 
  Area 
} from 'recharts';
import apiClient from '../api/client';
import { StatCard } from '../components/StatCard';
import { PrivacyBudgetGauge } from '../components/PrivacyBudgetGauge';
import { StatusBadge } from '../components/StatusBadge';
import { Link } from 'react-router-dom';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#64748b'];

export const DashboardPage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await apiClient.get('/dashboard/stats');
        setStats(res.data);
      } catch (err) {
        console.error("Failed to load dashboard stats:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="py-24 text-center">
        <div className="inline-block animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mb-3" />
        <p className="text-sm font-medium text-slate-500">Loading enterprise analytics dashboard...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Privacy-Preserving HR Dashboard
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time differential privacy budgeting, dataset fidelity analytics, and generative synthesis jobs.
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          <Link
            to="/upload"
            className="px-4 py-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 shadow-sm transition-all"
          >
            Upload Data
          </Link>
          <Link
            to="/generate"
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-sm shadow-indigo-600/20 transition-all flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>New Generation Job</span>
          </Link>
        </div>
      </div>

      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total HR Datasets"
          value={stats?.total_datasets || 0}
          subtitle="Validated & Schema-Detected"
          icon={Database}
          color="indigo"
        />
        <StatCard
          title="Synthetic Jobs"
          value={stats?.total_generation_jobs || 0}
          subtitle={`${stats?.completed_jobs || 0} successfully synthesized`}
          icon={Sparkles}
          color="emerald"
        />
        <StatCard
          title="Model Versions"
          value={stats?.model_versions_count || 0}
          subtitle="DP-Tabular-VAE & Baselines"
          icon={Cpu}
          color="purple"
        />
        <StatCard
          title="Active Users"
          value={stats?.active_users || 0}
          subtitle="Admin & Analyst Roles"
          icon={Users}
          color="blue"
        />
      </div>

      {/* Privacy Budget & Jobs Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <PrivacyBudgetGauge
            maxBudget={stats?.max_epsilon_budget || 10.0}
            spent={stats?.total_epsilon_spent || 0.0}
            remaining={stats?.remaining_epsilon_budget || 10.0}
            utilizationPct={stats?.privacy_budget_utilization_pct || 0.0}
          />
        </div>

        {/* Jobs by Status Card */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-slate-900 dark:text-white text-base mb-1">
              Generation Job Status
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
              Real-time pipeline job queue execution
            </p>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40">
                <span className="text-xs font-medium text-slate-600 dark:text-slate-300">Completed</span>
                <span className="font-bold text-emerald-600 dark:text-emerald-400 text-sm">
                  {stats?.jobs_by_status?.COMPLETED || 0}
                </span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40">
                <span className="text-xs font-medium text-slate-600 dark:text-slate-300">Processing</span>
                <span className="font-bold text-indigo-600 dark:text-indigo-400 text-sm">
                  {stats?.jobs_by_status?.PROCESSING || 0}
                </span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40">
                <span className="text-xs font-medium text-slate-600 dark:text-slate-300">Pending</span>
                <span className="font-bold text-amber-600 dark:text-amber-400 text-sm">
                  {stats?.jobs_by_status?.PENDING || 0}
                </span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40">
                <span className="text-xs font-medium text-slate-600 dark:text-slate-300">Failed</span>
                <span className="font-bold text-rose-600 dark:text-rose-400 text-sm">
                  {stats?.jobs_by_status?.FAILED || 0}
                </span>
              </div>
            </div>
          </div>

          <Link
            to="/privacy"
            className="mt-4 inline-flex items-center justify-center gap-1.5 text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline pt-2 border-t border-slate-100 dark:border-slate-800"
          >
            <span>Manage Privacy Limits</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* HR Benchmark Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Salary Distribution Chart */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-slate-900 dark:text-white text-base">
                Salary Brackets Distribution
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Aggregated workforce compensation tiers
              </p>
            </div>
            <BarChart3 className="w-4 h-4 text-slate-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats?.salary_distribution || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" opacity={0.5} />
                <XAxis dataKey="bracket" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#6366f1" radius={[6, 6, 0, 0]} name="Employees" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Department Distribution Chart */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-slate-900 dark:text-white text-base">
                Department Allocation
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Proportion of employees by business unit
              </p>
            </div>
            <PieIcon className="w-4 h-4 text-slate-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats?.department_distribution || []}
                  dataKey="count"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {(stats?.department_distribution || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Experience Distribution Chart */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <h3 className="font-bold text-slate-900 dark:text-white text-base mb-1">
            Years of Experience Distribution
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
            Tenure curve across employee groups
          </p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats?.experience_distribution || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" opacity={0.5} />
                <XAxis dataKey="range" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Area type="monotone" dataKey="count" stroke="#10b981" fill="#10b981" fillOpacity={0.15} name="Employees" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Performance Distribution Chart */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <h3 className="font-bold text-slate-900 dark:text-white text-base mb-1">
            Performance Ratings Spread
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
            Evaluation tier benchmark (1 to 5)
          </p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats?.performance_distribution || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" opacity={0.5} />
                <XAxis dataKey="rating" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#8b5cf6" radius={[6, 6, 0, 0]} name="Employees" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Activity Trail */}
      <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-indigo-500" />
            <h3 className="font-bold text-slate-900 dark:text-white text-base">
              Recent Enterprise Audit Events
            </h3>
          </div>
          <Link
            to="/audit"
            className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline"
          >
            View Full Audit Trail &rarr;
          </Link>
        </div>

        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {(stats?.recent_activity || []).map((act) => (
            <div key={act.id} className="py-3 flex items-center justify-between text-xs">
              <div className="flex items-center gap-3">
                <span className="font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium text-[11px]">
                  {act.action}
                </span>
                <span className="text-slate-600 dark:text-slate-400">
                  by <strong className="text-slate-800 dark:text-slate-200">{act.user_email}</strong>
                </span>
              </div>
              <span className="text-slate-400 dark:text-slate-500 text-[11px]">
                {new Date(act.created_at).toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
