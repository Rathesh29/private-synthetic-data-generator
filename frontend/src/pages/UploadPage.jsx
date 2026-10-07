import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  UploadCloud, 
  FileSpreadsheet, 
  CheckCircle2, 
  AlertCircle, 
  Info, 
  ArrowLeft,
  ShieldCheck,
  Download
} from 'lucide-react';
import apiClient from '../api/client';

export const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      if (!name) {
        setName(selected.name.replace(/\.[^/.]+$/, ""));
      }
      setError(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selected = e.dataTransfer.files[0];
      setFile(selected);
      if (!name) {
        setName(selected.name.replace(/\.[^/.]+$/, ""));
      }
      setError(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a valid CSV or Excel file to upload.');
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);
    formData.append('description', description);

    try {
      const res = await apiClient.post('/datasets/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      navigate(`/datasets/${res.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload dataset. Check format and size.');
      setUploading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link
          to="/datasets"
          className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-500"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Upload Sensitive HR Dataset
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Ingest corporate workforce records (.csv, .xlsx). Records are parsed and audited securely.
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/40 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Upload Form */}
      <form onSubmit={handleSubmit} className="bg-white dark:bg-slate-900 p-6 md:p-8 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
        {/* Drop zone */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-2xl p-8 text-center transition-colors
            ${file 
              ? 'border-indigo-400 bg-indigo-50/30 dark:bg-indigo-950/20' 
              : 'border-slate-300 dark:border-slate-700 hover:border-indigo-400 bg-slate-50/50 dark:bg-slate-800/30'}
          `}
        >
          <input
            type="file"
            id="fileInput"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileChange}
            className="hidden"
          />

          {file ? (
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 rounded-xl bg-indigo-100 dark:bg-indigo-950 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-3">
                <FileSpreadsheet className="w-6 h-6" />
              </div>
              <p className="font-semibold text-slate-900 dark:text-white text-sm">{file.name}</p>
              <p className="text-xs text-slate-400 mt-1">{(file.size / 1024).toFixed(1)} KB</p>
              <label
                htmlFor="fileInput"
                className="mt-3 text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline cursor-pointer"
              >
                Choose a different file
              </label>
            </div>
          ) : (
            <label htmlFor="fileInput" className="cursor-pointer flex flex-col items-center">
              <div className="w-12 h-12 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400 mb-3">
                <UploadCloud className="w-6 h-6" />
              </div>
              <p className="text-sm font-semibold text-slate-900 dark:text-white">
                Drag and drop your HR dataset here, or <span className="text-indigo-600 dark:text-indigo-400">browse</span>
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Supports CSV, XLSX, XLS up to 25MB
              </p>
            </label>
          )}
        </div>

        {/* Dataset metadata inputs */}
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Dataset Name *
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Workforce Q3 Demographics & Compensation"
              className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Description / Notes
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Provide business unit, collection scope, or sensitivity level..."
              className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
            />
          </div>
        </div>

        {/* Security Disclosures */}
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2 text-xs">
          <div className="flex items-center gap-1.5 font-bold text-slate-900 dark:text-white">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            <span>Strict Privacy Handling Guarantees</span>
          </div>
          <ul className="text-slate-500 dark:text-slate-400 list-disc list-inside space-y-1 text-[11px] leading-relaxed">
            <li>Raw employee records are NEVER exposed in browser logs, application logs, or external telemetry.</li>
            <li>Direct identifiers (Employee IDs, SSNs, Full Names) are automatically identified for elimination.</li>
            <li>All upload events are audited with SHA-256 integrity and logged for enterprise compliance.</li>
          </ul>
        </div>

        <button
          type="submit"
          disabled={uploading || !file}
          className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-md shadow-indigo-600/20 transition-all flex items-center justify-center gap-2"
        >
          {uploading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Analyzing & Ingesting Dataset...</span>
            </>
          ) : (
            <>
              <UploadCloud className="w-4 h-4" />
              <span>Ingest & Validate HR Dataset</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};
