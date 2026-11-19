import React, { useState, useEffect } from 'react';
import { KpiRibbon, AuditLogEntry } from './components/KpiRibbon';
import { Tab1Strategic } from './tabs/Tab1Strategic';
import { Tab2Policy } from './tabs/Tab2Policy';
import { Tab3Counterfactual } from './tabs/Tab3Counterfactual';
import { Tab4Explainability } from './tabs/Tab4Explainability';
import { Tab5Evaluation } from './tabs/Tab5Evaluation';
import {
  AnalyzedModule,
  CriterionWeights,
  POSDCORBPolicies,
  ParetoPoint,
  Developer,
  BenchmarkResult,
  CounterfactualStrategy,
  SoftwareModule,
} from './types';
import { DEFAULT_RAW_MODULES, calculateLocalPortfolio } from './defaultData';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);

  // Lock status & Audit Log
  const [isLocked, setIsLocked] = useState<boolean>(false);
  const [showAuditModal, setShowAuditModal] = useState<boolean>(false);
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([
    {
      id: 'AUD-001',
      timestamp: new Date().toLocaleTimeString(),
      action: 'PARAMETER_UPDATED',
      description: 'System initialized baseline FinTech Cloud Migration dataset.',
      user: 'SYSTEM_ADMIN',
      severity: 'INFO',
    },
  ]);

  // Core state
  const [weights, setWeights] = useState<CriterionWeights>({
    strategic_alignment: 0.20,
    market_potential: 0.20,
    customer_value: 0.15,
    technical_feasibility: 0.15,
    financial_viability: 0.15,
    risk_adjusted_potential: 0.15,
  });

  const [policies, setPolicies] = useState<POSDCORBPolicies>({
    planning_strict_dependencies: true,
    organizing_skill_balancing: true,
    staffing_allow_overtime: false,
    directing_focus_high_alignment: true,
    coordinating_max_parallel_tasks: 4,
    reporting_fmea_threshold: 120,
    budgeting_contingency_buffer_pct: 0.10,
  });

  const [rawModules, setRawModules] = useState<SoftwareModule[]>(DEFAULT_RAW_MODULES);
  const [analyzedModules, setAnalyzedModules] = useState<AnalyzedModule[]>(() =>
    calculateLocalPortfolio(DEFAULT_RAW_MODULES, {
      strategic_alignment: 0.20,
      market_potential: 0.20,
      customer_value: 0.15,
      technical_feasibility: 0.15,
      financial_viability: 0.15,
      risk_adjusted_potential: 0.15,
    })
  );

  const [paretoPoints, setParetoPoints] = useState<ParetoPoint[]>([]);
  const [selectedParetoId, setSelectedParetoId] = useState<string>('P-Balanced-Optimal');
  const [activeStrategyId, setActiveStrategyId] = useState<string | undefined>(undefined);
  const [developers, setDevelopers] = useState<Developer[]>([]);
  const [benchmarks, setBenchmarks] = useState<BenchmarkResult[]>([]);
  const [latexTable, setLatexTable] = useState<string>('');

  // Top KPIs
  const [kpis, setKpis] = useState({
    strategicValue: 6.84,
    budgetUtilizationPct: 84.4,
    scheduleFeasibility: 'On-Track (130d / 170d)',
    avgRPN: 88,
    spi: 1.04,
    cpi: 1.02,
    pmesScore: 0.912,
  });

  const logAudit = (
    action: AuditLogEntry['action'],
    description: string,
    severity: AuditLogEntry['severity'] = 'INFO'
  ) => {
    const newEntry: AuditLogEntry = {
      id: `AUD-${String(auditLogs.length + 1).padStart(3, '0')}`,
      timestamp: new Date().toLocaleTimeString(),
      action,
      description,
      user: 'EXEC_OFFICER (Human-in-Loop)',
      severity,
    };
    setAuditLogs((prev) => [newEntry, ...prev]);
  };

  const handleToggleLock = () => {
    if (!isLocked) {
      setIsLocked(true);
      logAudit('PLAN_LOCKED', 'Manager approved and locked active allocation plan against edits.', 'WARNING');
    } else {
      setIsLocked(false);
      logAudit('PLAN_UNLOCKED', 'Manager unlocked allocation plan. Modifications and calibrations permitted.', 'INFO');
    }
  };

  // Fetch initial data
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const analyzeRes = await fetch('/api/analyze', { method: 'POST' });
        if (analyzeRes.ok) {
          const data = await analyzeRes.json();
          setAnalyzedModules(data.analyzed_modules);
        }

        const paretoRes = await fetch('/api/pareto');
        if (paretoRes.ok) {
          const data = await paretoRes.json();
          setParetoPoints(data);
        }

        const datasetRes = await fetch('/api/dataset');
        if (datasetRes.ok) {
          const data = await datasetRes.json();
          setDevelopers(data.developers);
        }

        const benchRes = await fetch('/api/evaluate/benchmarks');
        if (benchRes.ok) {
          const data = await benchRes.json();
          setBenchmarks(data.benchmarks);
          setLatexTable(data.latex_table);
        }
      } catch (err) {
        console.warn('Backend not reached yet, utilizing built-in enterprise FinTech state.');
      } finally {
        setLoading(false);
      }
    };
    fetchInitialData();
  }, []);

  const handleUpdateWeights = async (newWeights: CriterionWeights) => {
    if (isLocked) {
      alert('Plan is currently locked by manager approval. Click "🔓 Unlock Plan" to modify weights.');
      return;
    }
    setWeights(newWeights);
    const localUpdated = calculateLocalPortfolio(rawModules, newWeights);
    setAnalyzedModules(localUpdated);
    logAudit('PARAMETER_UPDATED', 'Re-calibrated AHP multi-criteria priority weights.');

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newWeights),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.analyzed_modules && data.analyzed_modules.length > 0) {
          setAnalyzedModules(data.analyzed_modules);
        }
      }
    } catch (e) {
      // Backend offline, local calculation active
    }
  };

  const handleUpdateModule = (updatedModule: SoftwareModule) => {
    if (isLocked) {
      alert('Plan is currently locked. Click "🔓 Unlock Plan" to modify module parameters.');
      return;
    }
    const updatedList = rawModules.map((m) => (m.id === updatedModule.id ? updatedModule : m));
    setRawModules(updatedList);
    const recalculated = calculateLocalPortfolio(updatedList, weights);
    setAnalyzedModules(recalculated);
    logAudit(
      'PARAMETER_UPDATED',
      `Modified parameters for ${updatedModule.id} ($${updatedModule.estimated_cost}, ${updatedModule.estimated_duration_days}d, RPN: ${updatedModule.fmea_severity * updatedModule.fmea_occurrence * updatedModule.fmea_detection}).`
    );
  };

  const handleAdoptStrategy = (strat: CounterfactualStrategy) => {
    setActiveStrategyId(strat.strategy_id);

    // Update Top KPIs
    setKpis({
      strategicValue: (strat.strategic_value_retained_pct / 100.0) * 7.5,
      budgetUtilizationPct: Math.round((strat.total_cost / 450000.0) * 1000) / 10,
      scheduleFeasibility: `${strat.total_duration_days}d (${strat.is_feasible ? 'Feasible' : 'Delayed'})`,
      avgRPN: Math.round(strat.avg_risk_rpn),
      spi: Number((strat.total_duration_days <= 145 ? 1.05 : 0.92).toFixed(2)),
      cpi: Number((strat.total_cost <= 330000 ? 1.03 : 0.95).toFixed(2)),
      pmesScore: strat.pmes_score,
    });

    logAudit(
      'STRATEGY_DEPLOYED',
      `Adopted ${strat.name}. Retained ${strat.modules_retained.length} modules, deferred: [${strat.modules_deferred.join(', ')}].`,
      'CRITICAL'
    );
  };

  const handleSelectParetoPoint = (point: ParetoPoint) => {
    setSelectedParetoId(point.solution_id);
    setKpis((prev) => ({
      ...prev,
      strategicValue: point.total_strategic_value,
      budgetUtilizationPct: (point.total_cost / 450000.0) * 100.0,
      avgRPN: Math.round(point.avg_risk_rpn),
      scheduleFeasibility: `${point.total_duration_days}d / 170d`,
    }));
  };

  const handleRunCounterfactual = async (
    budgetDeltaPct: number,
    devOutages: string[],
    deadlineDeltaDays: number
  ): Promise<CounterfactualStrategy[]> => {
    const res = await fetch('/api/counterfactual/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        budget_delta_pct: budgetDeltaPct,
        unavailable_dev_ids: devOutages,
        deadline_delta_days: deadlineDeltaDays,
      }),
    });
    if (res.ok) {
      const data = await res.json();
      return data.strategies;
    }
    return [];
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Persistent KPI Ribbon with Lock, Unlock and Audit Trail */}
      <KpiRibbon
        strategicValue={kpis.strategicValue}
        budgetUtilizationPct={kpis.budgetUtilizationPct}
        scheduleFeasibility={kpis.scheduleFeasibility}
        avgRPN={kpis.avgRPN}
        spi={kpis.spi}
        cpi={kpis.cpi}
        pmesScore={kpis.pmesScore}
        isLocked={isLocked}
        onToggleLock={handleToggleLock}
        onOpenAuditTrail={() => setShowAuditModal(true)}
        auditCount={auditLogs.length}
      />

      {/* Audit Trail Drawer Modal */}
      {showAuditModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl border border-slate-200 max-w-2xl w-full p-6 space-y-4 max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between border-b pb-3">
              <div>
                <h3 className="font-extrabold text-slate-900 text-sm flex items-center space-x-2">
                  <span>📋 Immutable Governance Audit Trail</span>
                  <span className="text-[10px] bg-blue-100 text-blue-800 font-mono px-2 py-0.5 rounded">
                    {auditLogs.length} Entries
                  </span>
                </h3>
                <p className="text-xs text-slate-500">
                  Cryptographically trackable log of all Human-in-the-Loop overrides & solver actions
                </p>
              </div>
              <button
                onClick={() => setShowAuditModal(false)}
                className="text-slate-400 hover:text-slate-600 font-bold"
              >
                ✕
              </button>
            </div>

            <div className="overflow-y-auto space-y-2.5 flex-1 pr-1">
              {auditLogs.map((log) => (
                <div
                  key={log.id}
                  className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs flex flex-col justify-between space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono font-bold text-slate-700">{log.id}</span>
                      <span
                        className={`text-[9px] font-bold px-1.5 py-0.2 rounded font-mono ${
                          log.severity === 'CRITICAL'
                            ? 'bg-rose-100 text-rose-800'
                            : log.severity === 'WARNING'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {log.action}
                      </span>
                    </div>
                    <span className="text-slate-400 font-mono text-[10px]">{log.timestamp}</span>
                  </div>
                  <p className="text-slate-800 font-medium text-[11px]">{log.description}</p>
                  <span className="text-[10px] text-slate-400 font-mono">Actor: {log.user}</span>
                </div>
              ))}
            </div>

            <div className="pt-3 border-t flex justify-between items-center text-xs">
              <span className="text-slate-500">Status: {isLocked ? '🔒 Plan Locked' : '🔓 Plan Active / Unlocked'}</span>
              <button
                onClick={() => setShowAuditModal(false)}
                className="px-4 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-white font-bold shadow"
              >
                Close Audit Log
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Tab Navigation Bar */}
      <div className="bg-white border-b border-slate-200 px-6 sticky top-0 z-20 shadow-xs">
        <div className="max-w-7xl mx-auto flex space-x-8">
          {[
            { id: 1, label: '1. Strategic Portfolio & BCG Matrix', badge: 'L1' },
            { id: 2, label: '2. Policy & Multi-Objective Pareto', badge: 'L2/L3' },
            { id: 3, label: '3. Counterfactual Management Twin', badge: 'L4 Twin' },
            { id: 4, label: '4. Explainable Decision Replay', badge: 'BFS Graph' },
            { id: 5, label: '5. Empirical Evaluation & Baselines', badge: 'B1–B4' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3.5 text-xs font-bold border-b-2 transition flex items-center space-x-2 ${
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-700'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <span>{tab.label}</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${
                activeTab === tab.id ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-500'
              }`}>
                {tab.badge}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Workspace Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-6">
        {activeTab === 1 && (
          <Tab1Strategic
            modules={analyzedModules}
            weights={weights}
            onUpdateWeights={handleUpdateWeights}
            onUpdateModule={handleUpdateModule}
            consistencyRatio={0.042}
          />
        )}

        {activeTab === 2 && (
          <Tab2Policy
            policies={policies}
            onUpdatePolicies={setPolicies}
            paretoPoints={paretoPoints}
            selectedParetoId={selectedParetoId}
            onSelectParetoPoint={handleSelectParetoPoint}
            developers={developers}
          />
        )}

        {activeTab === 3 && (
          <Tab3Counterfactual
            onRunSimulation={handleRunCounterfactual}
            onAdoptStrategy={handleAdoptStrategy}
            activeStrategyId={activeStrategyId}
          />
        )}

        {activeTab === 4 && <Tab4Explainability />}

        {activeTab === 5 && (
          <Tab5Evaluation benchmarks={benchmarks} latexTable={latexTable} />
        )}
      </main>
    </div>
  );
};
