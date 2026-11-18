export interface SoftwareModule {
  id: string;
  name: string;
  description: string;
  estimated_cost: number;
  estimated_duration_days: number;
  deadline_day: number;
  strategic_alignment: number;
  market_potential: number;
  customer_value: number;
  technical_feasibility: number;
  financial_viability: number;
  risk_adjusted_potential: number;
  dependencies: string[];
  required_skills: string[];
  fmea_severity: number;
  fmea_occurrence: number;
  fmea_detection: number;
  source_origin?: string;
  rpn?: number;
}

export interface Developer {
  id: string;
  name: string;
  role: string;
  skills: string[];
  max_capacity_hours: number;
  hourly_rate: number;
  current_workload_hours: number;
  available: boolean;
}

export interface CriterionWeights {
  strategic_alignment: number;
  market_potential: number;
  customer_value: number;
  technical_feasibility: number;
  financial_viability: number;
  risk_adjusted_potential: number;
}

export interface POSDCORBPolicies {
  planning_strict_dependencies: boolean;
  organizing_skill_balancing: boolean;
  staffing_allow_overtime: boolean;
  directing_focus_high_alignment: boolean;
  coordinating_max_parallel_tasks: number;
  reporting_fmea_threshold: number;
  budgeting_contingency_buffer_pct: number;
}

export interface ProjectConfig {
  total_budget: number;
  target_deadline_day: number;
  criterion_weights: CriterionWeights;
  posdcorb_policies: POSDCORBPolicies;
}

export interface AnalyzedModule {
  module: SoftwareModule;
  priority_score: number;
  bcg_quadrant: 'Stars' | 'Cash Cows' | 'Question Marks' | 'Dogs';
  growth_proxy: number;
  position_proxy: number;
  recommended_action: string;
  proxy_indicator_tags: string[];
  strategic_rank?: number;
}

export interface ParetoPoint {
  solution_id: string;
  total_cost: number;
  total_duration_days: number;
  total_strategic_value: number;
  avg_risk_rpn: number;
  selected_module_ids: string[];
  is_pareto_optimal: boolean;
}

export interface CounterfactualStrategy {
  strategy_id: string;
  name: string;
  description: string;
  total_cost: number;
  total_duration_days: number;
  strategic_value_retained_pct: number;
  avg_risk_rpn: number;
  is_feasible: boolean;
  pmes_score: number;
  modules_retained: string[];
  modules_deferred: string[];
  policy_violations_count: number;
  tradeoff_verdict: string;
}

export interface BenchmarkResult {
  baseline_id: string;
  name: string;
  description: string;
  resource_utilization_pct: number;
  budget_adherence_pct: number;
  schedule_feasibility_pct: number;
  strategic_alignment_score: number;
  average_rpn_risk: number;
  constraint_violations_count: number;
  explanation_path_completeness_pct: number;
  pmes_score: number;
  modules_selected_count: number;
}
