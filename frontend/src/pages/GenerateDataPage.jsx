import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { 
  Sparkles, 
  ShieldCheck, 
  AlertTriangle, 
  Sliders, 
  HelpCircle, 
  CheckCircle2, 
  FileText,
  TrendingUp,
  Cpu,
  Layers,
  Info
} from 'lucide-react';
import apiClient from '../api/client';

export const GenerateDataPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [datasets, setDatasets] = useState([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState(searchParams.get('datasetId') || '');
  const [jobName, setJobName] = useState('');
  const [method, setMethod] = useState('DP_SGD_NEURAL');
  const [numRecords, setNumRecords] = useState(1000);

  // DP Hyperparameters
  const [noiseMultiplier, setNoiseMultiplier] = useState(1.1);
  const [clippingNorm, setClippingNorm] = useState(1.0);
  const [epochs, setEpochs] = useState(20);
  const [batchSize, setBatchSize] = useState(64);
  const [learningRate, setLearningRate] = useState(0.001);

  // Budget status & live tradeoff estimate
  const [budgetStatus, setBudgetStatus] = useState(null);
  const [tradeoffEstimate, setTradeoffEstimate] = useState(null);

  // Execution state
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [completedJob, setCompletedJob] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dsRes, bRes] = await Promise.all([
          apiClient.get('/datasets'),
          apiClient.get('/privacy/budget')
        ]);
        setDatasets(dsRes.data);
        setBudgetStatus(bRes.data);

        if (!selectedDatasetId && dsRes.data.length > 0) {
          setSelectedDatasetId(dsRes.data[0].id);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchData();
  }, [selectedDatasetId]);

  // Update default job name when dataset changes
  useEffect(() => {
    if (selectedDatasetId && datasets.length > 0) {
      const ds = datasets.find(d => String(d.id) === String(selectedDatasetId));
      if (ds && !jobName) {
        setJobName(`Synthetic ${ds.name} ${method === 'DP_SGD_NEURAL' ? 'DP' : 'Baseline'}`);
      }
    }
  }, [selectedDatasetId, datasets, method]);

  // Recalculate tradeoff estimate when DP sliders change
  useEffect(() => {
    const fetchEstimate = async () => {
      if (method !== 'DP_SGD_NEURAL') {
        setTradeoffEstimate(null);
        return;
      }
      try {
        const res = await apiClient.get('/privacy/estimate', {
          params: {
            noise_multiplier: noiseMultiplier,
            clipping_norm: clippingNorm,
            epochs: epochs,
            batch_size: batchSize,
            dataset_size: 1000
          }
        });
        setTradeoffEstimate(res.data);
      } catch (err) {
        console.error("Estimate fetch error:", err);
      }
    };
    fetchEstimate();
  }, [method, noiseMultiplier, clippingNorm, epochs, batchSize]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedDatasetId) {
      setError('Please select a source dataset.');
      return;
    }

    setRunning(true);
    setProgress(15);
    setError(null);
    setCompletedJob(null);

    const payload = {
      name: jobName || 'Synthetic HR Run',
      dataset_id: parseInt(selectedDatasetId),
      method: method,
      num_records: parseInt(numRecords),
      noise_multiplier: parseFloat(noiseMultiplier),
      clipping_norm: parseFloat(clippingNorm),
      epochs: parseInt(epochs),
      batch_size: parseInt(batchSize),
      learning_rate: parseFloat(learningRate),
      epsilon_target: tradeoffEstimate?.estimated_epsilon || 1.0,
      delta_target: 1e-5
    };

    // Simulated visual step interval
    const interval = setInterval(() => {
      setProgress(p => (p < 80 ? p + 12 : p));
    }, 600);

    try {
      const res = await apiClient.post('/generation/run', payload);
      clearInterval(interval);
      setProgress(100);
      setCompletedJob(res.data);
      // Reload privacy budget
      const bRes = await apiClient.get('/privacy/budget');
      setBudgetStatus(bRes.data);
    } catch (err) {
      clearInterval(interval);
      setError(err.response?.data?.detail || 'Synthetic generation job failed.');
    } finally {
      setRunning(false);
    }
  };

  const isBudgetExceeded = 
    method === 'DP_SGD_NEURAL' && 
    budgetStatus && 
    tradeoffEstimate && 
    tradeoffEstimate.estimated_epsilon > budgetStatus.remaining_epsilon_budget;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
          Generate Private Synthetic HR Data
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Train differentially private deep generative models or baseline synthesizers to produce shareable employee records.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/40 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Progress banner if executing */}
      {running && (
        <div className="p-6 rounded-2xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900/40 space-y-3">
          <div className="flex items-center justify-between text-xs font-bold text-indigo-900 dark:text-indigo-200">
            <span className="flex items-center gap-2">
              <div className="w-3.5 h-3.5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
              <span>Training Model & Generating Synthetic Samples...</span>
            </span>
            <span>{progress}%</span>
          </div>
          <div className="w-full h-2.5 bg-indigo-200 dark:bg-indigo-900/50 rounded-full overflow-hidden">
            <div 
              className="h-full bg-indigo-600 transition-all duration-300 rounded-full"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Completed Success Banner */}
      {completedJob && (
        <div className="p-6 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/40 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5 text-emerald-800 dark:text-emerald-300 font-bold text-base">
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
              <span>Synthetic Generation Succeeded ({completedJob.result_row_count} records)</span>
            </div>
            <div className="flex items-center gap-2">
              <Link
                to={`/reports?jobId=${completedJob.id}`}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm transition-all"
              >
                View Utility & Privacy Report &rarr;
              </Link>
            </div>
          </div>
          <p className="text-xs text-emerald-700 dark:text-emerald-400">
            {completedJob.guarantee_disclaimer}
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white dark:bg-slate-900 p-6 md:p-8 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
        {/* Dataset & Job Name */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Source HR Dataset *
            </label>
            <select
              value={selectedDatasetId}
              onChange={(e) => setSelectedDatasetId(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white"
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.row_count} rows)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Generation Job Name *
            </label>
            <input
              type="text"
              required
              value={jobName}
              onChange={(e) => setJobName(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white"
            />
          </div>
        </div>

        {/* Synthesis Method Selection */}
        <div className="space-y-3">
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">
            Synthesis Method & Privacy Mechanism *
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              onClick={() => setMethod('DP_SGD_NEURAL')}
              className={`
                p-4 rounded-xl border-2 cursor-pointer transition-all
                ${method === 'DP_SGD_NEURAL'
                  ? 'border-indigo-600 bg-indigo-50/40 dark:bg-indigo-950/30'
                  : 'border-slate-200 dark:border-slate-800 hover:border-slate-300'}
              `}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-xs text-slate-900 dark:text-white flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-indigo-600" />
                  <span>DP-SGD Neural (Tabular VAE)</span>
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300">
                  Formal (ε, δ) Guarantee
                </span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                PyTorch Deep Variational Autoencoder trained with per-sample L2 gradient clipping and calibrated Gaussian noise injection. Includes verified Rényi DP accounting.
              </p>
            </div>

            <div
              onClick={() => setMethod('BASELINE_STATISTICAL')}
              className={`
                p-4 rounded-xl border-2 cursor-pointer transition-all
                ${method === 'BASELINE_STATISTICAL'
                  ? 'border-indigo-600 bg-indigo-50/40 dark:bg-indigo-950/30'
                  : 'border-slate-200 dark:border-slate-800 hover:border-slate-300'}
              `}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-xs text-slate-900 dark:text-white flex items-center gap-1.5">
                  <TrendingUp className="w-4 h-4 text-amber-500" />
                  <span>Baseline Copula Synthesizer</span>
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-900 text-amber-700 dark:text-amber-300">
                  No Formal DP
                </span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                Empirical multivariate covariance & marginal sampling. Fast statistical utility benchmark with explicit disclosure that no formal differential privacy bound is provided.
              </p>
            </div>
          </div>
        </div>

        {/* Output Record Count */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
            Synthetic Records to Generate: <strong className="text-indigo-600 dark:text-indigo-400">{numRecords.toLocaleString()}</strong>
          </label>
          <input
            type="range"
            min={100}
            max={5000}
            step={100}
            value={numRecords}
            onChange={(e) => setNumRecords(parseInt(e.target.value))}
            className="w-full accent-indigo-600"
          />
          <div className="flex justify-between text-[11px] text-slate-400 mt-1">
            <span>100 records</span>
            <span>2,500 records</span>
            <span>5,000 records</span>
          </div>
        </div>

        {/* DP Hyperparameter Controls (Visible only for DP-SGD) */}
        {method === 'DP_SGD_NEURAL' && (
          <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-700 pb-3">
              <div className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-indigo-500" />
                <h4 className="font-bold text-xs text-slate-900 dark:text-white">
                  DP-SGD Hyperparameters & Noise Calibration
                </h4>
              </div>
              <span className="text-[11px] text-slate-500">
                Remaining Budget: <strong className="text-emerald-600">ε = {budgetStatus?.remaining_epsilon_budget || 10.0}</strong>
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {/* Noise Multiplier */}
              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  <span>Gaussian Noise Multiplier (σ)</span>
                  <span className="font-mono text-indigo-600 dark:text-indigo-400 font-bold">{noiseMultiplier.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min={0.5}
                  max={3.0}
                  step={0.1}
                  value={noiseMultiplier}
                  onChange={(e) => setNoiseMultiplier(parseFloat(e.target.value))}
                  className="w-full accent-indigo-600"
                />
                <p className="text-[10px] text-slate-400 mt-1">Higher noise = stronger privacy, lower epsilon.</p>
              </div>

              {/* Clipping Norm */}
              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  <span>L2 Gradient Clipping Norm (C)</span>
                  <span className="font-mono text-indigo-600 dark:text-indigo-400 font-bold">{clippingNorm.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min={0.2}
                  max={3.0}
                  step={0.1}
                  value={clippingNorm}
                  onChange={(e) => setClippingNorm(parseFloat(e.target.value))}
                  className="w-full accent-indigo-600"
                />
                <p className="text-[10px] text-slate-400 mt-1">Bounds the maximum sensitivity per sample.</p>
              </div>

              {/* Epochs */}
              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  <span>Training Epochs</span>
                  <span className="font-mono text-indigo-600 dark:text-indigo-400 font-bold">{epochs}</span>
                </div>
                <input
                  type="range"
                  min={5}
                  max={60}
                  step={5}
                  value={epochs}
                  onChange={(e) => setEpochs(parseInt(e.target.value))}
                  className="w-full accent-indigo-600"
                />
              </div>

              {/* Batch Size */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                  Subsampling Batch Size (q = B / N)
                </label>
                <select
                  value={batchSize}
                  onChange={(e) => setBatchSize(parseInt(e.target.value))}
                  className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs"
                >
                  <option value={16}>16 samples (High subsampling amplification)</option>
                  <option value={32}>32 samples</option>
                  <option value={64}>64 samples (Standard)</option>
                  <option value={128}>128 samples</option>
                </select>
              </div>
            </div>

            {/* Live Privacy vs Utility Tradeoff Calculator */}
            {tradeoffEstimate && (
              <div className="p-4 rounded-xl bg-white dark:bg-slate-800 border border-indigo-100 dark:border-indigo-900/50 space-y-2">
                <div className="flex items-center justify-between text-xs font-bold">
                  <span className="text-slate-900 dark:text-white flex items-center gap-1.5">
                    <TrendingUp className="w-4 h-4 text-indigo-500" />
                    <span>Projected Privacy-Utility Tradeoff Preview</span>
                  </span>
                  <span className="text-xs font-mono font-bold text-indigo-600 dark:text-indigo-400">
                    Target ε = {tradeoffEstimate.estimated_epsilon} &bull; δ = 1e-5
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  {tradeoffEstimate.explanation}
                </p>
                <div className="flex items-center gap-4 pt-1 text-[11px]">
                  <span>Projected Fidelity: <strong className="text-emerald-600">{tradeoffEstimate.projected_utility_score}%</strong></span>
                  <span>Empirical Disclosure Risk: <strong className="text-indigo-600">{tradeoffEstimate.privacy_risk_level}</strong></span>
                </div>
              </div>
            )}

            {isBudgetExceeded && (
              <div className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/40 text-xs text-rose-700 dark:text-rose-300">
                Warning: Requested parameters require ε={tradeoffEstimate.estimated_epsilon}, which exceeds the remaining budget of ε={budgetStatus.remaining_epsilon_budget}. Adjust noise or epochs before launching.
              </div>
            )}
          </div>
        )}

        <button
          type="submit"
          disabled={running || isBudgetExceeded}
          className="w-full py-3.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-md shadow-indigo-600/20 transition-all flex items-center justify-center gap-2"
        >
          {running ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Synthesizing Records in Progress...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Launch Synthetic Generation Job</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};
