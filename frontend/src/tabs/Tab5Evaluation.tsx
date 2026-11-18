import React, { useState } from 'react';
import { BenchmarkResult } from '../types';

interface Tab5EvaluationProps {
  benchmarks: BenchmarkResult[];
  latexTable: string;
}

export const Tab5Evaluation: React.FC<Tab5EvaluationProps> = ({ benchmarks, latexTable }) => {
  const [showLatex, setShowLatex] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  const handleCopyLatex = () => {
    navigator.clipboard.writeText(latexTable);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportCSV = () => {
    const headers = [
      'Baseline ID',
      'Configuration Name',
      'Resource Utilization (%)',
      'Budget Adherence (%)',
      'Schedule Feasibility (%)',
      'Strategic Score',
      'Average RPN',
      'Violations Count',
      'Explanation Completeness (%)',
      'PMES Score',
    ];
    const rows = benchmarks.map((b) => [
      b.baseline_id,
      `"${b.name}"`,
      b.resource_utilization_pct,
      b.budget_adherence_pct,
      b.schedule_feasibility_pct,
      b.strategic_alignment_score,
      b.average_rpn_risk,
      b.constraint_violations_count,
      b.explanation_path_completeness_pct,
      b.pmes_score,
    ]);

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'STRATOS_AI_Benchmark_Ablation_Results.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Export Actions */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="font-bold text-slate-800 text-sm">Empirical Evaluation & Ablation Study (B1–B4)</h3>
          <p className="text-xs text-slate-500">
            Rigorous comparative benchmark against conventional and unconstrained project management baselines
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowLatex(!showLatex)}
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded border border-slate-300 transition"
          >
            {showLatex ? 'Hide LaTeX Table' : 'View LaTeX Table'}
          </button>
          <button
            onClick={handleExportCSV}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded shadow transition flex items-center space-x-1"
          >
            <span>Export CSV for Paper</span>
          </button>
        </div>
      </div>

      {/* LaTeX Drawer */}
      {showLatex && (
        <div className="bg-slate-900 text-slate-100 p-4 rounded-xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-emerald-400">LaTeX Source (Ready for ACM/IEEE Manuscript):</span>
            <button
              onClick={handleCopyLatex}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-2.5 py-1 rounded font-mono transition"
            >
              {copied ? '✓ Copied!' : 'Copy to Clipboard'}
            </button>
          </div>
          <pre className="text-[11px] font-mono overflow-x-auto p-3 bg-slate-950 rounded border border-slate-800 text-slate-300">
            {latexTable}
          </pre>
        </div>
      )}

      {/* Benchmark Comparison Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100">
          <h4 className="font-bold text-slate-800 text-sm">Ablation Matrix: STRATOS-AI (B4) vs. Baselines (B1–B3)</h4>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-semibold">
                <th className="py-3 px-4">Configuration</th>
                <th className="py-3 px-4 text-center">Res. Util.</th>
                <th className="py-3 px-4 text-center">Budget Adherence</th>
                <th className="py-3 px-4 text-center">Schedule Feas.</th>
                <th className="py-3 px-4 text-center">Strategic Score</th>
                <th className="py-3 px-4 text-center">Avg RPN</th>
                <th className="py-3 px-4 text-center">Violations</th>
                <th className="py-3 px-4 text-center">Expl. Completeness</th>
                <th className="py-3 px-4 text-right">Composite PMES</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {benchmarks.map((b) => {
                const isB4 = b.baseline_id === 'B4';
                return (
                  <tr
                    key={b.baseline_id}
                    className={`transition ${isB4 ? 'bg-blue-50/60 font-semibold' : 'hover:bg-slate-50/80'}`}
                  >
                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          isB4 ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-800'
                        }`}>
                          {b.baseline_id}
                        </span>
                        <div>
                          <div className="font-bold text-slate-900">{b.name}</div>
                          <div className="text-[11px] text-slate-500 font-normal">{b.description}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-center font-mono">{b.resource_utilization_pct}%</td>
                    <td className="py-3.5 px-4 text-center font-mono">{b.budget_adherence_pct}%</td>
                    <td className="py-3.5 px-4 text-center font-mono">{b.schedule_feasibility_pct}%</td>
                    <td className="py-3.5 px-4 text-center font-mono font-bold text-slate-800">
                      {b.strategic_alignment_score}
                    </td>
                    <td className="py-3.5 px-4 text-center font-mono">
                      <span className={b.average_rpn_risk > 115 ? 'text-rose-600 font-bold' : 'text-slate-700'}>
                        {b.average_rpn_risk}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center font-mono">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                        b.constraint_violations_count === 0 ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                      }`}>
                        {b.constraint_violations_count}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center font-mono">{b.explanation_path_completeness_pct}%</td>
                    <td className="py-3.5 px-4 text-right font-mono font-black text-sm text-blue-700">
                      {b.pmes_score.toFixed(3)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
