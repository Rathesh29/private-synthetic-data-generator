import React, { useEffect, useState } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  HelpCircle, 
  Sliders, 
  BookOpen, 
  CheckCircle2, 
  History,
  TrendingUp,
  Lock
} from 'lucide-react';
import apiClient from '../api/client';
import { PrivacyBudgetGauge } from '../components/PrivacyBudgetGauge';
import { DataTable } from '../components/DataTable';

export const PrivacyBudgetPage = () => {
  const [budget, setBudget] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [bRes, hRes] = await Promise.all([
          apiClient.get('/privacy/budget'),
          apiClient.get('/privacy/history')
        ]);
        setBudget(bRes.data);
        setHistory(hRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const columns = [
    {
      header: 'Accounting Record ID',
      accessor: 'id',
      render: (row) => <span className="font-mono text-xs font-bold">#DP-{row.id}</span>
    },
    {
      header: 'Mechanism & Method',
      accessor: 'accountant_method',
      render: (row) => (
        <div>
          <span className="font-semibold text-slate-800 dark:text-slate-200 text-xs">
            {row.accountant_method}
          </span>
          <div className="text-[10px] text-slate-400 font-mono">
            σ={row.noise_multiplier} &bull; C={row.clipping_norm} &bull; {row.steps_computed} steps
          </div>
        </div>
      )
    },
    {
      header: 'Epsilon Spent (ε)',
      accessor: 'epsilon_spent',
      render: (row) => (
        <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400 text-xs">
          ε = {row.epsilon_spent.toFixed(4)}
        </span>
      )
    },
    {
      header: 'Cumulative Spent',
      accessor: 'cumulative_epsilon',
      render: (row) => (
        <span className="font-mono text-slate-700 dark:text-slate-300 text-xs">
          ε = {row.cumulative_epsilon.toFixed(4)}
        </span>
      )
    },
    {
      header: 'Target Delta (δ)',
      accessor: 'delta_spent',
      render: (row) => <span className="font-mono text-xs text-slate-500">{row.delta_spent}</span>
    },
    {
      header: 'Timestamp',
      accessor: 'created_at',
      render: (row) => (
        <span className="text-[11px] text-slate-400">
          {new Date(row.created_at).toLocaleString()}
        </span>
      )
    }
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
          Differential Privacy Budget Management
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Strict mathematical tracking of privacy loss parameter (ε, δ) using Rényi Differential Privacy composition.
        </p>
      </div>

      {/* Main Budget Gauge Card */}
      <PrivacyBudgetGauge
        maxBudget={budget?.max_epsilon_budget || 10.0}
        spent={budget?.total_epsilon_spent || 0.0}
        remaining={budget?.remaining_epsilon_budget || 10.0}
        utilizationPct={budget?.budget_utilization_pct || 0.0}
        delta={budget?.delta_reference || 1e-5}
      />

      {/* Mathematical Principles & Educational Card */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
          <div className="flex items-center gap-2 font-bold text-slate-900 dark:text-white text-sm">
            <Lock className="w-4 h-4 text-indigo-500" />
            <span>Understanding Differential Privacy (ε, δ)</span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            A randomized algorithm <em>M</em> satisfies <strong>(ε, δ)-Differential Privacy</strong> if for any two neighboring datasets <em>D</em> and <em>D'</em> differing by a single employee record:
          </p>
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 font-mono text-xs text-indigo-700 dark:text-indigo-300 text-center border border-slate-100 dark:border-slate-700">
            Pr[M(D) ∈ S] ≤ e^ε · Pr[M(D') ∈ S] + δ
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
            Smaller <strong>ε</strong> guarantees stronger privacy by making it nearly impossible for an adversary to detect whether any specific individual participated in the dataset.
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
          <div className="flex items-center gap-2 font-bold text-slate-900 dark:text-white text-sm">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            <span>DP-SGD Mathematical Assumptions</span>
          </div>
          <ul className="text-xs text-slate-500 dark:text-slate-400 space-y-2 leading-relaxed">
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              <span><strong>Per-Sample L2 Gradient Clipping:</strong> Each sample gradient is bounded by norm <em>C</em> to strictly limit sensitivity.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              <span><strong>Subsampled Gaussian Mechanism:</strong> Calibrated spherical noise <em>N(0, σ² C² I)</em> is injected at every optimization iteration.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              <span><strong>Analytical Accounting:</strong> RDP composition aggregates privacy loss across all training epochs tightly.</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Accounting History Ledger */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900 dark:text-white text-base">
              Privacy Expenditure Audit Ledger
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Immutable log of all model training runs and deducted differential privacy budget.
            </p>
          </div>
        </div>

        <DataTable
          columns={columns}
          data={history}
          loading={loading}
          emptyMessage="No differential privacy training runs recorded yet."
        />
      </div>
    </div>
  );
};
