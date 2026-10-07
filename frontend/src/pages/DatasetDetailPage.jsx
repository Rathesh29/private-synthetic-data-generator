import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Database, 
  Sparkles, 
  SlidersHorizontal, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  ArrowLeft,
  FileSpreadsheet,
  Layers,
  Fingerprint
} from 'lucide-react';
import apiClient from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { useAuth } from '../context/AuthContext';

export const DatasetDetailPage = () => {
  const { id } = useParams();
  const [dataset, setDataset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { hasRole } = useAuth();

  useEffect(() => {
    const fetchDataset = async () => {
      try {
        const res = await apiClient.get(`/datasets/${id}`);
        setDataset(res.data);
      } catch (err) {
        setError('Failed to fetch dataset details.');
      } finally {
        setLoading(false);
      }
    };
    fetchDataset();
  }, [id]);

  if (loading) {
    return (
      <div className="py-24 text-center">
        <div className="inline-block animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mb-3" />
        <p className="text-sm font-medium text-slate-500">Loading dataset schema & quality analysis...</p>
      </div>
    );
  }

  if (error || !dataset) {
    return (
      <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
        <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-900 dark:text-white mb-2">{error || 'Dataset not found'}</h3>
        <Link to="/datasets" className="text-xs font-semibold text-indigo-600 hover:underline">
          &larr; Back to Datasets Catalog
        </Link>
      </div>
    );
  }

  const quality = dataset.quality_report;

  return (
    <div className="space-y-6">
      {/* Back button & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            to="/datasets"
            className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-500"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
              {dataset.name}
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Source file: <span className="font-mono text-slate-700 dark:text-slate-300">{dataset.original_filename}</span> &bull; Uploaded {new Date(dataset.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {hasRole(['ADMIN', 'HR_ANALYST']) && (
          <div className="flex items-center gap-2">
            <Link
              to={`/preprocess/${dataset.id}`}
              className="px-4 py-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 text-xs font-semibold shadow-sm flex items-center gap-1.5"
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>Configure Preprocessing</span>
            </Link>
            <Link
              to={`/generate?datasetId=${dataset.id}`}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-sm shadow-indigo-600/20 flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Synthesize Records</span>
            </Link>
          </div>
        )}
      </div>

      {/* Quality Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Overall Quality</p>
          <div className="flex items-center gap-2 mt-2">
            <span className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">
              {dataset.quality_score.toFixed(1)}%
            </span>
            <CheckCircle2 className="w-5 h-5 text-emerald-500" />
          </div>
          <p className="text-[11px] text-slate-400 mt-2">Automated completeness check</p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Dimensions</p>
          <div className="text-3xl font-extrabold text-slate-900 dark:text-white mt-2">
            {dataset.row_count.toLocaleString()}
          </div>
          <p className="text-[11px] text-slate-400 mt-2">{dataset.column_count} validated feature columns</p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Missing & Duplicates</p>
          <div className="text-3xl font-extrabold text-slate-900 dark:text-white mt-2">
            {quality ? quality.duplicate_rows_count : 0} <span className="text-xs font-normal text-slate-400">dups</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            {quality ? quality.missing_values_count : 0} missing cells detected
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Direct Identifiers</p>
          <div className="flex items-center gap-2 mt-2">
            <span className="text-3xl font-extrabold text-purple-600 dark:text-purple-400">
              {quality ? quality.detected_identifiers.length : 0}
            </span>
            <Fingerprint className="w-5 h-5 text-purple-500" />
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Auto-flagged for elimination in ML steps
          </p>
        </div>
      </div>

      {/* Schema & Column Breakdown Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="p-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900 dark:text-white text-base">
              Detected Feature Schema & Attributes
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Individual column metadata, detected types, missingness, and safe sample values.
            </p>
          </div>
          <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
            {dataset.columns?.length || 0} columns
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-800/40 text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                <th className="py-3 px-4">Column Name</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Missing</th>
                <th className="py-3 px-4">Uniques</th>
                <th className="py-3 px-4">Distribution / Summary Stats</th>
                <th className="py-3 px-4">Safe Preview</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {dataset.columns?.map((col) => (
                <tr key={col.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/30">
                  <td className="py-3.5 px-4 font-mono font-medium text-slate-900 dark:text-white">
                    <div className="flex items-center gap-2">
                      <span>{col.column_name}</span>
                      {col.is_identifier && (
                        <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300">
                          PII Identifier
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-medium ${
                      col.data_type === 'numerical' 
                        ? 'bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300' 
                        : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                    }`}>
                      {col.data_type}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-600 dark:text-slate-400">
                    {col.missing_count === 0 ? (
                      <span className="text-emerald-600 dark:text-emerald-400 font-medium">None (0)</span>
                    ) : (
                      <span className="text-amber-600 font-medium">{col.missing_count} rows</span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-slate-700 dark:text-slate-300 font-medium">
                    {col.unique_count.toLocaleString()}
                  </td>
                  <td className="py-3.5 px-4 text-slate-500 dark:text-slate-400">
                    {col.data_type === 'numerical' && col.stats ? (
                      <span className="font-mono text-[11px]">
                        min: {col.stats.min} &bull; max: {col.stats.max} &bull; mean: {col.stats.mean}
                      </span>
                    ) : col.stats?.top_categories ? (
                      <span className="text-[11px]">
                        {Object.keys(col.stats.top_categories).slice(0, 3).join(', ')}...
                      </span>
                    ) : (
                      <span>-</span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 font-mono text-[11px] text-slate-600 dark:text-slate-400">
                    {col.is_identifier ? (
                      <span className="text-slate-400 italic font-sans">[Redacted for privacy]</span>
                    ) : (
                      col.sample_values?.slice(0, 3).join(', ')
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
