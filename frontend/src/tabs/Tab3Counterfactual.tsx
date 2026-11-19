import React, { useState } from 'react';
import { CounterfactualStrategy } from '../types';

interface Tab3CounterfactualProps {
  onRunSimulation: (budgetDeltaPct: number, devOutages: string[], deadlineDeltaDays: number) => Promise<CounterfactualStrategy[]>;
  onAdoptStrategy: (strat: CounterfactualStrategy) => void;
  activeStrategyId?: string;
}

export const Tab3Counterfactual: React.FC<Tab3CounterfactualProps> = ({
  onRunSimulation,
  onAdoptStrategy,
  activeStrategyId,
}) => {
  const [budgetCutPct, setBudgetCutPct] = useState<number>(-25);
  const [devOutage, setDevOutage] = useState<string>('DEV-01');
  const [deadlineDelta, setDeadlineDelta] = useState<number>(-15);
  const [loading, setLoading] = useState<boolean>(false);
  const [adoptedNotification, setAdoptedNotification] = useState<string | null>(null);

  const [strategies, setStrategies] = useState<CounterfactualStrategy[]>([
    {
      strategy_id: 'STRAT-A',
      name: 'Strategy A: Scope Trim (Star Preservation)',
      description: 'De-scopes low-priority modules to absorb budget/resource cuts while strictly protecting Star architectural flagships.',
      total_cost: 320000.0,
      total_duration_days: 130,
      strategic_value_retained_pct: 88.4,
      avg_risk_rpn: 85.0,
      is_feasible: true,
      pmes_score: 0.892,
      modules_retained: ['MOD-01', 'MOD-02', 'MOD-03', 'MOD-04', 'MOD-06'],
      modules_deferred: ['MOD-05', 'MOD-07', 'MOD-08', 'MOD-09', 'MOD-10'],
      policy_violations_count: 0,
      tradeoff_verdict: 'Highest architectural safety, minimum risk exposure, slight scope reduction.',
    },
    {
      strategy_id: 'STRAT-B',
      name: 'Strategy B: Staff Reallocation & Overtime',
      description: 'Preserves broad module scope by reassigning existing engineers and authorizing overtime (+8% budget premium).',
      total_cost: 345000.0,
      total_duration_days: 145,
      strategic_value_retained_pct: 95.2,
      avg_risk_rpn: 118.0,
      is_feasible: true,
      pmes_score: 0.810,
      modules_retained: ['MOD-01', 'MOD-02', 'MOD-03', 'MOD-04', 'MOD-05', 'MOD-06', 'MOD-07'],
      modules_deferred: ['MOD-08', 'MOD-09', 'MOD-10'],
      policy_violations_count: 2,
      tradeoff_verdict: 'Retains full scope but increases developer fatigue and risk exposure (+15% RPN).',
    },
    {
      strategy_id: 'STRAT-C',
      name: 'Strategy C: Schedule Extension (+35 Days)',
      description: 'Extends milestone delivery schedule by +35 days to eliminate overtime and absorb headcount constraints safely.',
      total_cost: 330000.0,
      total_duration_days: 165,
      strategic_value_retained_pct: 92.0,
      avg_risk_rpn: 89.0,
      is_feasible: true,
      pmes_score: 0.865,
      modules_retained: ['MOD-01', 'MOD-02', 'MOD-03', 'MOD-04', 'MOD-06', 'MOD-08'],
      modules_deferred: ['MOD-05', 'MOD-07', 'MOD-09', 'MOD-10'],
      policy_violations_count: 0,
      tradeoff_verdict: 'Highest feasibility and stability, zero overtime penalty, delayed time-to-market.',
    },
  ]);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const results = await onRunSimulation(
        budgetCutPct / 100.0,
        devOutage ? [devOutage] : [],
        deadlineDelta
      );
      if (results && results.length > 0) {
        setStrategies(results);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDeploy = (strat: CounterfactualStrategy) => {
    onAdoptStrategy(strat);
    setAdoptedNotification(`✓ ${strat.name} successfully adopted! Active baseline & KPIs updated.`);
    setTimeout(() => setAdoptedNotification(null), 4000);
  };

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {adoptedNotification && (
        <div className="p-3 bg-emerald-600 text-white font-bold text-xs rounded-lg shadow-lg flex items-center justify-between transition-all">
          <span>{adoptedNotification}</span>
          <button onClick={() => setAdoptedNotification(null)} className="text-white hover:text-slate-200">✕</button>
        </div>
      )}

      {/* What-If Shock Simulator Controls */}
      <div className="bg-slate-900 text-white p-5 rounded-xl border border-slate-800 shadow-md">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-extrabold text-base text-white tracking-wide">
              Counterfactual Management Twin: What-If Shock Simulator
            </h3>
            <p className="text-xs text-slate-400">
              Perturb project parameters to evaluate real-time strategic trade-offs across 3 recourse strategies
            </p>
          </div>
          <button
            onClick={handleSimulate}
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 font-bold text-xs shadow-md transition active:scale-95 flex items-center space-x-1.5"
          >
            <span>{loading ? 'Simulating Solver...' : '⚡ Run Twin Simulation'}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-3 border-t border-slate-800">
          {/* Shock 1: Budget Cut */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-300">Capital Budget Shock</span>
              <span className="font-mono text-rose-400 font-bold">{budgetCutPct}%</span>
            </div>
            <input
              type="range"
              min="-50"
              max="20"
              step="5"
              value={budgetCutPct}
              onChange={(e) => setBudgetCutPct(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-rose-500"
            />
            <span className="text-[10px] text-slate-400 block">Simulates sudden fiscal cuts or venture capital trim</span>
          </div>

          {/* Shock 2: Resource Outage */}
          <div className="space-y-2">
            <span className="text-xs font-semibold text-slate-300 block">Critical Headcount Outage</span>
            <select
              value={devOutage}
              onChange={(e) => setDevOutage(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg text-xs p-2 text-white font-medium"
            >
              <option value="DEV-01">Dr. Elena Rostova (Principal Cloud Architect)</option>
              <option value="DEV-02">Marcus Vance (Lead Security Engineer)</option>
              <option value="DEV-03">Amina Al-Mansoor (Senior DB Engineer)</option>
              <option value="DEV-04">Kai Chen (Senior Backend Architect)</option>
              <option value="">None (Full Team Available)</option>
            </select>
            <span className="text-[10px] text-slate-400 block">Removes engineer from solver constraint matrices</span>
          </div>

          {/* Shock 3: Deadline Compression */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-300">Milestone Compression</span>
              <span className="font-mono text-amber-400 font-bold">{deadlineDelta} Days</span>
            </div>
            <input
              type="range"
              min="-30"
              max="30"
              step="5"
              value={deadlineDelta}
              onChange={(e) => setDeadlineDelta(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
            <span className="text-[10px] text-slate-400 block">Simulates competitor launch forcing accelerated Go-Live</span>
          </div>
        </div>
      </div>

      {/* Side-by-Side 3-Strategy Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {strategies.map((strat) => {
          const isAdopted = activeStrategyId === strat.strategy_id;

          return (
            <div
              key={strat.strategy_id}
              className={`bg-white rounded-xl border-2 p-5 flex flex-col justify-between transition ${
                isAdopted
                  ? 'border-emerald-500 ring-2 ring-emerald-500/30 shadow-lg'
                  : 'border-slate-200 shadow-sm hover:shadow-md'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-black text-xs uppercase tracking-wider text-slate-800">
                    {strat.name}
                  </span>
                  <div className="flex items-center space-x-1.5">
                    {isAdopted && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-600 text-white">
                        ✓ ACTIVE PLAN
                      </span>
                    )}
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        strat.is_feasible
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                          : 'bg-rose-100 text-rose-800 border border-rose-200'
                      }`}
                    >
                      {strat.is_feasible ? '✓ Feasible' : '⚠ High Risk'}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-500 mb-4">{strat.description}</p>

                {/* Strategy Metrics Grid */}
                <div className="space-y-2 bg-slate-50 p-3 rounded-lg border border-slate-100 text-xs font-medium">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Revised Cost:</span>
                    <span className="font-mono font-bold text-slate-800">${strat.total_cost.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Duration:</span>
                    <span className="font-mono font-bold text-slate-800">{strat.total_duration_days} Days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Value Retained:</span>
                    <span className="font-mono font-black text-emerald-600">{strat.strategic_value_retained_pct}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Average RPN:</span>
                    <span className="font-mono font-bold text-slate-800">{strat.avg_risk_rpn}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">PMES Score:</span>
                    <span className="font-mono font-extrabold text-blue-600">{strat.pmes_score.toFixed(3)}</span>
                  </div>
                </div>

                {/* Modules Retained vs Deferred */}
                <div className="mt-4 space-y-2">
                  <div>
                    <span className="text-[11px] font-bold text-slate-700 block">Retained Scope:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {strat.modules_retained.map((m) => (
                        <span key={m} className="text-[9px] bg-emerald-50 text-emerald-800 border border-emerald-200 px-1.5 py-0.5 rounded font-mono font-semibold">
                          {m}
                        </span>
                      ))}
                    </div>
                  </div>

                  {strat.modules_deferred.length > 0 && (
                    <div>
                      <span className="text-[11px] font-bold text-slate-700 block">Deferred Modules:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {strat.modules_deferred.map((m) => (
                          <span key={m} className="text-[9px] bg-rose-50 text-rose-800 border border-rose-200 px-1.5 py-0.5 rounded font-mono font-semibold">
                            {m}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Trade-off Verdict Footer */}
              <div className="mt-5 pt-3 border-t border-slate-100">
                <span className="text-[11px] text-slate-600 italic block">
                  "{strat.tradeoff_verdict}"
                </span>
                <button
                  onClick={() => handleDeploy(strat)}
                  className={`w-full mt-3 py-1.5 rounded text-xs font-bold transition shadow ${
                    isAdopted
                      ? 'bg-emerald-700 hover:bg-emerald-600 text-white'
                      : 'bg-slate-800 hover:bg-slate-700 text-white'
                  }`}
                >
                  {isAdopted ? '✓ Currently Deployed' : 'Adopt & Deploy Strategy →'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
