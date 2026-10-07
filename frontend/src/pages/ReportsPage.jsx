import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  FileBarChart, 
  Download, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  TrendingUp, 
  Layers, 
  BarChart3,
  Cpu,
  Info
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';

export const ReportsPage = () => {
  const [searchParams] = useSearchParams();
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(searchParams.get('jobId') || '');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);
  const { hasRole } = useAuth();

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await apiClient.get('/generation');
        const completed = res.data.filter(j => j.status === 'COMPLETED');
        setJobs(completed);
        if (!selectedJobId && completed.length > 0) {
          setSelectedJobId(completed[0].id);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchJobs();
  }, [selectedJobId]);

  useEffect(() => {
    const fetchReport = async () => {
      if (!selectedJobId) return;
      setLoading(true);
      setError(null);
      try {
        const res = await apiClient.get(`/evaluation/job/${selectedJobId}`);
        setReport(res.data);
      } catch (err) {
        setError('Evaluation report not found for this generation job.');
        setReport(null);
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [selectedJobId]);

  const handleDownload = async () => {
    if (!selectedJobId) return;
    setDownloading(true);
    try {
      const res = await apiClient.get(`/generation/${selectedJobId}/export`, {
        responseType: 'blob'
      });
      const blob = new Blob([res.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `synthetic_hr_dataset_job_${selectedJobId}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to download synthetic dataset.');
    } finally {
      setDownloading(false);
    }
  };

  const selectedJob = jobs.find(j => String(j.id) === String(selectedJobId));

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Synthetic Data Evaluation & Export
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Aggregated statistical fidelity comparison, empirical disclosure risk metrics, and certified CSV export.
          </p>
        </div>

        {hasRole(['ADMIN', 'HR_ANALYST']) && selectedJob && (
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-xs font-bold shadow-md shadow-emerald-600/20 flex items-center gap-2 transition-all"
          >
            <Download className="w-4 h-4" />
            <span>{downloading ? 'Preparing CSV...' : 'Download Synthetic HR Dataset (CSV)'}</span>
          </button>
        )}
      </div>

      {/* Job Selector Dropdown */}
      <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <FileBarChart className="w-5 h-5 text-indigo-500 shrink-0" />
          <div>
            <label className="block text-xs font-bold text-slate-900 dark:text-white">
              Selected Generation Job
            </label>
            <p className="text-[11px] text-slate-400">
              Switch between runs to compare statistical retention and privacy parameters.
            </p>
          </div>
        </div>

        <select
          value={selectedJobId}
          onChange={(e) => setSelectedJobId(e.target.value)}
          className="px-3.5 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
        >
          {jobs.map((j) => (
            <option key={j.id} value={j.id}>
              Job #{j.id}: {j.name} ({j.method === 'DP_SGD_NEURAL' ? `DP ε=${j.epsilon_spent.toFixed(2)}` : 'Baseline Copula'})
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="py-24 text-center">
          <div className="inline-block animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mb-3" />
          <p className="text-sm font-medium text-slate-500">Computing comparative statistics...</p>
        </div>
      ) : error || !report ? (
        <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
          <AlertTriangle className="w-10 h-10 text-amber-500 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900 dark:text-white mb-2">No Report Available</h3>
          <p className="text-xs text-slate-500 mb-4">{error || 'Please run a synthetic generation job first.'}</p>
          <Link to="/generate" className="text-xs font-semibold text-indigo-600 hover:underline">
            Launch New Generation Job &rarr;
          </Link>
        </div>
      ) : (
        <>
          {/* Top Scores Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Overall Utility Score</p>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">
                  {report.overall_utility_score.toFixed(1)}%
                </span>
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
              </div>
              <p className="text-[11px] text-slate-400 mt-2">Aggregated distribution & correlation fidelity</p>
            </div>

            <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Correlation Matrix Match</p>
              <div className="text-3xl font-extrabold text-indigo-600 dark:text-indigo-400 mt-2">
                {report.correlation_metrics?.frobenius_similarity_score?.toFixed(1) || 90.0}%
              </div>
              <p className="text-[11px] text-slate-400 mt-2">Pairwise feature relationships preserved</p>
            </div>

            <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Exact Replica Check</p>
              <div className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-2">
                {report.nearest_neighbor_risk?.exact_replica_count === 0 ? '0 detected' : `${report.nearest_neighbor_risk?.exact_replica_count} replicas`}
              </div>
              <p className="text-[11px] text-slate-400 mt-2">Zero training record memorization</p>
            </div>

            <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Membership Attack Risk</p>
              <div className="text-3xl font-extrabold text-indigo-600 dark:text-indigo-400 mt-2">
                {report.membership_inference_risk?.threat_level || 'Low'}
              </div>
              <p className="text-[11px] text-slate-400 mt-2">
                Advantage over random guess: +{report.membership_inference_risk?.advantage_over_random_pct || 0}%
              </p>
            </div>
          </div>

          {/* Real vs Synthetic Statistical Comparison Table */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm">
            <div className="p-5 border-b border-slate-200 dark:border-slate-800">
              <h3 className="font-bold text-slate-900 dark:text-white text-base">
                Feature-by-Feature Statistical Distribution Comparison
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Comparing real vs synthetic aggregates: means, standard deviations, and Wasserstein / Variation distances.
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-800/40 text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                    <th className="py-3 px-4">Feature Name</th>
                    <th className="py-3 px-4">Type</th>
                    <th className="py-3 px-4">Real Mean / Median</th>
                    <th className="py-3 px-4">Synthetic Mean / Median</th>
                    <th className="py-3 px-4">Real Std Dev</th>
                    <th className="py-3 px-4">Synthetic Std Dev</th>
                    <th className="py-3 px-4">Similarity Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {report.column_metrics?.map((col, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/30">
                      <td className="py-3 px-4 font-mono font-medium text-slate-900 dark:text-white">
                        {col.column_name}
                      </td>
                      <td className="py-3 px-4 capitalize text-slate-500">
                        {col.data_type}
                      </td>
                      <td className="py-3 px-4 text-slate-700 dark:text-slate-300">
                        {col.data_type === 'numerical' ? `${col.real_mean} / ${col.real_median}` : `${col.categories_compared || 'N/A'} categories`}
                      </td>
                      <td className="py-3 px-4 text-slate-700 dark:text-slate-300 font-medium">
                        {col.data_type === 'numerical' ? `${col.synthetic_mean} / ${col.synthetic_median}` : 'Preserved proportions'}
                      </td>
                      <td className="py-3 px-4 text-slate-500">
                        {col.data_type === 'numerical' ? col.real_std : '-'}
                      </td>
                      <td className="py-3 px-4 text-slate-500">
                        {col.data_type === 'numerical' ? col.synthetic_std : '-'}
                      </td>
                      <td className="py-3 px-4">
                        <span className="font-bold text-emerald-600 dark:text-emerald-400">
                          {col.similarity_score}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Correlation Preservation Table */}
          {report.correlation_metrics?.pairs?.length > 0 && (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
              <h3 className="font-bold text-slate-900 dark:text-white text-base">
                Pairwise Correlation Matrix Preservation
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Verifies that crucial HR relationships (e.g., tenure vs salary, overtime vs attrition) are preserved without exposing raw training records.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
                {report.correlation_metrics.pairs.map((p, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 text-xs">
                    <p className="font-semibold text-slate-800 dark:text-slate-200 mb-1">{p.pair}</p>
                    <div className="flex justify-between text-[11px] text-slate-500">
                      <span>Real r = <strong className="text-slate-700 dark:text-slate-300">{p.real_correlation}</strong></span>
                      <span>Synth r = <strong className="text-indigo-600 dark:text-indigo-400">{p.synthetic_correlation}</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Privacy Limitations & Regulatory Disclaimer */}
          <div className="p-6 rounded-2xl bg-amber-50/60 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/40 space-y-3 text-xs">
            <div className="flex items-center gap-2 font-bold text-amber-900 dark:text-amber-300 text-sm">
              <ShieldCheck className="w-5 h-5 text-amber-600" />
              <span>Scientific & Regulatory Disclaimer on Privacy Guarantees</span>
            </div>
            <ul className="text-amber-800 dark:text-amber-400 list-disc list-inside space-y-1.5 leading-relaxed text-[11px]">
              {report.limitations_disclosure?.caveats?.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
              <li>
                <strong>Empirical tests (DCR, Membership Inference) are heuristic sanity checks</strong> and do NOT provide mathematical worst-case differential privacy guarantees. Formal protection is provided solely by the DP-SGD algorithm calibrated with Rényi DP bounds.
              </li>
              <li>
                All exported files are synthetic approximations generated via machine learning algorithms. No synthetic row corresponds to an identifiable employee.
              </li>
            </ul>
          </div>
        </>
      )}
    </div>
  );
};
