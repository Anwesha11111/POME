import React from 'react';

interface KpiRibbonProps {
  strategicValue: number;
  budgetUtilizationPct: number;
  scheduleFeasibility: string;
  avgRPN: number;
  spi: number;
  cpi: number;
  pmesScore: number;
  onLockAll: () => void;
}

export const KpiRibbon: React.FC<KpiRibbonProps> = ({
  strategicValue,
  budgetUtilizationPct,
  scheduleFeasibility,
  avgRPN,
  spi,
  cpi,
  pmesScore,
  onLockAll,
}) => {
  return (
    <div className="bg-slate-900 text-white border-b border-slate-800 shadow-lg px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
        {/* Brand Title */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-blue-700 to-indigo-500 flex items-center justify-center font-black text-xl tracking-wider shadow-md">
            S
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg tracking-wide text-white">STRATOS-AI</span>
              <span className="text-[10px] uppercase font-bold tracking-widest bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-0.5 rounded">
                Enterprise Command Center
              </span>
            </div>
            <p className="text-xs text-slate-400">Explainable Decision-Support for Strategic Resource Allocation</p>
          </div>
        </div>

        {/* Persistent KPI Ribbon */}
        <div className="flex items-center gap-6 divide-x divide-slate-800">
          <div className="pl-4 text-center">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Strategic Value (V)</span>
            <span className="text-lg font-black text-emerald-400">{strategicValue.toFixed(2)}</span>
          </div>

          <div className="pl-4 text-center">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Budget Util (C / B)</span>
            <span className={`text-lg font-black ${budgetUtilizationPct > 95 ? 'text-amber-400' : 'text-slate-100'}`}>
              {budgetUtilizationPct.toFixed(1)}%
            </span>
          </div>

          <div className="pl-4 text-center">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Schedule</span>
            <span className="text-lg font-black text-blue-400">{scheduleFeasibility}</span>
          </div>

          <div className="pl-4 text-center">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Avg Risk (RPN)</span>
            <span className={`text-lg font-black ${avgRPN > 120 ? 'text-rose-400' : 'text-emerald-400'}`}>
              {avgRPN.toFixed(0)}
            </span>
          </div>

          <div className="pl-4 text-center">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">EVM (SPI / CPI)</span>
            <span className="text-lg font-black text-indigo-300">
              {spi.toFixed(2)} / {cpi.toFixed(2)}
            </span>
          </div>

          <div className="pl-4 text-center">
            <div className="flex items-center justify-center space-x-1">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">PMES Score</span>
              <span className="text-[9px] bg-amber-500/20 text-amber-300 border border-amber-500/30 px-1 rounded font-mono">
                Exploratory
              </span>
            </div>
            <span className="text-lg font-black text-emerald-300">{pmesScore.toFixed(3)}</span>
          </div>
        </div>

        {/* Human-in-the-loop Override Actions */}
        <div className="flex items-center space-x-2">
          <button
            onClick={onLockAll}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs shadow transition active:scale-95"
          >
            <span>Lock Plan & Audit Trail</span>
          </button>
        </div>
      </div>
    </div>
  );
};
