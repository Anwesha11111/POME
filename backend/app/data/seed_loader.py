import json
import csv
import os
from typing import List, Dict, Any, Tuple
from app.models.schemas import SoftwareModule, Developer, ProjectConfig

# Realistic Default Dataset: Enterprise FinTech Cloud Migration
# 10 interdependent modules, 8 developers with diverse skills, realistic costs, durations, and FMEA scores.

DEFAULT_MODULES: List[Dict[str, Any]] = [
    {
        "id": "MOD-01",
        "name": "Cloud VPC & Infrastructure Foundation",
        "description": "Multi-region AWS/Terraform VPC landing zone, transit gateway, IAM zero-trust baseline.",
        "estimated_cost": 45000.0,
        "estimated_duration_days": 20,
        "deadline_day": 30,
        "strategic_alignment": 0.95,
        "market_potential": 0.70,
        "customer_value": 0.80,
        "technical_feasibility": 0.90,
        "financial_viability": 0.85,
        "risk_adjusted_potential": 0.88,
        "dependencies": [],
        "required_skills": ["Cloud Architecture", "Terraform", "DevOps"],
        "fmea_severity": 8,
        "fmea_occurrence": 3,
        "fmea_detection": 3,
        "source_origin": "seeded"
    },
    {
        "id": "MOD-02",
        "name": "Identity & Access Management (IAM / OAuth2)",
        "description": "Federated Single Sign-On, Keycloak/Okta integration, mTLS, JWT service-to-service auth.",
        "estimated_cost": 38000.0,
        "estimated_duration_days": 18,
        "deadline_day": 45,
        "strategic_alignment": 0.90,
        "market_potential": 0.65,
        "customer_value": 0.85,
        "technical_feasibility": 0.85,
        "financial_viability": 0.80,
        "risk_adjusted_potential": 0.82,
        "dependencies": ["MOD-01"],
        "required_skills": ["Cybersecurity", "Python", "DevOps"],
        "fmea_severity": 9,
        "fmea_occurrence": 2,
        "fmea_detection": 4,
        "source_origin": "seeded"
    },
    {
        "id": "MOD-03",
        "name": "Ledger Database Modernization & Migration",
        "description": "Sharded Aurora PostgreSQL migration from legacy Oracle DB with real-time CDC replication.",
        "estimated_cost": 65000.0,
        "estimated_duration_days": 35,
        "deadline_day": 80,
        "strategic_alignment": 0.92,
        "market_potential": 0.75,
        "customer_value": 0.90,
        "technical_feasibility": 0.70,
        "financial_viability": 0.85,
        "risk_adjusted_potential": 0.78,
        "dependencies": ["MOD-01"],
        "required_skills": ["Database Administration", "PostgreSQL", "Data Migration"],
        "fmea_severity": 9,
        "fmea_occurrence": 4,
        "fmea_detection": 5,
        "source_origin": "seeded"
    },
    {
        "id": "MOD-04",
        "name": "Core Banking Transaction Processing Engine",
        "description": "High-throughput, event-driven ledger service using Apache Kafka and FastAPI microservices.",
        "estimated_cost": 80000.0,
        "estimated_duration_days": 40,
        "deadline_day": 110,
        "strategic_alignment": 0.98,
        "market_potential": 0.95,
        "customer_value": 0.95,
        "technical_feasibility": 0.75,
        "financial_viability": 0.92,
        "risk_adjusted_potential": 0.85,
        "dependencies": ["MOD-02", "MOD-03"],
        "required_skills": ["FastAPI", "Python", "Kafka", "Distributed Systems"],
        "fmea_severity": 9,
        "fmea_occurrence": 4,
        "fmea_detection": 4,
        "source_origin": "seeded"
    },
    {
        "id": "MOD-05",
        "name": "Real-Time Fraud & Anomaly Detection Service",
        "description": "Streaming machine-learning inference pipeline for instant transaction anomaly scoring.",
        "estimated_cost": 55000.0,
        "estimated_duration_days": 30,
        "deadline_day": 125,
        "strategic_alignment": 0.85,
        "market_potential": 0.90,
        "customer_value": 0.90,
        "technical_feasibility": 0.72,
        "financial_viability": 0.80,
        "risk_adjusted_potential": 0.75,
        "dependencies": ["MOD-04"],
        "required_skills": ["Machine Learning", "Python", "Kafka", "Data Engineering"],
        "fmea_severity": 8,
        "fmea_occurrence": 5,
        "fmea_detection": 4,
        "source_origin": "seeded"
    },
    {
        "id": "MOD-06",
        "name": "PCI-DSS Payment Gateway Integrations",
        "description": "External payment processor hooks (Stripe, SWIFT, SEPA) with tokenized card data vaults.",
        "estimated_cost": 50000.0,
        "estimated_duration_days": 25,
        "deadline_day": 130,
        "strategic_alignment": 0.88,
        "market_potential": 0.92,
        "customer_value": 0.88,
        "technical_feasibility": 0.80,
        "financial_viability": 0.89,
        "risk_adjusted_potential": 0.82,
        "dependencies": ["MOD-02", "MOD-04"],
        "required_skills": ["Cybersecurity", "FastAPI", "API Integration"],
        "fmea_severity": 9,
        "fmea_occurrence": 3,
        "fmea_detection": 3,
        "source_origin": "seeded"
    },
    {
        "id": "MOD-07",
        "name": "Customer Self-Service Mobile & Web API",
        "description": "GraphQL & REST gateways providing balances, transfers, and notifications for UI clients.",
        "estimated_cost": 42000.0,
        "estimated_duration_days": 22,
        "deadline_day": 145,
        "strategic_alignment": 0.82,
        "market_potential": 0.88,
        "customer_value": 0.92,
        "technical_feasibility": 0.88,
        "financial_viability": 0.85,
        "risk_adjusted_potential": 0.84,
        "dependencies": ["MOD-04", "MOD-06"],
        "required_skills": ["FastAPI", "GraphQL", "Python"],
        "fmea_severity": 6,
        "fmea_occurrence": 3,
        "fmea_detection": 3,
        "source_origin": "seeded"
    },
    {
        "id": "MOD-08",
        "name": "Regulatory Compliance & Audit Reporting",
        "description": "SOX/GDPR/Basel-III automated reporting engine with cryptographically signed audit logs.",
        "estimated_cost": 36000.0,
        "estimated_duration_days": 20,
        "deadline_day": 160,
        "strategic_alignment": 0.91,
        "market_potential": 0.60,
        "customer_value": 0.70,
        "technical_feasibility": 0.85,
        "financial_viability": 0.75,
        "risk_adjusted_potential": 0.80,
        "dependencies": ["MOD-03", "MOD-04"],
        "required_skills": ["Database Administration", "Python", "Data Engineering"],
        "fmea_severity": 8,
        "fmea_occurrence": 2,
        "fmea_detection": 3,
        "source_origin": "seeded"
    },
    {
        "id": "MOD-09",
        "name": "Automated Canary Deployments & Chaos Mesh",
        "description": "ArgoCD gitops pipeline, automated chaos engineering drills, zero-downtime rollback.",
        "estimated_cost": 32000.0,
        "estimated_duration_days": 18,
        "deadline_day": 165,
        "strategic_alignment": 0.78,
        "market_potential": 0.55,
        "customer_value": 0.75,
        "technical_feasibility": 0.82,
        "financial_viability": 0.78,
        "risk_adjusted_potential": 0.86,
        "dependencies": ["MOD-01", "MOD-07"],
        "required_skills": ["DevOps", "Terraform", "Cloud Architecture"],
        "fmea_severity": 7,
        "fmea_occurrence": 3,
        "fmea_detection": 3,
        "source_origin": "seeded"
    },
    {
        "id": "MOD-10",
        "name": "Customer Insights & Predictive Analytics Portal",
        "description": "Executive dashboards, user engagement trends, and lifetime-value predictive models.",
        "estimated_cost": 35000.0,
        "estimated_duration_days": 20,
        "deadline_day": 175,
        "strategic_alignment": 0.75,
        "market_potential": 0.82,
        "customer_value": 0.80,
        "technical_feasibility": 0.85,
        "financial_viability": 0.80,
        "risk_adjusted_potential": 0.79,
        "dependencies": ["MOD-05", "MOD-07"],
        "required_skills": ["Machine Learning", "Data Engineering", "API Integration"],
        "fmea_severity": 5,
        "fmea_occurrence": 3,
        "fmea_detection": 3,
        "source_origin": "seeded"
    }
]

DEFAULT_DEVELOPERS: List[Dict[str, Any]] = [
    {
        "id": "DEV-01",
        "name": "Dr. Elena Rostova",
        "role": "Principal Cloud Architect",
        "skills": ["Cloud Architecture", "Terraform", "DevOps", "Distributed Systems"],
        "max_capacity_hours": 160.0,
        "hourly_rate": 125.0,
        "current_workload_hours": 0.0,
        "available": True
    },
    {
        "id": "DEV-02",
        "name": "Marcus Vance",
        "role": "Lead Security Engineer",
        "skills": ["Cybersecurity", "API Integration", "Python", "DevOps"],
        "max_capacity_hours": 160.0,
        "hourly_rate": 115.0,
        "current_workload_hours": 0.0,
        "available": True
    },
    {
        "id": "DEV-03",
        "name": "Amina Al-Mansoor",
        "role": "Senior Database Engineer",
        "skills": ["Database Administration", "PostgreSQL", "Data Migration", "Data Engineering"],
        "max_capacity_hours": 160.0,
        "hourly_rate": 110.0,
        "current_workload_hours": 0.0,
        "available": True
    },
    {
        "id": "DEV-04",
        "name": "Kai Chen",
        "role": "Senior Backend Architect",
        "skills": ["FastAPI", "Python", "Kafka", "Distributed Systems"],
        "max_capacity_hours": 160.0,
        "hourly_rate": 110.0,
        "current_workload_hours": 0.0,
        "available": True
    },
    {
        "id": "DEV-05",
        "name": "Sofia Lindqvist",
        "role": "Staff ML Engineer",
        "skills": ["Machine Learning", "Python", "Kafka", "Data Engineering"],
        "max_capacity_hours": 160.0,
        "hourly_rate": 115.0,
        "current_workload_hours": 0.0,
        "available": True
    },
    {
        "id": "DEV-06",
        "name": "Tariq Washington",
        "role": "Full Stack API Engineer",
        "skills": ["FastAPI", "GraphQL", "Python", "API Integration"],
        "max_capacity_hours": 160.0,
        "hourly_rate": 95.0,
        "current_workload_hours": 0.0,
        "available": True
    },
    {
        "id": "DEV-07",
        "name": "Nadia O'Connor",
        "role": "Senior DevOps / SRE",
        "skills": ["DevOps", "Terraform", "Cloud Architecture", "Distributed Systems"],
        "max_capacity_hours": 160.0,
        "hourly_rate": 105.0,
        "current_workload_hours": 0.0,
        "available": True
    },
    {
        "id": "DEV-08",
        "name": "Hiroshi Tanaka",
        "role": "Data & Compliance Engineer",
        "skills": ["Data Engineering", "PostgreSQL", "Python", "Database Administration"],
        "max_capacity_hours": 160.0,
        "hourly_rate": 90.0,
        "current_workload_hours": 0.0,
        "available": True
    }
]


class SeedDataLoader:
    """
    Manages seeding, Jira CSV/JSON dataset ingestion, and domain enrichment.
    """

    @classmethod
    def get_default_dataset(cls) -> Tuple[List[SoftwareModule], List[Developer], ProjectConfig]:
        """Returns the high-fidelity FinTech Cloud Migration dataset."""
        modules = [SoftwareModule(**m) for m in DEFAULT_MODULES]
        developers = [Developer(**d) for d in DEFAULT_DEVELOPERS]
        config = ProjectConfig(
            total_budget=450000.0,
            target_deadline_day=170
        )
        return modules, developers, config

    @classmethod
    def load_from_jira_json(cls, raw_json_data: List[Dict[str, Any]]) -> List[SoftwareModule]:
        """
        Parses Public Jira Dataset export JSON (Epics/Issues/Components).
        Supplements missing strategic/market scores using conservative deterministic heuristics.
        """
        modules = []
        for idx, item in enumerate(raw_json_data, start=1):
            key = item.get("key", f"JIRA-{idx}")
            fields = item.get("fields", item)
            summary = fields.get("summary", f"Module {key}")
            desc = fields.get("description", "") or summary
            
            # Map time tracking / story points to estimated cost & duration
            time_spent = fields.get("timespent") or fields.get("aggregatetimespent") or 288000 # default 10 days in secs
            duration_days = max(5, int(time_spent / (8 * 3600)))
            cost = duration_days * 8 * 95.0  # Approx $95/hr standard
            
            # Extract dependencies from issue links
            issuelinks = fields.get("issuelinks", [])
            deps = []
            for link in issuelinks:
                outward = link.get("outwardIssue")
                if outward and link.get("type", {}).get("name") in ["Blocks", "Depends", "Dependency"]:
                    deps.append(outward.get("key"))
            
            # Extract skills from components/labels
            labels = fields.get("labels", [])
            components = [c.get("name") for c in fields.get("components", []) if isinstance(c, dict)]
            skills = list(set(labels + components))
            if not skills:
                skills = ["General Engineering", "Python"]

            # Scenario-based synthetic augmentation for missing indicators
            priority = str(fields.get("priority", {}).get("name", "Medium")).lower()
            strat_val = 0.9 if "high" in priority or "blocker" in priority else (0.6 if "low" in priority else 0.75)
            
            module = SoftwareModule(
                id=key,
                name=summary,
                description=desc[:200],
                estimated_cost=round(cost, 2),
                estimated_duration_days=duration_days,
                deadline_day=duration_days * 2 + 10,
                strategic_alignment=strat_val,
                market_potential=fields.get("customfield_market", 0.70),
                customer_value=fields.get("customfield_custval", 0.75),
                technical_feasibility=fields.get("customfield_feasibility", 0.80),
                financial_viability=fields.get("customfield_financial", 0.75),
                risk_adjusted_potential=round(strat_val * 0.9, 2),
                dependencies=deps,
                required_skills=skills[:4],
                fmea_severity=fields.get("customfield_sev", 6),
                fmea_occurrence=fields.get("customfield_occ", 4),
                fmea_detection=fields.get("customfield_det", 3),
                source_origin="jira"
            )
            modules.append(module)
        return modules

    @classmethod
    def load_from_jira_csv(cls, csv_text: str) -> List[SoftwareModule]:
        """
        Parses Jira export CSV into SoftwareModule instances.
        """
        modules = []
        reader = csv.DictReader(csv_text.strip().splitlines())
        for idx, row in enumerate(reader, start=1):
            key = row.get("Issue key") or row.get("Key") or f"JIRA-{idx}"
            summary = row.get("Summary") or f"Module {key}"
            desc = row.get("Description") or summary
            
            # Duration and cost calculation
            hours_str = row.get("Original Estimate") or row.get("Time Spent") or "80"
            try:
                hours = float(hours_str) if hours_str.replace(".", "", 1).isdigit() else 80.0
            except ValueError:
                hours = 80.0
            duration_days = max(3, int(hours / 8))
            cost = duration_days * 8 * 95.0

            raw_deps = row.get("Outward issue link (Blocks)") or row.get("Dependencies") or ""
            deps = [d.strip() for d in raw_deps.split(",") if d.strip()]

            skills_raw = row.get("Components") or row.get("Labels") or "Backend"
            skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

            strat_score = float(row.get("Strategic Alignment", 0.75))
            
            module = SoftwareModule(
                id=key,
                name=summary,
                description=desc[:200],
                estimated_cost=cost,
                estimated_duration_days=duration_days,
                deadline_day=duration_days * 2 + 14,
                strategic_alignment=strat_score,
                market_potential=float(row.get("Market Potential", 0.70)),
                customer_value=float(row.get("Customer Value", 0.75)),
                technical_feasibility=float(row.get("Technical Feasibility", 0.80)),
                financial_viability=float(row.get("Financial Viability", 0.75)),
                risk_adjusted_potential=float(row.get("Risk Adjusted", 0.72)),
                dependencies=deps,
                required_skills=skills,
                fmea_severity=int(row.get("FMEA Severity", 5)),
                fmea_occurrence=int(row.get("FMEA Occurrence", 4)),
                fmea_detection=int(row.get("FMEA Detection", 3)),
                source_origin="jira_csv"
            )
            modules.append(module)
        return modules
