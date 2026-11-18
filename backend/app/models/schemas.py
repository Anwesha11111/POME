from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator


class CriterionWeights(BaseModel):
    strategic_alignment: float = Field(default=0.20, ge=0.0, le=1.0, description="Weight for strategic alignment")
    market_potential: float = Field(default=0.20, ge=0.0, le=1.0, description="Weight for market potential")
    customer_value: float = Field(default=0.15, ge=0.0, le=1.0, description="Weight for customer value")
    technical_feasibility: float = Field(default=0.15, ge=0.0, le=1.0, description="Weight for technical feasibility")
    financial_viability: float = Field(default=0.15, ge=0.0, le=1.0, description="Weight for financial viability")
    risk_adjusted_potential: float = Field(default=0.15, ge=0.0, le=1.0, description="Weight for risk-adjusted potential")

    @field_validator("strategic_alignment", "market_potential", "customer_value", 
                    "technical_feasibility", "financial_viability", "risk_adjusted_potential")
    @classmethod
    def check_weights(cls, v: float) -> float:
        if v < 0.0 or v > 1.0:
            raise ValueError("Criterion weight must be between 0.0 and 1.0")
        return v


class POSDCORBPolicies(BaseModel):
    planning_strict_dependencies: bool = Field(default=True, description="Strict predecessor enforcement in critical path")
    organizing_skill_balancing: bool = Field(default=True, description="Balance workload across skilled developers")
    staffing_allow_overtime: bool = Field(default=False, description="Allow developers to exceed max capacity with penalty")
    directing_focus_high_alignment: bool = Field(default=True, description="Prioritize high strategic alignment modules")
    coordinating_max_parallel_tasks: int = Field(default=4, ge=1, description="Max concurrent modules per phase")
    reporting_fmea_threshold: int = Field(default=120, ge=1, le=1000, description="RPN cut-off threshold for audit triggers")
    budgeting_contingency_buffer_pct: float = Field(default=0.10, ge=0.0, le=1.0, description="Financial contingency margin")


class SoftwareModule(BaseModel):
    id: str = Field(..., description="Unique module identifier (e.g. MOD-01)")
    name: str = Field(..., description="Descriptive module name")
    description: str = Field(default="", description="Detailed scope of the module")
    estimated_cost: float = Field(..., ge=0.0, description="Estimated capital expenditure/cost in USD")
    estimated_duration_days: int = Field(..., ge=1, description="Estimated duration in working days")
    deadline_day: int = Field(..., ge=1, description="Milestone deadline target day")
    
    # Multicriteria Scores [0.0 - 1.0]
    strategic_alignment: float = Field(..., ge=0.0, le=1.0)
    market_potential: float = Field(..., ge=0.0, le=1.0)
    customer_value: float = Field(..., ge=0.0, le=1.0)
    technical_feasibility: float = Field(..., ge=0.0, le=1.0)
    financial_viability: float = Field(..., ge=0.0, le=1.0)
    risk_adjusted_potential: float = Field(..., ge=0.0, le=1.0)
    
    # Dependencies & Competencies
    dependencies: List[str] = Field(default_factory=list, description="IDs of predecessor modules")
    required_skills: List[str] = Field(default_factory=list, description="Required competency tags")
    
    # FMEA (Failure Mode and Effects Analysis) [1 - 10]
    fmea_severity: int = Field(..., ge=1, le=10, description="Severity of potential failure mode")
    fmea_occurrence: int = Field(..., ge=1, le=10, description="Likelihood of failure occurrence")
    fmea_detection: int = Field(..., ge=1, le=10, description="Inability to detect failure early")
    
    # Metadata for provenance/scenario mapping
    source_origin: Optional[str] = Field(default="seeded", description="Origin: 'jira', 'seeded', or 'synthetic'")

    @property
    def rpn(self) -> int:
        """Risk Priority Number (RPN) = Severity * Occurrence * Detection (1 to 1000)"""
        return self.fmea_severity * self.fmea_occurrence * self.fmea_detection

    def calculate_composite_score(self, weights: CriterionWeights) -> float:
        return (
            self.strategic_alignment * weights.strategic_alignment +
            self.market_potential * weights.market_potential +
            self.customer_value * weights.customer_value +
            self.technical_feasibility * weights.technical_feasibility +
            self.financial_viability * weights.financial_viability +
            self.risk_adjusted_potential * weights.risk_adjusted_potential
        )


class Developer(BaseModel):
    id: str = Field(..., description="Developer ID (e.g. DEV-01)")
    name: str = Field(..., description="Full Name")
    role: str = Field(..., description="Primary engineering role")
    skills: List[str] = Field(default_factory=list, description="Technical skill capabilities")
    max_capacity_hours: float = Field(default=160.0, ge=0.0, description="Capacity per iteration/cycle")
    hourly_rate: float = Field(default=85.0, ge=0.0, description="Hourly billing rate")
    current_workload_hours: float = Field(default=0.0, ge=0.0, description="Currently committed hours")
    available: bool = Field(default=True, description="Availability status")


class ProjectConfig(BaseModel):
    total_budget: float = Field(default=500000.0, ge=0.0, description="Total project budget limit")
    target_deadline_day: int = Field(default=180, ge=1, description="Hard deadline in calendar/working days")
    criterion_weights: CriterionWeights = Field(default_factory=CriterionWeights)
    posdcorb_policies: POSDCORBPolicies = Field(default_factory=POSDCORBPolicies)


class AllocationDecision(BaseModel):
    module_id: str
    selected: bool
    assigned_developers: List[str] = Field(default_factory=list)
    start_day: int = 0
    end_day: int = 0
    allocated_cost: float = 0.0
    composite_score: float = 0.0
    rpn: int = 0
    rationale: str = ""


class ParetoPoint(BaseModel):
    solution_id: str
    total_cost: float
    total_duration_days: int
    total_strategic_value: float
    avg_risk_rpn: float
    selected_module_ids: List[str]
    is_pareto_optimal: bool = True


class CounterfactualScenario(BaseModel):
    scenario_id: str
    description: str
    modified_parameters: Dict[str, Any]
    delta_budget: float
    delta_strategic_value: float
    delta_duration_days: int
    modules_added: List[str]
    modules_removed: List[str]


class BFSReplayNode(BaseModel):
    step_id: int
    state_description: str
    current_module_id: str
    explored_branch: str
    queue_state: List[str]
    cumulative_cost: float
    cumulative_score: float
    decision_taken: str  # e.g., 'INCLUDED', 'PRUNED_BUDGET', 'PRUNED_DEPENDENCY'


class EvaluationMetrics(BaseModel):
    budget_utilization_pct: float
    time_critical_path_days: int
    schedule_variance_days: int
    aggregate_strategic_score: float
    average_rpn: float
    unassigned_skills_count: int
    developer_utilization: Dict[str, float]  # dev_id -> % utilization


class OptimizationResult(BaseModel):
    status: str  # 'OPTIMAL', 'FEASIBLE', 'INFEASIBLE'
    allocations: List[AllocationDecision]
    metrics: EvaluationMetrics
    pareto_frontier: List[ParetoPoint] = Field(default_factory=list)
    bfs_replay_trace: List[BFSReplayNode] = Field(default_factory=list)
    counterfactuals: List[CounterfactualScenario] = Field(default_factory=list)
