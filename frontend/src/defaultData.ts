import { SoftwareModule, AnalyzedModule, CriterionWeights } from './types';

export const DEFAULT_RAW_MODULES: SoftwareModule[] = [
  {
    id: "MOD-01",
    name: "Cloud VPC & Infrastructure Foundation",
    description: "Multi-region AWS/Terraform VPC landing zone, transit gateway, IAM zero-trust baseline.",
    estimated_cost: 45000.0,
    estimated_duration_days: 20,
    deadline_day: 30,
    strategic_alignment: 0.95,
    market_potential: 0.70,
    customer_value: 0.80,
    technical_feasibility: 0.90,
    financial_viability: 0.85,
    risk_adjusted_potential: 0.88,
    dependencies: [],
    required_skills: ["Cloud Architecture", "Terraform", "DevOps"],
    fmea_severity: 8,
    fmea_occurrence: 3,
    fmea_detection: 3,
    rpn: 72,
    source_origin: "seeded"
  },
  {
    id: "MOD-02",
    name: "Identity & Access Management (IAM / OAuth2)",
    description: "Federated Single Sign-On, Keycloak/Okta integration, mTLS, JWT service-to-service auth.",
    estimated_cost: 38000.0,
    estimated_duration_days: 18,
    deadline_day: 45,
    strategic_alignment: 0.90,
    market_potential: 0.65,
    customer_value: 0.85,
    technical_feasibility: 0.85,
    financial_viability: 0.80,
    risk_adjusted_potential: 0.82,
    dependencies: ["MOD-01"],
    required_skills: ["Cybersecurity", "Python", "DevOps"],
    fmea_severity: 9,
    fmea_occurrence: 2,
    fmea_detection: 4,
    rpn: 72,
    source_origin: "seeded"
  },
  {
    id: "MOD-03",
    name: "Ledger Database Modernization & Migration",
    description: "Sharded Aurora PostgreSQL migration from legacy Oracle DB with real-time CDC replication.",
    estimated_cost: 65000.0,
    estimated_duration_days: 35,
    deadline_day: 80,
    strategic_alignment: 0.92,
    market_potential: 0.75,
    customer_value: 0.90,
    technical_feasibility: 0.70,
    financial_viability: 0.85,
    risk_adjusted_potential: 0.78,
    dependencies: ["MOD-01"],
    required_skills: ["Database Administration", "PostgreSQL", "Data Migration"],
    fmea_severity: 9,
    fmea_occurrence: 4,
    fmea_detection: 5,
    rpn: 180,
    source_origin: "seeded"
  },
  {
    id: "MOD-04",
    name: "Core Banking Transaction Processing Engine",
    description: "High-throughput, event-driven ledger service using Apache Kafka and FastAPI microservices.",
    estimated_cost: 80000.0,
    estimated_duration_days: 40,
    deadline_day: 110,
    strategic_alignment: 0.98,
    market_potential: 0.95,
    customer_value: 0.95,
    technical_feasibility: 0.75,
    financial_viability: 0.92,
    risk_adjusted_potential: 0.85,
    dependencies: ["MOD-02", "MOD-03"],
    required_skills: ["FastAPI", "Python", "Kafka", "Distributed Systems"],
    fmea_severity: 9,
    fmea_occurrence: 4,
    fmea_detection: 4,
    rpn: 144,
    source_origin: "seeded"
  },
  {
    id: "MOD-05",
    name: "Real-Time Fraud & Anomaly Detection Service",
    description: "Streaming machine-learning inference pipeline for instant transaction anomaly scoring.",
    estimated_cost: 55000.0,
    estimated_duration_days: 30,
    deadline_day: 125,
    strategic_alignment: 0.85,
    market_potential: 0.90,
    customer_value: 0.90,
    technical_feasibility: 0.72,
    financial_viability: 0.80,
    risk_adjusted_potential: 0.75,
    dependencies: ["MOD-04"],
    required_skills: ["Machine Learning", "Python", "Kafka", "Data Engineering"],
    fmea_severity: 8,
    fmea_occurrence: 5,
    fmea_detection: 4,
    rpn: 160,
    source_origin: "seeded"
  },
  {
    id: "MOD-06",
    name: "PCI-DSS Payment Gateway Integrations",
    description: "External payment processor hooks (Stripe, SWIFT, SEPA) with tokenized card data vaults.",
    estimated_cost: 50000.0,
    estimated_duration_days: 25,
    deadline_day: 130,
    strategic_alignment: 0.88,
    market_potential: 0.92,
    customer_value: 0.88,
    technical_feasibility: 0.80,
    financial_viability: 0.89,
    risk_adjusted_potential: 0.82,
    dependencies: ["MOD-02", "MOD-04"],
    required_skills: ["Cybersecurity", "FastAPI", "API Integration"],
    fmea_severity: 9,
    fmea_occurrence: 3,
    fmea_detection: 3,
    rpn: 81,
    source_origin: "seeded"
  },
  {
    id: "MOD-07",
    name: "Customer Self-Service Mobile & Web API",
    description: "GraphQL & REST gateways providing balances, transfers, and notifications for UI clients.",
    estimated_cost: 42000.0,
    estimated_duration_days: 22,
    deadline_day: 145,
    strategic_alignment: 0.82,
    market_potential: 0.88,
    customer_value: 0.92,
    technical_feasibility: 0.88,
    financial_viability: 0.85,
    risk_adjusted_potential: 0.84,
    dependencies: ["MOD-04", "MOD-06"],
    required_skills: ["FastAPI", "GraphQL", "Python"],
    fmea_severity: 6,
    fmea_occurrence: 3,
    fmea_detection: 3,
    rpn: 54,
    source_origin: "seeded"
  },
  {
    id: "MOD-08",
    name: "Regulatory Compliance & Audit Reporting",
    description: "SOX/GDPR/Basel-III automated reporting engine with cryptographically signed audit logs.",
    estimated_cost: 36000.0,
    estimated_duration_days: 20,
    deadline_day: 160,
    strategic_alignment: 0.91,
    market_potential: 0.60,
    customer_value: 0.70,
    technical_feasibility: 0.85,
    financial_viability: 0.75,
    risk_adjusted_potential: 0.80,
    dependencies: ["MOD-03", "MOD-04"],
    required_skills: ["Database Administration", "Python", "Data Engineering"],
    fmea_severity: 8,
    fmea_occurrence: 2,
    fmea_detection: 3,
    rpn: 48,
    source_origin: "seeded"
  },
  {
    id: "MOD-09",
    name: "Automated Canary Deployments & Chaos Mesh",
    description: "ArgoCD gitops pipeline, automated chaos engineering drills, zero-downtime rollback.",
    estimated_cost: 32000.0,
    estimated_duration_days: 18,
    deadline_day: 165,
    strategic_alignment: 0.78,
    market_potential: 0.55,
    customer_value: 0.75,
    technical_feasibility: 0.82,
    financial_viability: 0.78,
    risk_adjusted_potential: 0.86,
    dependencies: ["MOD-01", "MOD-07"],
    required_skills: ["DevOps", "Terraform", "Cloud Architecture"],
    fmea_severity: 7,
    fmea_occurrence: 3,
    fmea_detection: 3,
    rpn: 63,
    source_origin: "seeded"
  },
  {
    id: "MOD-10",
    name: "Customer Insights & Predictive Analytics Portal",
    description: "Executive dashboards, user engagement trends, and lifetime-value predictive models.",
    estimated_cost: 35000.0,
    estimated_duration_days: 20,
    deadline_day: 175,
    strategic_alignment: 0.75,
    market_potential: 0.82,
    customer_value: 0.80,
    technical_feasibility: 0.85,
    financial_viability: 0.80,
    risk_adjusted_potential: 0.79,
    dependencies: ["MOD-05", "MOD-07"],
    required_skills: ["Machine Learning", "Data Engineering", "API Integration"],
    fmea_severity: 5,
    fmea_occurrence: 3,
    fmea_detection: 3,
    rpn: 45,
    source_origin: "seeded"
  }
];

export function calculateLocalPortfolio(
  modules: SoftwareModule[],
  weights: CriterionWeights
): AnalyzedModule[] {
  const sumWeights =
    weights.strategic_alignment +
    weights.market_potential +
    weights.customer_value +
    weights.technical_feasibility +
    weights.financial_viability +
    weights.risk_adjusted_potential || 1.0;

  // First pass: compute growth and position proxies for all modules
  const rawAnalyzed = modules.map((m) => {
    const p_i =
      (weights.strategic_alignment / sumWeights) * m.strategic_alignment +
      (weights.market_potential / sumWeights) * m.market_potential +
      (weights.customer_value / sumWeights) * m.customer_value +
      (weights.technical_feasibility / sumWeights) * m.technical_feasibility +
      (weights.financial_viability / sumWeights) * m.financial_viability +
      (weights.risk_adjusted_potential / sumWeights) * m.risk_adjusted_potential;

    const growth = Number((0.5 * m.market_potential + 0.5 * m.risk_adjusted_potential).toFixed(3));
    const position = Number(
      (0.4 * m.strategic_alignment + 0.3 * m.customer_value + 0.3 * m.technical_feasibility).toFixed(3)
    );

    return { m, p_i, growth, position };
  });

  // Calculate dynamic portfolio medians so modules are distributed across all 4 quadrants
  const sortedGrowth = [...rawAnalyzed].map((x) => x.growth).sort((a, b) => a - b);
  const sortedPosition = [...rawAnalyzed].map((x) => x.position).sort((a, b) => a - b);
  const mid = Math.floor(sortedGrowth.length / 2);
  const medianGrowth = sortedGrowth.length > 0 ? sortedGrowth[mid] : 0.78;
  const medianPosition = sortedPosition.length > 0 ? sortedPosition[mid] : 0.85;

  const analyzed = rawAnalyzed.map(({ m, p_i, growth, position }) => {
    let quadrant: 'Stars' | 'Cash Cows' | 'Question Marks' | 'Dogs';
    let action: string;

    if (growth >= medianGrowth && position >= medianPosition) {
      quadrant = 'Stars';
      action = 'Protect & Prioritize (High Capital & Top Talent Allocation)';
    } else if (growth >= medianGrowth && position < medianPosition) {
      quadrant = 'Question Marks';
      action = 'Selective Investment / R&D Spike to Resolve Feasibility';
    } else if (growth < medianGrowth && position >= medianPosition) {
      quadrant = 'Cash Cows';
      action = 'Maintain Foundation with Lean Staffing';
    } else {
      quadrant = 'Dogs';
      action = 'De-scope, Defer, or Prime for Counterfactual Trade-off';
    }

    return {
      module: m,
      priority_score: Number(p_i.toFixed(3)),
      bcg_quadrant: quadrant,
      growth_proxy: growth,
      position_proxy: position,
      recommended_action: action,
      proxy_indicator_tags: [
        'Growth = f(Market, Risk-Adjusted) [Proxy]',
        'Position = f(Strategic, Customer, Feasibility) [Proxy]',
        `Source: ${m.source_origin}`
      ]
    };
  });

  analyzed.sort((a, b) => b.priority_score - a.priority_score);
  analyzed.forEach((item, index) => {
    item.strategic_rank = index + 1;
  });

  return analyzed;
}
