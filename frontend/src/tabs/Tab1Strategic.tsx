import React, { useState } from 'react';
import { AnalyzedModule, CriterionWeights } from '../types';

interface Tab1StrategicProps {
  modules: AnalyzedModule[];
  weights: CriterionWeights;
  onUpdateWeights: (newWeights: CriterionWeights) => void;
  consistencyRatio: number;
}

export const Tab1Strategic: React.FC<Tab1StrategicProps> = ({
  modules,
  weights,
  onUpdateWeights,
  consistencyRatio,
}) => {
  const [selectedQuadrant, setSelectedQuadrant] = useState<string>('ALL');

  const handleWeightChange = (key: keyof CriterionWeights, val: number) => {
    onUpdateWeights({
      ...weights,
      [key]: val,
    });
  };

  const filteredModules = selectedQuadrant === 'ALL'
    ? modules
    : modules.filter((m) => m.bcg_quadrant === selectedQuadrant);

  const getQuadrantColor = (quad: string) => {
    switch (quad) {
      case 'Stars':
        return 'bg-emerald-50 text-emerald-700 border-emerald-300';
      case 'Cash Cows':
        return 'bg-blue-50 text-blue-700 border-blue-300';
      case 'Question Marks':
        return 'bg-amber-50 text-amber-700 border-amber-300';
      case 'Dogs':
        return 'bg-rose-50 text-rose-700 border-rose-300';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & AHP Weights Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* AHP Weights Controls */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b pb-3">
            <div>
              <h3 className="font-bold text-slate-800 text-sm">AHP Criterion Weights (∑ w_j = 1.0)</h3>
              <p className="text-xs text-slate-500">Multi-criteria priority model calibration</p>
            </div>
            <div className="text-right">
              <span className={`text-xs px-2 py-0.5 rounded font-mono font-bold ${consistencyRatio < 0.1 ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}`}>
                CR = {consistencyRatio.toFixed(3)} {consistencyRatio < 0.1 ? '✓ Valid' : '⚠ Inconsistent'}
              </span>
            </div>
          </div>

          <div className="space-y-3">
            {(Object.keys(weights) as Array<keyof CriterionWeights>).map((key) => (
              <div key={key} className="space-y-1">
                <div className="flex justify-between text-xs font-medium text-slate-600">
                  <span className="capitalize">{key.replace('_', ' ')}</span>
                  <span className="font-mono font-bold text-slate-800">{(weights[key] * 100).toFixed(0)}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="0.5"
                  step="0.01"
                  value={weights[key]}
                  onChange={(e) => handleWeightChange(key, parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </div>
            ))}
          </div>
        </div>

        {/* 2x2 BCG Matrix Visual Representation */}
        <div className="lg:col-span-2 bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h3 className="font-bold text-slate-800 text-sm">BCG-Inspired Strategic Portfolio Matrix</h3>
              <p className="text-xs text-slate-500">Growth Potential (Proxy) vs. Relative Position (Proxy)</p>
            </div>
            <div className="flex space-x-1.5">
              {['ALL', 'Stars', 'Cash Cows', 'Question Marks', 'Dogs'].map((q) => (
                <button
                  key={q}
                  onClick={() => setSelectedQuadrant(q)}
                  className={`text-xs px-2.5 py-1 rounded font-semibold transition ${
                    selectedQuadrant === q
                      ? 'bg-slate-800 text-white shadow'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* 2x2 Quadrant Grid */}
          <div className="grid grid-cols-2 gap-3 h-64 mt-2">
            {/* Question Marks (Top Left: High Growth, Low Position) */}
            <div className="border-2 border-dashed border-amber-300 bg-amber-50/40 rounded-lg p-3 relative flex flex-col justify-between">
              <div className="flex justify-between items-start">
                <span className="font-extrabold text-xs text-amber-800 uppercase tracking-wider">? Question Marks</span>
                <span className="text-[10px] text-amber-700 bg-amber-100 px-1.5 py-0.5 rounded font-medium">Selective R&D</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {modules.filter((m) => m.bcg_quadrant === 'Question Marks').map((m) => (
                  <span key={m.module.id} className="text-[11px] bg-white border border-amber-300 text-amber-900 font-bold px-2 py-0.5 rounded shadow-sm">
                    {m.module.id}
                  </span>
                ))}
              </div>
              <span className="text-[10px] text-slate-400">High Growth, Low Relative Position</span>
            </div>

            {/* Stars (Top Right: High Growth, High Position) */}
            <div className="border-2 border-emerald-400 bg-emerald-50/50 rounded-lg p-3 relative flex flex-col justify-between">
              <div className="flex justify-between items-start">
                <span className="font-extrabold text-xs text-emerald-800 uppercase tracking-wider">★ Stars</span>
                <span className="text-[10px] text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded font-medium">Protect & Prioritize</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {modules.filter((m) => m.bcg_quadrant === 'Stars').map((m) => (
                  <span key={m.module.id} className="text-[11px] bg-white border border-emerald-400 text-emerald-900 font-bold px-2 py-0.5 rounded shadow-sm">
                    {m.module.id}
                  </span>
                ))}
              </div>
              <span className="text-[10px] text-slate-400">High Growth, High Relative Position</span>
            </div>

            {/* Dogs (Bottom Left: Low Growth, Low Position) */}
            <div className="border-2 border-dashed border-rose-300 bg-rose-50/40 rounded-lg p-3 relative flex flex-col justify-between">
              <div className="flex justify-between items-start">
                <span className="font-extrabold text-xs text-rose-800 uppercase tracking-wider">✕ Dogs</span>
                <span className="text-[10px] text-rose-700 bg-rose-100 px-1.5 py-0.5 rounded font-medium">De-scope / Defer</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {modules.filter((m) => m.bcg_quadrant === 'Dogs').map((m) => (
                  <span key={m.module.id} className="text-[11px] bg-white border border-rose-300 text-rose-900 font-bold px-2 py-0.5 rounded shadow-sm">
                    {m.module.id}
                  </span>
                ))}
              </div>
              <span className="text-[10px] text-slate-400">Low Growth, Low Relative Position</span>
            </div>

            {/* Cash Cows (Bottom Right: Low Growth, High Position) */}
            <div className="border-2 border-blue-400 bg-blue-50/50 rounded-lg p-3 relative flex flex-col justify-between">
              <div className="flex justify-between items-start">
                <span className="font-extrabold text-xs text-blue-800 uppercase tracking-wider">◆ Cash Cows</span>
                <span className="text-[10px] text-blue-700 bg-blue-100 px-1.5 py-0.5 rounded font-medium">Maintain Backbone</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {modules.filter((m) => m.bcg_quadrant === 'Cash Cows').map((m) => (
                  <span key={m.module.id} className="text-[11px] bg-white border border-blue-400 text-blue-900 font-bold px-2 py-0.5 rounded shadow-sm">
                    {m.module.id}
                  </span>
                ))}
              </div>
              <span className="text-[10px] text-slate-400">Low Growth, High Relative Position</span>
            </div>
          </div>
        </div>
      </div>

      {/* Module Prioritization Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-800 text-sm">Strategic Priority Ranking Table</h3>
            <p className="text-xs text-slate-500">Includes observed metrics from Jira exports and explicitly tagged proxy indicators</p>
          </div>
          <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2.5 py-1 rounded">
            Showing {filteredModules.length} Modules
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-semibold">
                <th className="py-3 px-4">Rank</th>
                <th className="py-3 px-4">Module ID & Name</th>
                <th className="py-3 px-4">Quadrant</th>
                <th className="py-3 px-4 text-right">Est. Cost</th>
                <th className="py-3 px-4 text-center">FMEA (RPN)</th>
                <th className="py-3 px-4 text-right">Priority (P_i)</th>
                <th className="py-3 px-4">Action Recommendation</th>
                <th className="py-3 px-4">Indicator Badges</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredModules.map((item) => (
                <tr key={item.module.id} className="hover:bg-slate-50/80 transition">
                  <td className="py-3 px-4 font-mono font-bold text-slate-700">#{item.strategic_rank}</td>
                  <td className="py-3 px-4">
                    <div className="font-bold text-slate-900">{item.module.id} - {item.module.name}</div>
                    <div className="text-[11px] text-slate-500 truncate max-w-xs">{item.module.description}</div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold border ${getQuadrantColor(item.bcg_quadrant)}`}>
                      {item.bcg_quadrant}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-mono font-medium text-slate-800">
                    ${item.module.estimated_cost.toLocaleString()}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`inline-block px-2 py-0.5 rounded font-mono font-bold text-[11px] ${
                      (item.module.rpn || 0) > 120 ? 'bg-rose-100 text-rose-800' : 'bg-slate-100 text-slate-700'
                    }`}>
                      {item.module.rpn || (item.module.fmea_severity * item.module.fmea_occurrence * item.module.fmea_detection)}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-mono font-black text-blue-600 text-sm">
                    {item.priority_score.toFixed(3)}
                  </td>
                  <td className="py-3 px-4 text-slate-600 font-medium text-[11px]">
                    {item.recommended_action}
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex flex-wrap gap-1">
                      <span className="text-[9px] bg-blue-50 text-blue-700 border border-blue-200 px-1 rounded">
                        Jira: {item.module.source_origin}
                      </span>
                      <span className="text-[9px] bg-slate-100 text-slate-600 border border-slate-200 px-1 rounded">
                        Proxy Tagged
                      </span>
                    </div>
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
