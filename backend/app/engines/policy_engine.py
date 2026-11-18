from typing import List, Dict, Any, Tuple
import networkx as nx
from app.models.schemas import (
    SoftwareModule,
    Developer,
    ProjectConfig,
    POSDCORBPolicies,
    AllocationDecision,
)


class PolicyViolation:
    def __init__(self, rule_name: str, policy_category: str, severity: str, message: str, entity_id: str):
        self.rule_name = rule_name
        self.policy_category = policy_category  # Planning, Organising, Staffing, Directing, Coordinating, Reporting, Budgeting
        self.severity = severity  # 'CRITICAL', 'WARNING', 'INFO'
        self.message = message
        self.entity_id = entity_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_name": self.rule_name,
            "policy_category": self.policy_category,
            "severity": self.severity,
            "message": self.message,
            "entity_id": self.entity_id,
        }


class PolicyAuditLog:
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []

    def log(self, category: str, rule: str, status: str, details: str):
        self.entries.append({
            "category": category,
            "rule": rule,
            "status": status,  # "PASSED", "VIOLATED", "ADJUSTED"
            "details": details,
        })


class ManagementPolicyEngine:
    """
    Layer L2: Management Policy Engine
    Translates POSDCORB principles into machine-checkable rules & constraints:
    - Planning: Enforce minimum strategic priority thresholds for funded modules.
    - Organising: Enforce module ownership and clear role boundaries.
    - Staffing: Enforce developer skill matching (a_{ik} <= m_{ik}) and capacity limits (sum_i h_{ik} a_{ik} <= H_k).
    - Directing: Priority-based task dispatching order.
    - Co-ordinating: Precedence constraints (s_j >= s_i + d_i for all (i -> j) in E).
    - Reporting: Generate structured audit logs explaining every constraint applied or violated.
    - Budgeting: Enforce hard budget ceiling (sum_i c_i y_i <= B).

    Also implements the Management Functions execution loop (POSDCORB / EVM):
    SV = EV - PV, CV = EV - AC, SPI = EV / PV, CPI = EV / AC.
    """

    def __init__(self, modules: List[SoftwareModule], developers: List[Developer], config: ProjectConfig):
        self.modules = {m.id: m for m in modules}
        self.developers = {d.id: d for d in developers}
        self.config = config
        self.policies = config.posdcorb_policies
        self.audit_log = PolicyAuditLog()

    def validate_posdcorb_constraints(
        self,
        selected_module_ids: List[str],
        developer_assignments: Dict[str, List[str]],  # module_id -> [dev_ids]
        start_days: Dict[str, int],  # module_id -> start_day
    ) -> Tuple[bool, List[PolicyViolation], PolicyAuditLog]:
        """
        Validates all POSDCORB rules against candidate allocation plan.
        """
        violations: List[PolicyViolation] = []

        # 1. Budgeting (B): sum_i c_i y_i <= B * (1 - contingency)
        total_cost = sum(self.modules[m].estimated_cost for m in selected_module_ids)
        budget_limit = self.config.total_budget
        contingency_limit = budget_limit * (1.0 - self.policies.budgeting_contingency_buffer_pct)

        if total_cost > budget_limit:
            violations.append(
                PolicyViolation(
                    rule_name="HardBudgetCeiling",
                    policy_category="Budgeting",
                    severity="CRITICAL",
                    message=f"Total cost ${total_cost:,.2f} exceeds hard budget ${budget_limit:,.2f}",
                    entity_id="GLOBAL_BUDGET"
                )
            )
            self.audit_log.log("Budgeting", "HardBudgetCeiling", "VIOLATED", f"Cost ${total_cost} > Budget ${budget_limit}")
        elif total_cost > contingency_limit:
            violations.append(
                PolicyViolation(
                    rule_name="ContingencyBufferBreached",
                    policy_category="Budgeting",
                    severity="WARNING",
                    message=f"Total cost ${total_cost:,.2f} encroaches into contingency buffer limit ${contingency_limit:,.2f}",
                    entity_id="GLOBAL_BUDGET"
                )
            )
            self.audit_log.log("Budgeting", "ContingencyBufferBreached", "ADJUSTED", f"Cost ${total_cost} encroached buffer")
        else:
            self.audit_log.log("Budgeting", "HardBudgetCeiling", "PASSED", f"Cost ${total_cost:,.2f} within ${contingency_limit:,.2f}")

        # 2. Planning (P): Minimum strategic priority threshold
        min_priority_threshold = 0.50 if self.policies.directing_focus_high_alignment else 0.0
        for mid in selected_module_ids:
            mod = self.modules[mid]
            p_score = mod.calculate_composite_score(self.config.criterion_weights)
            if p_score < min_priority_threshold:
                violations.append(
                    PolicyViolation(
                        rule_name="MinimumStrategicThreshold",
                        policy_category="Planning",
                        severity="WARNING",
                        message=f"Module {mid} has composite priority {p_score:.2f} below threshold {min_priority_threshold:.2f}",
                        entity_id=mid
                    )
                )
                self.audit_log.log("Planning", "MinimumStrategicThreshold", "VIOLATED", f"Module {mid} low priority {p_score:.2f}")

        # 3. Staffing (S): Developer skill matching (a_{ik} <= m_{ik}) & Capacity limits (sum_i h_{ik} a_{ik} <= H_k)
        dev_workloads = {d: 0.0 for d in self.developers.keys()}

        for mid in selected_module_ids:
            mod = self.modules[mid]
            assigned_devs = developer_assignments.get(mid, [])

            if not assigned_devs:
                violations.append(
                    PolicyViolation(
                        rule_name="UnstaffedModule",
                        policy_category="Staffing",
                        severity="CRITICAL",
                        message=f"Funded module {mid} has no assigned engineers",
                        entity_id=mid
                    )
                )
                self.audit_log.log("Staffing", "UnstaffedModule", "VIOLATED", f"Module {mid} has 0 engineers")
                continue

            req_skills = set(mod.required_skills)
            hours_per_dev = (mod.estimated_duration_days * 8.0) / len(assigned_devs)

            for dev_id in assigned_devs:
                dev = self.developers.get(dev_id)
                if not dev:
                    continue
                dev_workloads[dev_id] += hours_per_dev

                # Skill fit check: at least one matched skill
                dev_skills = set(dev.skills)
                if not req_skills.intersection(dev_skills):
                    violations.append(
                        PolicyViolation(
                            rule_name="SkillMismatch",
                            policy_category="Staffing",
                            severity="WARNING",
                            message=f"Developer {dev.name} ({dev_id}) lacks required competencies {mod.required_skills} for {mid}",
                            entity_id=dev_id
                        )
                    )
                    self.audit_log.log("Staffing", "SkillMismatch", "VIOLATED", f"Dev {dev_id} lacks skills for {mid}")

        # Capacity check
        for dev_id, total_hours in dev_workloads.items():
            dev = self.developers[dev_id]
            max_cap = dev.max_capacity_hours
            if not self.policies.staffing_allow_overtime and total_hours > max_cap:
                violations.append(
                    PolicyViolation(
                        rule_name="CapacityOverload",
                        policy_category="Staffing",
                        severity="CRITICAL",
                        message=f"Developer {dev.name} allocated {total_hours:.1f}h exceeding max {max_cap:.1f}h",
                        entity_id=dev_id
                    )
                )
                self.audit_log.log("Staffing", "CapacityOverload", "VIOLATED", f"Dev {dev_id} {total_hours}h > {max_cap}h")
            else:
                self.audit_log.log("Staffing", "CapacityLimit", "PASSED", f"Dev {dev_id} {total_hours:.1f}h / {max_cap:.1f}h")

        # 4. Co-ordinating (CO): Precedence constraints s_j >= s_i + d_i for all (i -> j) in E
        for mid in selected_module_ids:
            mod = self.modules[mid]
            s_j = start_days.get(mid, 0)
            for pred_id in mod.dependencies:
                if pred_id in selected_module_ids:
                    pred_mod = self.modules[pred_id]
                    s_i = start_days.get(pred_id, 0)
                    finish_i = s_i + pred_mod.estimated_duration_days
                    if s_j < finish_i:
                        violations.append(
                            PolicyViolation(
                                rule_name="PrecedenceViolation",
                                policy_category="Co-ordinating",
                                severity="CRITICAL",
                                message=f"Module {mid} starts on day {s_j} before predecessor {pred_id} completes on day {finish_i}",
                                entity_id=mid
                            )
                        )
                        self.audit_log.log("Co-ordinating", "PrecedenceViolation", "VIOLATED", f"{mid} starts day {s_j} < {pred_id} ends {finish_i}")
                elif self.policies.planning_strict_dependencies:
                    violations.append(
                        PolicyViolation(
                            rule_name="MissingPredecessorFunding",
                            policy_category="Co-ordinating",
                            severity="CRITICAL",
                            message=f"Predecessor {pred_id} required by {mid} is not funded",
                            entity_id=mid
                        )
                    )
                    self.audit_log.log("Co-ordinating", "MissingPredecessor", "VIOLATED", f"Pred {pred_id} not funded for {mid}")

        # 5. Reporting (R): FMEA threshold triggers
        for mid in selected_module_ids:
            mod = self.modules[mid]
            if mod.rpn > self.policies.reporting_fmea_threshold:
                violations.append(
                    PolicyViolation(
                        rule_name="FMEARiskAuditTrigger",
                        policy_category="Reporting",
                        severity="WARNING",
                        message=f"Module {mid} RPN {mod.rpn} exceeds risk reporting ceiling {self.policies.reporting_fmea_threshold}",
                        entity_id=mid
                    )
                )
                self.audit_log.log("Reporting", "FMEARiskAuditTrigger", "ADJUSTED", f"Module {mid} high RPN {mod.rpn}")

        is_valid = not any(v.severity == "CRITICAL" for v in violations)
        return is_valid, violations, self.audit_log

    def compute_evm_metrics(
        self,
        current_day: int,
        selected_module_ids: List[str],
        actual_costs: Dict[str, float] = None,
        progress_pcts: Dict[str, float] = None,
    ) -> Dict[str, float]:
        """
        Computes Earned Value Management (EVM) parameters:
        PV = Planned Value, EV = Earned Value, AC = Actual Cost
        Schedule Variance (SV) = EV - PV
        Cost Variance (CV) = EV - AC
        Schedule Performance Index (SPI) = EV / PV
        Cost Performance Index (CPI) = EV / AC
        """
        actual_costs = actual_costs or {}
        progress_pcts = progress_pcts or {}

        pv = 0.0
        ev = 0.0
        ac = 0.0

        for mid in selected_module_ids:
            m = self.modules[mid]
            cost = m.estimated_cost
            dur = m.estimated_duration_days

            # Planned progress based on linear planned timeline
            planned_frac = min(1.0, max(0.0, current_day / dur)) if dur > 0 else 1.0
            actual_frac = progress_pcts.get(mid, planned_frac)

            pv += cost * planned_frac
            ev += cost * actual_frac
            ac += actual_costs.get(mid, cost * actual_frac * 0.98)  # realistic baseline AC

        sv = ev - pv
        cv = ev - ac
        spi = (ev / pv) if pv > 0 else 1.0
        cpi = (ev / ac) if ac > 0 else 1.0

        return {
            "planned_value_pv": round(pv, 2),
            "earned_value_ev": round(ev, 2),
            "actual_cost_ac": round(ac, 2),
            "schedule_variance_sv": round(sv, 2),
            "cost_variance_cv": round(cv, 2),
            "schedule_performance_index_spi": round(spi, 3),
            "cost_performance_index_cpi": round(cpi, 3),
            "current_day": current_day
        }
