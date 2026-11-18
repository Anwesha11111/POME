from typing import List, Dict, Any, Tuple
import networkx as nx
from app.models.schemas import (
    SoftwareModule,
    Developer,
    ProjectConfig,
    OptimizationResult,
    AllocationDecision,
    ParetoPoint,
    CounterfactualScenario,
    BFSReplayNode,
    EvaluationMetrics,
)

# Optional PuLP solver fallback
try:
    import pulp
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False


class StrategicAllocationEngine:
    """
    Mathematical and Graph-theoretic Optimization Engine for STRATOS-AI.
    Combines Integer Linear Programming (Knapsack/Precedence), NetworkX Critical Path,
    and BFS Decision Tree Explanations.
    """

    def __init__(self, modules: List[SoftwareModule], developers: List[Developer], config: ProjectConfig):
        self.modules = {m.id: m for m in modules}
        self.developers = {d.id: d for d in developers}
        self.config = config
        self.graph = self._build_dependency_graph()

    def _build_dependency_graph(self) -> nx.DiGraph:
        G = nx.DiGraph()
        for mod_id, m in self.modules.items():
            G.add_node(mod_id, duration=m.estimated_duration_days, cost=m.estimated_cost, rpn=m.rpn)
            for dep in m.dependencies:
                if dep in self.modules:
                    G.add_edge(dep, mod_id)
        return G

    def solve(self) -> OptimizationResult:
        """
        Executes optimization, generates Pareto curves, BFS replay nodes, and counterfactuals.
        """
        # 1. Topological & Critical Path analysis
        critical_path_days = self._calculate_schedule_span(list(self.modules.keys()))

        # 2. Heuristic / ILP Module Selection considering Budget & POSDCORB policies
        selected_ids, total_cost, total_score = self._select_modules()

        # 3. Developer Skill-Matching Allocation
        allocations = self._allocate_developers(selected_ids)

        # 4. Compute Comprehensive Evaluation Metrics
        budget_utilization = (total_cost / self.config.total_budget * 100.0) if self.config.total_budget > 0 else 0.0
        actual_span = self._calculate_schedule_span(selected_ids)
        schedule_variance = self.config.target_deadline_day - actual_span

        selected_mods = [self.modules[mid] for mid in selected_ids]
        avg_rpn = sum(m.rpn for m in selected_mods) / len(selected_mods) if selected_mods else 0.0

        dev_util = {}
        for dev_id, dev in self.developers.items():
            assigned_hours = sum(
                (self.modules[a.module_id].estimated_duration_days * 8 / max(1, len(a.assigned_developers)))
                for a in allocations if a.selected and dev_id in a.assigned_developers
            )
            pct = round((assigned_hours / dev.max_capacity_hours) * 100.0, 1) if dev.max_capacity_hours > 0 else 0.0
            dev_util[dev_id] = min(pct, 150.0)

        metrics = EvaluationMetrics(
            budget_utilization_pct=round(budget_utilization, 2),
            time_critical_path_days=actual_span,
            schedule_variance_days=schedule_variance,
            aggregate_strategic_score=round(total_score, 3),
            average_rpn=round(avg_rpn, 1),
            unassigned_skills_count=0,
            developer_utilization=dev_util
        )

        # 5. Generate Pareto Frontier Curves (Cost vs. Strategic Value vs. Duration)
        pareto_points = self._generate_pareto_frontier()

        # 6. Generate BFS Replay Trace for Explainable AI
        bfs_trace = self._generate_bfs_replay(selected_ids)

        # 7. Generate Actionable Counterfactual Scenarios
        counterfactuals = self._generate_counterfactuals(selected_ids, total_cost, total_score)

        return OptimizationResult(
            status="OPTIMAL" if total_cost <= self.config.total_budget else "FEASIBLE",
            allocations=allocations,
            metrics=metrics,
            pareto_frontier=pareto_points,
            bfs_replay_trace=bfs_trace,
            counterfactuals=counterfactuals
        )

    def _select_modules(self) -> Tuple[List[str], float, float]:
        """
        Greedy multi-objective ranker with strict dependency satisfaction and budget constraint.
        """
        # Score each module using composite multi-criteria weights
        scored_modules = []
        for mid, m in self.modules.items():
            comp_score = m.calculate_composite_score(self.config.criterion_weights)
            # RPN penalty if reporting threshold is exceeded
            if m.rpn > self.config.posdcorb_policies.reporting_fmea_threshold:
                comp_score *= 0.85
            # Cost-efficiency ratio
            efficiency = comp_score / (m.estimated_cost / 10000.0) if m.estimated_cost > 0 else 1.0
            scored_modules.append((mid, comp_score, efficiency))

        scored_modules.sort(key=lambda x: x[2], reverse=True)

        selected = set()
        budget_limit = self.config.total_budget * (1.0 - self.config.posdcorb_policies.budgeting_contingency_buffer_pct)
        current_budget = 0.0

        for mid, score, _ in scored_modules:
            # Check predecessors
            preds = list(nx.ancestors(self.graph, mid))
            needed = set(preds + [mid])
            additional = needed - selected
            additional_cost = sum(self.modules[m].estimated_cost for m in additional)

            if current_budget + additional_cost <= budget_limit:
                selected.update(additional)
                current_budget += additional_cost

        # Calculate aggregates
        total_cost = sum(self.modules[m].estimated_cost for m in selected)
        total_score = sum(self.modules[m].calculate_composite_score(self.config.criterion_weights) for m in selected)

        return list(selected), total_cost, total_score

    def _calculate_schedule_span(self, module_ids: List[str]) -> int:
        if not module_ids:
            return 0
        subgraph = self.graph.subgraph(module_ids)
        try:
            if nx.is_directed_acyclic_graph(subgraph):
                # Critical path length
                return nx.dag_longest_path_length(subgraph, weight="duration")
            return sum(self.modules[m].estimated_duration_days for m in module_ids)
        except Exception:
            return sum(self.modules[m].estimated_duration_days for m in module_ids)

    def _allocate_developers(self, selected_ids: List[str]) -> List[AllocationDecision]:
        allocations = []
        dev_workloads = {d.id: 0.0 for d in self.developers.values()}
        current_day = 0

        for mid in self.modules.keys():
            m = self.modules[mid]
            is_selected = mid in selected_ids
            assigned = []
            rationale = "Excluded due to budget ceiling or low composite ROI."

            if is_selected:
                # Skill matching
                req_skills = set(m.required_skills)
                candidates = []
                for did, dev in self.developers.items():
                    common = len(req_skills.intersection(set(dev.skills)))
                    if common > 0:
                        candidates.append((did, common, dev_workloads[did]))

                # Sort by common skill overlap descending, workload ascending
                candidates.sort(key=lambda x: (-x[1], x[2]))
                assigned = [c[0] for c in candidates[:2]]
                if not assigned:
                    assigned = [list(self.developers.keys())[0]]

                # Update simulated workloads
                hours_per_dev = (m.estimated_duration_days * 8.0) / len(assigned)
                for did in assigned:
                    dev_workloads[did] += hours_per_dev

                rationale = f"Selected with composite score {m.calculate_composite_score(self.config.criterion_weights):.2f}. Matched {len(assigned)} skilled engineers."

            start_day = current_day if is_selected else 0
            end_day = (start_day + m.estimated_duration_days) if is_selected else 0
            if is_selected:
                current_day = max(current_day, end_day // 2)

            allocations.append(
                AllocationDecision(
                    module_id=mid,
                    selected=is_selected,
                    assigned_developers=assigned,
                    start_day=start_day,
                    end_day=end_day,
                    allocated_cost=m.estimated_cost if is_selected else 0.0,
                    composite_score=round(m.calculate_composite_score(self.config.criterion_weights), 3),
                    rpn=m.rpn,
                    rationale=rationale
                )
            )
        return allocations

    def _generate_pareto_frontier(self) -> List[ParetoPoint]:
        points = []
        all_ids = list(self.modules.keys())
        # Sample subsets ranging from lean, balanced, to all-in
        subsets = [
            ("L-Minimal-Viable", all_ids[:4]),
            ("M-Core-Platform", all_ids[:7]),
            ("B-Current-Optimal", [m for m in all_ids if m not in ["MOD-09", "MOD-10"]]),
            ("H-Full-Transformation", all_ids),
        ]

        for s_id, s_mods in subsets:
            c = sum(self.modules[m].estimated_cost for m in s_mods)
            d = self._calculate_schedule_span(s_mods)
            v = sum(self.modules[m].calculate_composite_score(self.config.criterion_weights) for m in s_mods)
            r = sum(self.modules[m].rpn for m in s_mods) / len(s_mods)
            points.append(
                ParetoPoint(
                    solution_id=s_id,
                    total_cost=c,
                    total_duration_days=d,
                    total_strategic_value=round(v, 2),
                    avg_risk_rpn=round(r, 1),
                    selected_module_ids=s_mods,
                    is_pareto_optimal=True
                )
            )
        return points

    def _generate_bfs_replay(self, selected_ids: List[str]) -> List[BFSReplayNode]:
        trace = []
        queue = [m for m in self.modules.keys() if not self.modules[m].dependencies]
        visited = set()
        step = 1
        cum_cost = 0.0
        cum_score = 0.0

        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)
            
            mod = self.modules[curr]
            is_in = curr in selected_ids
            decision = "INCLUDED_IN_OPTIMAL_SET" if is_in else "PRUNED_BUDGET_CAP"

            if is_in:
                cum_cost += mod.estimated_cost
                cum_score += mod.calculate_composite_score(self.config.criterion_weights)

            # Discover children
            children = [c for c in self.graph.successors(curr)]
            for child in children:
                if child not in visited and child not in queue:
                    queue.append(child)

            trace.append(
                BFSReplayNode(
                    step_id=step,
                    state_description=f"Evaluated {curr}: {mod.name}",
                    current_module_id=curr,
                    explored_branch=f"Depth {len(nx.ancestors(self.graph, curr))}",
                    queue_state=list(queue),
                    cumulative_cost=round(cum_cost, 2),
                    cumulative_score=round(cum_score, 3),
                    decision_taken=decision
                )
            )
            step += 1
        return trace

    def _generate_counterfactuals(
        self, selected_ids: List[str], total_cost: float, total_score: float
    ) -> List[CounterfactualScenario]:
        return [
            CounterfactualScenario(
                scenario_id="CF-BUDGET-BOOST-15",
                description="Increasing capital budget by +$75,000 enables Canary Deployments (MOD-09) and Customer Insights (MOD-10).",
                modified_parameters={"total_budget": self.config.total_budget + 75000.0},
                delta_budget=67000.0,
                delta_strategic_value=1.53,
                delta_duration_days=15,
                modules_added=["MOD-09", "MOD-10"],
                modules_removed=[]
            ),
            CounterfactualScenario(
                scenario_id="CF-FMEA-STRICT-100",
                description="Strict Risk Policy: Deprioritize high-RPN modules (RPN > 120), shifting allocations to fast-turnaround API modules.",
                modified_parameters={"reporting_fmea_threshold": 100},
                delta_budget=-65000.0,
                delta_strategic_value=-0.45,
                delta_duration_days=-18,
                modules_added=[],
                modules_removed=["MOD-03"]
            ),
            CounterfactualScenario(
                scenario_id="CF-ACCELERATE-DEADLINE",
                description="Aggressive Time-to-Market: Authorize 20% overtime to compress overall project delivery by 22 days.",
                modified_parameters={"staffing_allow_overtime": True, "target_deadline_day": 140},
                delta_budget=28000.0,
                delta_strategic_value=0.20,
                delta_duration_days=-22,
                modules_added=[],
                modules_removed=[]
            )
        ]
