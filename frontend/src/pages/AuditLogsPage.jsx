import React, { useEffect, useState } from 'react';
import { History, Shield, Download, Filter, Search } from 'lucide-react';
import apiClient from '../api/client';
import { DataTable } from '../components/DataTable';

export const AuditLogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [exports, setExports] = useState([]);
  const [activeTab, setActiveTab] = useState('audit'); // 'audit' or 'exports'
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [lRes, eRes] = await Promise.all([
          apiClient.get('/audit/logs'),
          apiClient.get('/audit/exports')
        ]);
        setLogs(lRes.data);
        setExports(eRes.data);
      } catch (err) {
        console.error("Failed to load audit records:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const auditColumns = [
    {
      header: 'Event ID',
      accessor: 'id',
      render: (row) => <span className="font-mono text-xs font-bold text-slate-500">#{row.id}</span>
    },
    {
      header: 'Action',
      accessor: 'action',
      render: (row) => (
        <span className="font-mono text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200">
          {row.action}
        </span>
      )
    },
    {
      header: 'User Email',
      accessor: 'user_email',
      render: (row) => <span className="font-semibold text-slate-900 dark:text-white text-xs">{row.user_email || 'System'}</span>
    },
    {
      header: 'Resource',
      accessor: 'resource_type',
      render: (row) => (
        <span className="text-slate-500 text-xs">
          {row.resource_type} {row.resource_id ? `(${row.resource_id})` : ''}
        </span>
      )
    },
    {
      header: 'IP Address',
      accessor: 'ip_address',
      render: (row) => <span className="font-mono text-[11px] text-slate-400">{row.ip_address || 'Internal'}</span>
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

  const exportColumns = [
    {
      header: 'Export ID',
      accessor: 'id',
      render: (row) => <span className="font-mono text-xs font-bold">#EXP-{row.id}</span>
    },
    {
      header: 'Job ID',
      accessor: 'generation_job_id',
      render: (row) => <span className="font-mono text-xs">Job #{row.generation_job_id}</span>
    },
    {
      header: 'Record Count',
      accessor: 'record_count',
      render: (row) => <strong className="text-slate-900 dark:text-white text-xs">{row.record_count.toLocaleString()}</strong>
    },
    {
      header: 'Format',
      accessor: 'format',
      render: (row) => <span className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 text-[11px] font-bold">{row.format}</span>
    },
    {
      header: 'Exported At',
      accessor: 'exported_at',
      render: (row) => (
        <span className="text-[11px] text-slate-400">
          {new Date(row.exported_at).toLocaleString()}
        </span>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Security & Compliance Audit Trail
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Enterprise immutable logging for dataset uploads, training jobs, parameter modifications, and dataset downloads.
          </p>
        </div>

        {/* Tab switch */}
        <div className="flex p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
          <button
            onClick={() => setActiveTab('audit')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'audit'
                ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            System Audit Events ({logs.length})
          </button>
          <button
            onClick={() => setActiveTab('exports')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'exports'
                ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Download History ({exports.length})
          </button>
        </div>
      </div>

      {activeTab === 'audit' ? (
        <DataTable
          columns={auditColumns}
          data={logs}
          searchKey="action"
          searchPlaceholder="Search audit actions (e.g., LOGIN, UPLOAD)..."
          loading={loading}
          emptyMessage="No security events logged yet."
        />
      ) : (
        <DataTable
          columns={exportColumns}
          data={exports}
          searchKey="format"
          searchPlaceholder="Filter export records..."
          loading={loading}
          emptyMessage="No dataset export downloads recorded."
        />
      )}
    </div>
  );
};
