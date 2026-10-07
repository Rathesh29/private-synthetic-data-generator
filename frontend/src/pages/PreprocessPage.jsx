import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  SlidersHorizontal, 
  CheckCircle2, 
  AlertCircle, 
  ShieldCheck, 
  ArrowLeft,
  Sparkles,
  Info
} from 'lucide-react';
import apiClient from '../api/client';

export const PreprocessPage = () => {
  const { datasetId } = useParams();
  const navigate = useNavigate();
  const [datasets, setDatasets] = useState([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState(datasetId || '');
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Form options
  const [dropIdentifiers, setDropIdentifiers] = useState(true);
  const [numericalImputation, setNumericalImputation] = useState('median');
  const [categoricalImputation, setCategoricalImputation] = useState('mode');
  const [numericalScaling, setNumericalScaling] = useState('minmax');
  const [categoricalEncoding, setCategoricalEncoding] = useState('onehot');
  const [outlierHandling, setOutlierHandling] = useState('clip');

  useEffect(() => {
    const fetchDatasets = async () => {
      try {
        const res = await apiClient.get('/datasets');
        setDatasets(res.data);
        if (!selectedDatasetId && res.data.length > 0) {
          setSelectedDatasetId(res.data[0].id);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchDatasets();
  }, [selectedDatasetId]);

  const handleRun = async (e) => {
    e.preventDefault();
    if (!selectedDatasetId) {
      setError('Please select a dataset to preprocess.');
      return;
    }

    setExecuting(true);
    setError(null);
    setResult(null);

    try {
      const config = {
        drop_identifiers: dropIdentifiers,
        numerical_imputation: numericalImputation,
        categorical_imputation: categoricalImputation,
        numerical_scaling: numericalScaling,
        categorical_encoding: categoricalEncoding,
        outlier_handling: outlierHandling,
        outlier_std_dev_threshold: 3.0
      };

      const res = await apiClient.post(`/preprocessing/run/${selectedDatasetId}`, config);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Preprocessing failed.');
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link
          to="/datasets"
          className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-500"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Configure Data Preprocessing
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Format tabular HR features into normalized representations suitable for DP-SGD generative modeling.
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/40 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleRun} className="bg-white dark:bg-slate-900 p-6 md:p-8 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
        {/* Dataset Selection */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
            Select Target HR Dataset *
          </label>
          <select
            value={selectedDatasetId}
            onChange={(e) => setSelectedDatasetId(e.target.value)}
            className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
          >
            {datasets.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name} ({d.row_count} rows, {d.column_count} columns)
              </option>
            ))}
          </select>
        </div>

        {/* Configuration Options Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-2">
          {/* Identifier Protection */}
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-xs font-bold text-slate-900 dark:text-white">
                  Strip Direct Identifiers
                </label>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Prevents employee IDs and names from entering training weights.
                </p>
              </div>
              <input
                type="checkbox"
                checked={dropIdentifiers}
                onChange={(e) => setDropIdentifiers(e.target.checked)}
                className="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
              />
            </div>
            <div className="flex items-center gap-1.5 text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Recommended for Privacy Compliance</span>
            </div>
          </div>

          {/* Outlier Handling */}
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2">
            <label className="block text-xs font-bold text-slate-900 dark:text-white">
              Outlier Handling
            </label>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Clips extreme compensation or tenure values to bound sensitivity.
            </p>
            <select
              value={outlierHandling}
              onChange={(e) => setOutlierHandling(e.target.value)}
              className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs"
            >
              <option value="clip">Clip to 3 Standard Deviations (Recommended)</option>
              <option value="none">Keep Unaltered</option>
            </select>
          </div>

          {/* Numerical Scaling */}
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2">
            <label className="block text-xs font-bold text-slate-900 dark:text-white">
              Numerical Feature Normalization
            </label>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Scales age, salary, and experience into normalized bounds.
            </p>
            <select
              value={numericalScaling}
              onChange={(e) => setNumericalScaling(e.target.value)}
              className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs"
            >
              <option value="minmax">Min-Max Normalization [0, 1] (Standard for VAE)</option>
              <option value="standard">Z-Score Standardization (Zero Mean, Unit Std)</option>
            </select>
          </div>

          {/* Categorical Encoding */}
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2">
            <label className="block text-xs font-bold text-slate-900 dark:text-white">
              Categorical Encoding Strategy
            </label>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Converts departments, roles, and attrition flags into vectors.
            </p>
            <select
              value={categoricalEncoding}
              onChange={(e) => setCategoricalEncoding(e.target.value)}
              className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs"
            >
              <option value="onehot">One-Hot Encoding with Softmax Projections</option>
              <option value="label">Ordinal Label Encoding</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={executing || !selectedDatasetId}
          className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-md shadow-indigo-600/20 transition-all flex items-center justify-center gap-2"
        >
          {executing ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Fitting Preprocessing Transformers...</span>
            </>
          ) : (
            <>
              <SlidersHorizontal className="w-4 h-4" />
              <span>Execute Preprocessing Pipeline</span>
            </>
          )}
        </button>
      </form>

      {/* Preprocessing Summary Results */}
      {result && (
        <div className="bg-white dark:bg-slate-900 p-6 md:p-8 rounded-2xl border border-emerald-200 dark:border-emerald-900/40 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold text-base">
              <CheckCircle2 className="w-5 h-5" />
              <span>Preprocessing Complete & Transformers Cached</span>
            </div>
            <Link
              to={`/generate?datasetId=${selectedDatasetId}`}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-sm shadow-indigo-600/20 flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Proceed to Generative Synthesis &rarr;</span>
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40">
              <p className="text-[11px] font-medium text-slate-500">Numeric Features</p>
              <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">
                {result.summary?.numeric_columns?.length || 0}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40">
              <p className="text-[11px] font-medium text-slate-500">Categorical Features</p>
              <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">
                {result.summary?.categorical_columns?.length || 0}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40">
              <p className="text-[11px] font-medium text-slate-500">Total Encoded ML Dims</p>
              <p className="text-xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">
                {result.summary?.total_encoded_dimensions || 0} dimensions
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
