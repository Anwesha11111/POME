import React, { useState } from 'react';

export const Tab4Explainability: React.FC = () => {
  const [activeStep, setActiveStep] = useState<number>(0);
  const [activeTrigger, setActiveTrigger] = useState<string>('TRIGGER-BUDGET-CUT');

  const triggers = [
    { id: 'TRIGGER-BUDGET-CUT', label: 'Budget Cut (-25% / -$112,500)' },
    { id: 'TRIGGER-DEV-OUTAGE', label: 'Principal Architect Outage (Dr. Rostova)' },
    { id: 'TRIGGER-DEADLINE-PULL', label: 'Executive Target Accelerated (-20 Days)' },
  ];

  const replaySteps = [
    {
      depth: 0,
      title: 'Depth 0: Shock Perturbation Injected',
      node: activeTrigger,
      badge: 'Trigger Event',
      badgeColor: 'bg-rose-100 text-rose-800 border-rose-300',
      description: 'An external management perturbation is applied to the active project baseline.',
      details: 'Evaluates solver sensitivity under non-equilibrium state conditions.',
    },
    {
      depth: 1,
      title: 'Depth 1: Direct Component Impact',
      node: activeTrigger === 'TRIGGER-BUDGET-CUT' ? 'MOD-09 (Canary & Chaos)' : 'MOD-01 (VPC Foundation)',
      badge: 'Affected Module',
      badgeColor: 'bg-amber-100 text-amber-800 border-amber-300',
      description: 'Capital constraint directly breaches the allocation threshold for low-ROI or high-cost components.',
      details: 'POSDCORB Budgeting rule (HardBudgetCeiling) marks component candidate for de-scoping.',
    },
    {
      depth: 2,
      title: 'Depth 2: Dependency Precedence Blockage',
      node: 'MOD-10 (Predictive Analytics) & Downstream Pipelines',
      badge: 'Blocked Predecessor',
      badgeColor: 'bg-orange-100 text-orange-800 border-orange-300',
      description: 'Precedence graph traversal identifies dependent successors whose architectural prerequisites are violated.',
      details: 'Rule: s_j >= s_i + d_i violated for edge (MOD-09 -> MOD-10).',
    },
    {
      depth: 3,
      title: 'Depth 3: Critical Path & Milestone At Risk',
      node: 'MS-GO-LIVE (Production Customer Go-Live, Day 170)',
      badge: 'Milestone Slip',
      badgeColor: 'bg-purple-100 text-purple-800 border-purple-300',
      description: 'Critical path length exceeds target delivery deadline, resulting in negative schedule variance.',
      details: 'EVM Schedule Performance Index drops: SPI = 0.82 (Schedule slip of ~18 days).',
    },
    {
      depth: 4,
      title: 'Depth 4: Algorithmic Recommendation & Recourse',
      node: 'Strategy A: Scope Trim (Star Preservation) Recommended',
      badge: 'Optimal Recourse',
      badgeColor: 'bg-emerald-100 text-emerald-800 border-emerald-300',
      description: 'Decision Twin identifies Strategy A as the optimal recourse plan, retaining 88.4% strategic value.',
      details: 'Preserves Star modules (MOD-01..04), restores SPI to 1.0, and eliminates all policy violations.',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Controller */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="font-bold text-slate-800 text-sm">Explainable Decision Replay (Knowledge Graph + BFS)</h3>
          <p className="text-xs text-slate-500">
            Step-by-step causal propagation explaining why decisions were taken from trigger to recourse
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-600">Active Shock Trigger:</span>
          <select
            value={activeTrigger}
            onChange={(e) => {
              setActiveTrigger(e.target.value);
              setActiveStep(0);
            }}
            className="text-xs font-bold bg-slate-100 border border-slate-200 rounded-lg px-3 py-1.5 text-slate-800"
          >
            {triggers.map((t) => (
              <option key={t.id} value={t.id}>{t.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* BFS Stepper Interactive Visualizer */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        {/* Step Progress Pills */}
        <div className="flex items-center justify-between mb-8 relative">
          <div className="absolute top-1/2 left-0 right-0 h-1 bg-slate-100 -translate-y-1/2 -z-0" />
          {replaySteps.map((s, idx) => (
            <button
              key={s.depth}
              onClick={() => setActiveStep(idx)}
              className={`relative z-10 flex flex-col items-center transition group`}
            >
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-black text-xs transition border-2 ${
                  idx === activeStep
                    ? 'bg-blue-600 text-white border-blue-600 shadow-lg scale-110'
                    : idx < activeStep
                    ? 'bg-emerald-500 text-white border-emerald-500'
                    : 'bg-white text-slate-500 border-slate-300'
                }`}
              >
                D{s.depth}
              </div>
              <span className={`text-[11px] font-bold mt-2 ${idx === activeStep ? 'text-blue-700' : 'text-slate-600'}`}>
                {s.title.split(':')[0]}
              </span>
            </button>
          ))}
        </div>

        {/* Current Active Step Deep-Dive */}
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <span className={`text-xs font-bold px-2.5 py-1 rounded border uppercase ${replaySteps[activeStep].badgeColor}`}>
              {replaySteps[activeStep].badge}
            </span>
            <span className="text-xs font-mono font-bold text-slate-500">
              Depth Level {replaySteps[activeStep].depth} of 4
            </span>
          </div>

          <h4 className="text-base font-extrabold text-slate-900 mb-2">
            {replaySteps[activeStep].node}
          </h4>

          <p className="text-xs text-slate-600 font-medium mb-3">
            {replaySteps[activeStep].description}
          </p>

          <div className="bg-white p-3 rounded-lg border border-slate-200 text-xs font-mono text-slate-700">
            <span className="font-bold text-blue-700 block mb-1">Audit Trail & Formal Rationale:</span>
            {replaySteps[activeStep].details}
          </div>

          {/* Stepper Buttons */}
          <div className="flex justify-between items-center mt-6 pt-4 border-t border-slate-200">
            <button
              onClick={() => setActiveStep(Math.max(0, activeStep - 1))}
              disabled={activeStep === 0}
              className="px-4 py-1.5 rounded text-xs font-bold bg-white border border-slate-300 text-slate-700 disabled:opacity-40 hover:bg-slate-50 transition"
            >
              ← Previous Causal Hop
            </button>
            <span className="text-xs text-slate-500 font-semibold">
              Hop {activeStep + 1} / {replaySteps.length}
            </span>
            <button
              onClick={() => setActiveStep(Math.min(replaySteps.length - 1, activeStep + 1))}
              disabled={activeStep === replaySteps.length - 1}
              className="px-4 py-1.5 rounded text-xs font-bold bg-blue-600 text-white disabled:opacity-40 hover:bg-blue-500 transition shadow"
            >
              Next Causal Hop →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
