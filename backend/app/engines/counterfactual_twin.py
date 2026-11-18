from typing import List, Dict, Any, Tuple
import copy
from app.models.schemas import (
    SoftwareModule,
    Developer,
    ProjectConfig,
    CounterfactualScenario,
)
from app.engines.strategic_engine import StrategicPrioritisationEngine
from app.engines.optimizer_engine import MultiObjectiveResourceOptimizer
from app.engines.policy_engine import ManagementPolicyEngine


class CounterfactualTwin:
    """
    Layer L4: Counterfactual Management Twin
    Interactive what-if simulation engine supporting perturbations:
    - Budget shock (e.g. -25% budget cut)
    - Resource shock (mark specific developer unavailable or capacity reduction)
    - Schedule shock (pull target deadline forward by N days)
    - Priority shift (increase weight on Risk-Adjusted Potential or Market)

    Automatically generates and solves 3 distinct strategic alternatives:
    - Strategy A: Scope Trim (Protect core 'Star' modules by deferring low-priority 'Dog/Question Mark' modules)
    - Strategy B: Staff Reallocation (Reallocate developers across modules, accepting minor skill-fit penalties)
    - Strategy C: Timeline Extension (Relax schedule constraints / extend target deadline to absorb shock)

    Compares all 3 alternatives side-by-side on Cost, Schedule Feasibility, RPN Risk Exposure,
    Strategic Value Retained, PMES score, and Policy Violations.
    """

    def __init__(self, modules: List[SoftwareModule], developers: List[Developer], base_config: ProjectConfig):
        self.modules = {m.id: copy.deepcopy(m) for m in modules}
        self.developers = {d.id: copy.deepcopy(d) for d in developers}
        self.base_config = copy.deepcopy(base_config)

    def simulate_perturbation(
        self,
        budget_delta_pct: float = 0.0,  # e.g. -0.25 (-25%)
        unavailable_dev_ids: List[str] = None,  # e.g. ["DEV-01"]
        deadline_delta_days: int = 0,  # e.g. -20 days
        weight_override: Dict[str, float] = None,
    ) -> Dict[str, Any]:
        unavailable_dev_ids = unavailable_dev_ids or []
        perturbed_budget = max(50000.0, self.base_config.total_budget * (1.0 + budget_delta_pct))
        perturbed_deadline = max(30, self.base_config.target_deadline_day + deadline_delta_days)

        active_devs = [
            d for d in self.developers.values() if d.id not in unavailable_dev_ids
        ]

        # Base Reference Plan (unperturbed)
        base_opt = MultiObjectiveResourceOptimizer(list(self.modules.values()), list(self.developers.values()), self.base_config)
        base_sel, base_assign, base_starts = base_opt.solve()
        base_cost = sum(self.modules[m].estimated_cost for m in base_sel)
        base_val = sum(StrategicPrioritisationEngine.calculate_priority_score(self.modules[m], self.base_config.criterion_weights) for m in base_sel)
        base_rpn = sum(self.modules[m].rpn for m in base_sel) / max(1, len(base_sel))

        # --- Strategy A: Scope Trim ---
        # Focus on "Star" and "Cash Cow" modules, de-scope "Dogs" and low-priority components
        cfg_a = copy.deepcopy(self.base_config)
        cfg_a.total_budget = perturbed_budget
        cfg_a.target_deadline_day = perturbed_deadline
        opt_a = MultiObjectiveResourceOptimizer(list(self.modules.values()), active_devs, cfg_a)
        # Weight value higher than cost to strictly protect stars
        sel_a, assign_a, starts_a = opt_a.solve(lambda_value=0.75, lambda_cost=0.15, lambda_risk=0.10)
        cost_a = sum(self.modules[m].estimated_cost for m in sel_a)
        val_a = sum(StrategicPrioritisationEngine.calculate_priority_score(self.modules[m], cfg_a.criterion_weights) for m in sel_a)
        rpn_a = sum(self.modules[m].rpn for m in sel_a) / max(1, len(sel_a))
        dur_a = max([starts_a.get(m, 0) + self.modules[m].estimated_duration_days for m in sel_a], default=0)

        # Policy & PMES checks for Strategy A
        pol_a = ManagementPolicyEngine(list(self.modules.values()), active_devs, cfg_a)
        is_feas_a, viols_a, _ = pol_a.validate_posdcorb_constraints(sel_a, assign_a, starts_a)
        pmes_a = opt_a.calculate_pmes(
            strategic_value_ratio=val_a / max(1.0, base_val),
            policy_compliance_ratio=1.0 - (len(viols_a) / 10.0),
            execution_efficiency_ratio=1.0 if dur_a <= perturbed_deadline else 0.70,
        )

        strat_a_result = {
            "strategy_id": "STRAT-A",
            "name": "Strategy A: Scope Trim (Star Preservation)",
            "description": "De-scopes low-priority modules to absorb budget/resource cuts while strictly protecting Star architectural flagships.",
            "total_cost": round(cost_a, 2),
            "total_duration_days": dur_a,
            "strategic_value_retained_pct": round((val_a / max(0.01, base_val)) * 100.0, 1),
            "avg_risk_rpn": round(rpn_a, 1),
            "is_feasible": is_feas_a and (dur_a <= perturbed_deadline),
            "pmes_score": pmes_a["pmes_score"],
            "modules_retained": sel_a,
            "modules_deferred": [m for m in self.modules.keys() if m not in sel_a],
            "policy_violations_count": len(viols_a),
            "tradeoff_verdict": "Highest architectural safety, minimum risk exposure, slight scope reduction.",
        }

        # --- Strategy B: Staff Reallocation ---
        # Keep modules funded, allow overtime and stretch team across tasks
        cfg_b = copy.deepcopy(self.base_config)
        cfg_b.total_budget = perturbed_budget
        cfg_b.target_deadline_day = perturbed_deadline
        cfg_b.posdcorb_policies.staffing_allow_overtime = True
        opt_b = MultiObjectiveResourceOptimizer(list(self.modules.values()), active_devs, cfg_b)
        sel_b, assign_b, starts_b = opt_b.solve(lambda_value=0.50, lambda_cost=0.30, lambda_risk=0.20)
        cost_b = sum(self.modules[m].estimated_cost for m in sel_b) * 1.08  # Overtime premium
        val_b = sum(StrategicPrioritisationEngine.calculate_priority_score(self.modules[m], cfg_b.criterion_weights) for m in sel_b)
        rpn_b = (sum(self.modules[m].rpn for m in sel_b) / max(1, len(sel_b))) * 1.15  # Fatigue/overload risk
        dur_b = max([starts_b.get(m, 0) + self.modules[m].estimated_duration_days for m in sel_b], default=0)

        pol_b = ManagementPolicyEngine(list(self.modules.values()), active_devs, cfg_b)
        is_feas_b, viols_b, _ = pol_b.validate_posdcorb_constraints(sel_b, assign_b, starts_b)
        pmes_b = opt_b.calculate_pmes(
            strategic_value_ratio=val_b / max(1.0, base_val),
            policy_compliance_ratio=max(0.4, 1.0 - (len(viols_b) / 10.0)),
            execution_efficiency_ratio=0.85,
        )

        strat_b_result = {
            "strategy_id": "STRAT-B",
            "name": "Strategy B: Staff Reallocation & Overtime",
            "description": "Preserves broad module scope by reassigning existing engineers and authorizing overtime (+8% budget premium).",
            "total_cost": round(cost_b, 2),
            "total_duration_days": dur_b,
            "strategic_value_retained_pct": round((val_b / max(0.01, base_val)) * 100.0, 1),
            "avg_risk_rpn": round(rpn_b, 1),
            "is_feasible": bool(cost_b <= perturbed_budget * 1.10),
            "pmes_score": pmes_b["pmes_score"],
            "modules_retained": sel_b,
            "modules_deferred": [m for m in self.modules.keys() if m not in sel_b],
            "policy_violations_count": len(viols_b),
            "tradeoff_verdict": "Retains full scope but increases developer fatigue and risk exposure (+15% RPN).",
        }

        # --- Strategy C: Timeline Extension ---
        # Relax target deadline by +30 days to avoid rush costs and overtime
        cfg_c = copy.deepcopy(self.base_config)
        cfg_c.total_budget = perturbed_budget
        cfg_c.target_deadline_day = perturbed_deadline + 35
        opt_c = MultiObjectiveResourceOptimizer(list(self.modules.values()), active_devs, cfg_c)
        sel_c, assign_c, starts_c = opt_c.solve(lambda_value=0.60, lambda_cost=0.30, lambda_risk=0.10)
        cost_c = sum(self.modules[m].estimated_cost for m in sel_c)
        val_c = sum(StrategicPrioritisationEngine.calculate_priority_score(self.modules[m], cfg_c.criterion_weights) for m in sel_c)
        rpn_c = sum(self.modules[m].rpn for m in sel_c) / max(1, len(sel_c))
        dur_c = max([starts_c.get(m, 0) + self.modules[m].estimated_duration_days for m in sel_c], default=0) + 15

        pol_c = ManagementPolicyEngine(list(self.modules.values()), active_devs, cfg_c)
        is_feas_c, viols_c, _ = pol_c.validate_posdcorb_constraints(sel_c, assign_c, starts_c)
        pmes_c = opt_c.calculate_pmes(
            strategic_value_ratio=val_c / max(1.0, base_val),
            policy_compliance_ratio=1.0 - (len(viols_c) / 10.0),
            execution_efficiency_ratio=0.80,
        )

        strat_c_result = {
            "strategy_id": "STRAT-C",
            "name": "Strategy C: Schedule Extension (+35 Days)",
            "description": "Extends milestone delivery schedule by +35 days to eliminate overtime and absorb headcount constraints safely.",
            "total_cost": round(cost_c, 2),
            "total_duration_days": dur_c,
            "strategic_value_retained_pct": round((val_c / max(0.01, base_val)) * 100.0, 1),
            "avg_risk_rpn": round(rpn_c, 1),
            "is_feasible": True,
            "pmes_score": pmes_c["pmes_score"],
            "modules_retained": sel_c,
            "modules_deferred": [m for m in self.modules.keys() if m not in sel_c],
            "policy_violations_count": len(viols_c),
            "tradeoff_verdict": "Highest feasibility and stability, zero overtime penalty, delayed time-to-market.",
        }

        return {
            "perturbation": {
                "budget_delta_pct": budget_delta_pct,
                "perturbed_budget": perturbed_budget,
                "unavailable_developers": unavailable_dev_ids,
                "deadline_delta_days": deadline_delta_days,
                "perturbed_deadline": perturbed_deadline,
            },
            "baseline_reference": {
                "total_cost": round(base_cost, 2),
                "total_strategic_value": round(base_val, 2),
                "avg_rpn": round(base_rpn, 1),
            },
            "strategies": [strat_a_result, strat_b_result, strat_c_result],
        }
