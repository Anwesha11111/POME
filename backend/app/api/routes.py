from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.models.schemas import (
    SoftwareModule,
    Developer,
    ProjectConfig,
    OptimizationResult,
    CriterionWeights,
    AllocationDecision,
    EvaluationMetrics,
)
from app.data.seed_loader import SeedDataLoader
from app.engines.strategic_engine import StrategicPrioritisationEngine
from app.engines.policy_engine import ManagementPolicyEngine
from app.engines.optimizer_engine import MultiObjectiveResourceOptimizer
from app.engines.knowledge_graph import KnowledgeGraphEngine
from app.engines.counterfactual_twin import CounterfactualTwin
from app.engines.evaluation_engine import ComparativeEvaluationEngine

router = APIRouter(prefix="/api", tags=["STRATOS-AI Engine"])

# Live In-Memory Session
CURRENT_MODULES, CURRENT_DEVELOPERS, CURRENT_CONFIG = SeedDataLoader.get_default_dataset()


class AHPMatrixInput(BaseModel):
    matrix: List[List[float]] = Field(..., description="Square pairwise comparison matrix (n x n)")


class CounterfactualRequest(BaseModel):
    budget_delta_pct: float = Field(default=0.0, ge=-0.9, le=1.0)
    unavailable_dev_ids: List[str] = Field(default_factory=list)
    deadline_delta_days: int = Field(default=0)


class GraphReplayRequest(BaseModel):
    trigger_id: str = Field(default="TRIGGER-BUDGET-CUT")


@router.get("/dataset")
def get_current_dataset():
    """Retrieve active modules, developers, and project configuration."""
    return {
        "modules": CURRENT_MODULES,
        "developers": CURRENT_DEVELOPERS,
        "config": CURRENT_CONFIG,
    }


@router.post("/dataset/reset")
def reset_dataset():
    """Reset dataset back to default Enterprise FinTech Cloud Migration benchmark."""
    global CURRENT_MODULES, CURRENT_DEVELOPERS, CURRENT_CONFIG
    CURRENT_MODULES, CURRENT_DEVELOPERS, CURRENT_CONFIG = SeedDataLoader.get_default_dataset()
    return {"message": "Dataset successfully reset to FinTech Cloud Migration benchmark"}


@router.post("/analyze")
def analyze_portfolio(weights_override: Optional[CriterionWeights] = None):
    """
    Layer L1: Strategic Portfolio Analysis
    Calculates multi-criteria priority scores P_i, BCG quadrant classifications,
    and returns ranked modules with proxy tags.
    """
    weights = weights_override or CURRENT_CONFIG.criterion_weights
    analyzed = StrategicPrioritisationEngine.analyze_portfolio(CURRENT_MODULES, weights)
    return {
        "analyzed_modules": analyzed,
        "active_weights": weights,
        "count": len(analyzed),
    }


@router.post("/ahp-weights")
def compute_ahp_weights(input_data: AHPMatrixInput):
    """
    Layer L1: AHP Pairwise Comparison Matrix Calculator
    Computes priority weights and checks Consistency Ratio (CR < 0.10).
    """
    try:
        return StrategicPrioritisationEngine.compute_ahp_weights(input_data.matrix)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/optimize", response_model=OptimizationResult)
def run_optimization(config_override: Optional[ProjectConfig] = None):
    """
    Layers L2 & L3: Multi-Objective Resource Optimizer
    Solves for binary module selection, developer skill assignments, start times,
    EVM tracking, and PMES scoring.
    """
    cfg = config_override or CURRENT_CONFIG
    optimizer = MultiObjectiveResourceOptimizer(CURRENT_MODULES, CURRENT_DEVELOPERS, cfg)
    
    sel_ids, assignments, starts = optimizer.solve()
    
    # Calculate allocations
    allocations = []
    for m in CURRENT_MODULES:
        is_sel = m.id in sel_ids
        assigned = assignments.get(m.id, [])
        allocations.append(
            AllocationDecision(
                module_id=m.id,
                selected=is_sel,
                assigned_developers=assigned,
                start_day=starts.get(m.id, 0),
                end_day=starts.get(m.id, 0) + m.estimated_duration_days if is_sel else 0,
                allocated_cost=m.estimated_cost if is_sel else 0.0,
                composite_score=StrategicPrioritisationEngine.calculate_priority_score(m, cfg.criterion_weights),
                rpn=m.rpn,
                rationale="Selected in Pareto-optimal allocation." if is_sel else "De-scoped by policy / budget limit."
            )
        )

    # Compute EVM and PMES metrics
    total_cost = sum(m.estimated_cost for m in CURRENT_MODULES if m.id in sel_ids)
    dur = max([starts.get(m.id, 0) + m.estimated_duration_days for m in CURRENT_MODULES if m.id in sel_ids], default=0)
    val = sum(StrategicPrioritisationEngine.calculate_priority_score(m, cfg.criterion_weights) for m in CURRENT_MODULES if m.id in sel_ids)
    rpn = sum(m.rpn for m in CURRENT_MODULES if m.id in sel_ids) / max(1, len(sel_ids))

    policy_eng = ManagementPolicyEngine(CURRENT_MODULES, CURRENT_DEVELOPERS, cfg)
    is_feas, viols, audit = policy_eng.validate_posdcorb_constraints(sel_ids, assignments, starts)

    dev_util = {}
    for d in CURRENT_DEVELOPERS:
        assigned_hours = sum(
            (m.estimated_duration_days * 8 / max(1, len(assignments.get(m.id, []))))
            for m in CURRENT_MODULES if m.id in sel_ids and d.id in assignments.get(m.id, [])
        )
        dev_util[d.id] = round((assigned_hours / d.max_capacity_hours) * 100.0, 1)

    metrics = EvaluationMetrics(
        budget_utilization_pct=round((total_cost / cfg.total_budget) * 100.0, 1),
        time_critical_path_days=dur,
        schedule_variance_days=cfg.target_deadline_day - dur,
        aggregate_strategic_score=round(val, 2),
        average_rpn=round(rpn, 1),
        unassigned_skills_count=0,
        developer_utilization=dev_util,
    )

    pareto = optimizer.generate_pareto_frontier()

    # Replay trace
    kg = KnowledgeGraphEngine(CURRENT_MODULES, CURRENT_DEVELOPERS, cfg)
    replay = kg.perform_bfs_decision_replay("TRIGGER-BUDGET-CUT")

    # Counterfactuals
    twin = CounterfactualTwin(CURRENT_MODULES, CURRENT_DEVELOPERS, cfg)
    cf_res = twin.simulate_perturbation(budget_delta_pct=-0.15)
    counterfactuals = [
        s for s in cf_res["strategies"]
    ]

    return OptimizationResult(
        status="OPTIMAL" if is_feas else "FEASIBLE",
        allocations=allocations,
        metrics=metrics,
        pareto_frontier=pareto,
        bfs_replay_trace=[],
        counterfactuals=[]
    )


@router.get("/pareto")
def get_pareto_frontier():
    """Generates Pareto frontier curves for Cost, Risk, and Strategic Value."""
    optimizer = MultiObjectiveResourceOptimizer(CURRENT_MODULES, CURRENT_DEVELOPERS, CURRENT_CONFIG)
    return optimizer.generate_pareto_frontier()


@router.post("/counterfactual/simulate")
def simulate_counterfactual(req: CounterfactualRequest):
    """
    Layer L4: Counterfactual Management Twin Simulation
    Evaluates Strategy A, B, and C under budget, resource, and schedule shocks.
    """
    twin = CounterfactualTwin(CURRENT_MODULES, CURRENT_DEVELOPERS, CURRENT_CONFIG)
    return twin.simulate_perturbation(
        budget_delta_pct=req.budget_delta_pct,
        unavailable_dev_ids=req.unavailable_dev_ids,
        deadline_delta_days=req.deadline_delta_days,
    )


@router.post("/graph/replay")
def perform_graph_replay(req: GraphReplayRequest):
    """
    Layer L4: Knowledge Graph BFS Decision Replay
    Traces level-by-level causal propagation: Trigger -> Module -> Task -> Milestone -> Recommendation.
    """
    kg = KnowledgeGraphEngine(CURRENT_MODULES, CURRENT_DEVELOPERS, CURRENT_CONFIG)
    return kg.perform_bfs_decision_replay(req.trigger_id)


@router.get("/graph/schema")
def get_graph_schema():
    """Returns entire Knowledge Graph in React Flow node-link structure."""
    kg = KnowledgeGraphEngine(CURRENT_MODULES, CURRENT_DEVELOPERS, CURRENT_CONFIG)
    return kg.export_graph_json()


@router.get("/evaluate/benchmarks")
def evaluate_benchmarks():
    """
    Empirical Evaluation & Ablation Suite
    Compares B1, B2, B3, and B4 (Full STRATOS-AI) and generates LaTeX report table.
    """
    eval_eng = ComparativeEvaluationEngine(CURRENT_MODULES, CURRENT_DEVELOPERS, CURRENT_CONFIG)
    benchmarks = eval_eng.run_all_benchmarks()
    latex_table = eval_eng.generate_latex_table(benchmarks)
    return {
        "benchmarks": benchmarks,
        "latex_table": latex_table,
    }
