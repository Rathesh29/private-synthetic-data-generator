import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Database, 
  UploadCloud, 
  Trash2, 
  Eye, 
  Sparkles, 
  SlidersHorizontal,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import apiClient from '../api/client';
import { DataTable } from '../components/DataTable';
import { StatusBadge } from '../components/StatusBadge';
import { useAuth } from '../context/AuthContext';

export const DatasetsPage = () => {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { hasRole } = useAuth();

  const loadDatasets = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/datasets');
      setDatasets(res.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch datasets.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDatasets();
  }, []);

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to permanently delete dataset "${name}" and all associated metadata?`)) {
      return;
    }
    try {
      await apiClient.delete(`/datasets/${id}`);
      setDatasets(prev => prev.filter(d => d.id !== id));
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete dataset.');
    }
  };

  const columns = [
    {
      header: 'Dataset Name',
      accessor: 'name',
      render: (row) => (
        <div>
          <Link 
            to={`/datasets/${row.id}`}
            className="font-semibold text-slate-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400"
          >
            {row.name}
          </Link>
          <div className="text-[11px] text-slate-400 font-mono">{row.original_filename}</div>
        </div>
      )
    },
    {
      header: 'Records & Cols',
      accessor: 'row_count',
      render: (row) => (
        <span>
          <strong className="text-slate-800 dark:text-slate-200">{row.row_count.toLocaleString()}</strong> rows &bull; {row.column_count} cols
        </span>
      )
    },
    {
      header: 'File Size',
      accessor: 'file_size_bytes',
      render: (row) => `${(row.file_size_bytes / 1024).toFixed(1)} KB`
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (row) => <StatusBadge status={row.status} />
    },
    {
      header: 'Quality Score',
      accessor: 'quality_score',
      render: (row) => (
        <div className="flex items-center gap-1.5 font-bold">
          <span className={row.quality_score >= 90 ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'}>
            {row.quality_score.toFixed(1)}%
          </span>
        </div>
      )
    },
    {
      header: 'Actions',
      accessor: 'actions',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Link
            to={`/datasets/${row.id}`}
            className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300"
            title="Inspect Schema & Quality Report"
          >
            <Eye className="w-3.5 h-3.5" />
          </Link>
          {hasRole(['ADMIN', 'HR_ANALYST']) && (
            <>
              <Link
                to={`/preprocess/${row.id}`}
                className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300"
                title="Configure Preprocessing"
              >
                <SlidersHorizontal className="w-3.5 h-3.5" />
              </Link>
              <Link
                to={`/generate?datasetId=${row.id}`}
                className="p-1.5 rounded-lg border border-indigo-200 dark:border-indigo-800 bg-indigo-50 dark:bg-indigo-950/40 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-indigo-600 dark:text-indigo-400"
                title="Generate Synthetic Data"
              >
                <Sparkles className="w-3.5 h-3.5" />
              </Link>
              <button
                onClick={() => handleDelete(row.id, row.name)}
                className="p-1.5 rounded-lg border border-rose-200 dark:border-rose-800/60 hover:bg-rose-50 dark:hover:bg-rose-950/40 text-rose-600 dark:text-rose-400"
                title="Delete Dataset"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </>
          )}
        </div>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Sensitive HR Datasets
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Uploaded employee records catalog. Raw PII is isolated and shielded behind differential privacy pipelines.
          </p>
        </div>
        {hasRole(['ADMIN', 'HR_ANALYST']) && (
          <Link
            to="/upload"
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-sm shadow-indigo-600/20 transition-all flex items-center gap-1.5"
          >
            <UploadCloud className="w-4 h-4" />
            <span>Upload New HR File</span>
          </Link>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/40 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <DataTable
        columns={columns}
        data={datasets}
        searchKey="name"
        searchPlaceholder="Filter datasets by name..."
        loading={loading}
        emptyMessage="No datasets uploaded yet. Upload a CSV or Excel file to get started."
      />
    </div>
  );
};
