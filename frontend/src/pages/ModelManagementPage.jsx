import React, { useEffect, useState } from 'react';
import { 
  Cpu, 
  ShieldCheck, 
  TrendingDown, 
  Eye, 
  Activity, 
  Layers,
  Sparkles
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import apiClient from '../api/client';
import { DataTable } from '../components/DataTable';
import { GuaranteeBadge } from '../components/StatusBadge';
import { Modal } from '../components/Modal';

export const ModelManagementPage = () => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedModel, setSelectedModel] = useState(null);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const res = await apiClient.get('/models');
        setModels(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchModels();
  }, []);

  const columns = [
    {
      header: 'Model Name & Version',
      accessor: 'name',
      render: (row) => (
        <div>
          <span className="font-semibold text-slate-900 dark:text-white text-xs">
            {row.name}
          </span>
          <div className="font-mono text-[10px] text-slate-400">
            {row.version_tag} &bull; {row.architecture}
          </div>
        </div>
      )
    },
    {
      header: 'Formal DP Guarantee',
      accessor: 'has_formal_dp',
      render: (row) => <GuaranteeBadge hasFormalDp={row.has_formal_dp} />
    },
    {
      header: 'Privacy Loss (ε)',
      accessor: 'epsilon_spent',
      render: (row) => (
        <span className="font-mono text-xs font-bold text-indigo-600 dark:text-indigo-400">
          {row.has_formal_dp ? `ε = ${row.epsilon_spent.toFixed(2)}` : 'N/A'}
        </span>
      )
    },
    {
      header: 'Utility Score',
      accessor: 'utility_score',
      render: (row) => (
        <span className="font-bold text-xs text-emerald-600 dark:text-emerald-400">
          {row.utility_score ? `${row.utility_score.toFixed(1)}%` : 'Evaluated'}
        </span>
      )
    },
    {
      header: 'Training Config',
      accessor: 'training_config',
      render: (row) => (
        <span className="font-mono text-[11px] text-slate-500">
          {row.training_config?.epochs ? `${row.training_config.epochs} epochs, lr=${row.training_config.learning_rate}` : 'Direct Fitting'}
        </span>
      )
    },
    {
      header: 'Created',
      accessor: 'created_at',
      render: (row) => (
        <span className="text-[11px] text-slate-400">
          {new Date(row.created_at).toLocaleDateString()}
        </span>
      )
    },
    {
      header: 'Details',
      accessor: 'actions',
      render: (row) => (
        <button
          onClick={() => setSelectedModel(row)}
          className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300"
          title="Inspect Loss Curves & Architecture"
        >
          <Eye className="w-3.5 h-3.5" />
        </button>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
          Model Management & Version Registry
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Catalog of trained synthetic generators, DP-SGD checkpoint metadata, and utility evaluation scores.
        </p>
      </div>

      <DataTable
        columns={columns}
        data={models}
        searchKey="name"
        searchPlaceholder="Filter models..."
        loading={loading}
        emptyMessage="No model versions registered yet. Run a generation job to create a model version."
      />

      {/* Model Detail Modal */}
      <Modal
        isOpen={!!selectedModel}
        onClose={() => setSelectedModel(null)}
        title={selectedModel?.name || 'Model Inspection'}
        maxWidth="max-w-3xl"
      >
        {selectedModel && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40">
                <p className="text-[11px] text-slate-400">Architecture</p>
                <p className="text-xs font-bold text-slate-900 dark:text-white mt-1">
                  {selectedModel.architecture}
                </p>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40">
                <p className="text-[11px] text-slate-400">Privacy (ε)</p>
                <p className="text-xs font-bold text-indigo-600 dark:text-indigo-400 mt-1">
                  {selectedModel.has_formal_dp ? `ε = ${selectedModel.epsilon_spent.toFixed(2)}` : 'Non-DP Baseline'}
                </p>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40">
                <p className="text-[11px] text-slate-400">Utility Score</p>
                <p className="text-xs font-bold text-emerald-600 dark:text-emerald-400 mt-1">
                  {selectedModel.utility_score.toFixed(1)}%
                </p>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40">
                <p className="text-[11px] text-slate-400">Epochs</p>
                <p className="text-xs font-bold text-slate-900 dark:text-white mt-1">
                  {selectedModel.training_config?.epochs || 'N/A'}
                </p>
              </div>
            </div>

            {/* Training Loss History Chart */}
            {selectedModel.training_loss_history?.length > 0 ? (
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                  <Activity className="w-4 h-4 text-indigo-500" />
                  <span>DP-SGD Training Loss & Epsilon Progression</span>
                </h4>
                <div className="h-60 bg-slate-50 dark:bg-slate-800/40 p-4 rounded-2xl border border-slate-100 dark:border-slate-800">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={selectedModel.training_loss_history}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" opacity={0.5} />
                      <XAxis dataKey="epoch" tick={{ fontSize: 11 }} label={{ value: 'Epoch', position: 'insideBottom', offset: -5 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Line type="monotone" dataKey="loss" stroke="#6366f1" strokeWidth={2} name="VAE Loss" />
                      <Line type="monotone" dataKey="epsilon" stroke="#10b981" strokeWidth={2} name="Cumulative ε" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">
                Baseline statistical models do not require epoch-based SGD optimization.
              </p>
            )}

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 text-xs">
              <span className="font-bold text-slate-900 dark:text-white">Training Configuration:</span>
              <pre className="mt-2 font-mono text-[11px] text-slate-600 dark:text-slate-300 overflow-x-auto">
                {JSON.stringify(selectedModel.training_config, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
