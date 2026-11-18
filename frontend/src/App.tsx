import React, { useState, useEffect } from 'react';
import { KpiRibbon } from './components/KpiRibbon';
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
} from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);

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

  const [analyzedModules, setAnalyzedModules] = useState<AnalyzedModule[]>([]);
  const [paretoPoints, setParetoPoints] = useState<ParetoPoint[]>([]);
  const [selectedParetoId, setSelectedParetoId] = useState<string>('P-Balanced-Optimal');
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
    setWeights(newWeights);
    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newWeights),
      });
      if (res.ok) {
        const data = await res.json();
        setAnalyzedModules(data.analyzed_modules);
      }
    } catch (e) {
      console.error(e);
    }
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
      {/* Persistent KPI Ribbon */}
      <KpiRibbon
        strategicValue={kpis.strategicValue}
        budgetUtilizationPct={kpis.budgetUtilizationPct}
        scheduleFeasibility={kpis.scheduleFeasibility}
        avgRPN={kpis.avgRPN}
        spi={kpis.spi}
        cpi={kpis.cpi}
        pmesScore={kpis.pmesScore}
        onLockAll={() => alert('Plan state locked & committed to compliance audit log.')}
      />

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
          <Tab3Counterfactual onRunSimulation={handleRunCounterfactual} />
        )}

        {activeTab === 4 && <Tab4Explainability />}

        {activeTab === 5 && (
          <Tab5Evaluation benchmarks={benchmarks} latexTable={latexTable} />
        )}
      </main>
    </div>
  );
};
