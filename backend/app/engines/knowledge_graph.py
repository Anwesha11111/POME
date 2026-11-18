from typing import List, Dict, Any, Optional
import networkx as nx
from app.models.schemas import SoftwareModule, Developer, ProjectConfig


class KnowledgeGraphEngine:
    """
    Layer L4: Knowledge Graph & Explainable Decision Replay
    Constructs a directed NetworkX graph connecting:
    - Triggers (e.g., 'Budget Cut -25%', 'Lead Developer Unavailable')
    - PolicyRules (POSDCORB Governance constraints)
    - Developers (Engineers & competencies)
    - Modules (Software system building blocks)
    - Tasks (Work breakdown packages)
    - Risks (FMEA Failure modes)
    - Milestones (Project delivery target dates)
    - Recommendations (Strategic recourse alternatives)

    Supported typed causal edges:
    - requires_skill
    - blocks
    - funded_by
    - governed_by_policy
    - gates_milestone
    - triggers_reallocation
    """

    def __init__(self, modules: List[SoftwareModule], developers: List[Developer], config: ProjectConfig):
        self.modules = {m.id: m for m in modules}
        self.developers = {d.id: d for d in developers}
        self.config = config
        self.graph = nx.DiGraph()
        self._build_knowledge_graph()

    def _build_knowledge_graph(self):
        # 1. Add Policy Rule Nodes (POSDCORB)
        policies = [
            ("POL-BUDGET", "PolicyRule", "Hard Budget Ceiling (B)", "Ensures total allocation cost does not breach approved budget."),
            ("POL-STAFF", "PolicyRule", "Competency Matching & Capacity (S)", "Enforces developer skill-fit and prevents weekly overload."),
            ("POL-PRECEDENCE", "PolicyRule", "Strict Dependency Sequencing (CO)", "Requires all architectural predecessors to be funded and completed."),
            ("POL-FMEA", "PolicyRule", "Risk Priority Audit Ceiling (R)", "Mandates executive review for components with RPN > 120."),
        ]
        for p_id, p_type, label, desc in policies:
            self.graph.add_node(p_id, node_type=p_type, label=label, description=desc)

        # 2. Add Developer Nodes
        for d_id, dev in self.developers.items():
            self.graph.add_node(
                d_id,
                node_type="Developer",
                label=dev.name,
                role=dev.role,
                skills=dev.skills,
                capacity=dev.max_capacity_hours,
            )

        # 3. Add Module & Risk Nodes
        for m_id, mod in self.modules.items():
            self.graph.add_node(
                m_id,
                node_type="Module",
                label=mod.name,
                cost=mod.estimated_cost,
                duration=mod.estimated_duration_days,
                strategic_alignment=mod.strategic_alignment,
                rpn=mod.rpn,
            )
            # Edge: governed_by_policy
            self.graph.add_edge(m_id, "POL-BUDGET", edge_type="governed_by_policy")
            if mod.rpn > 120:
                self.graph.add_edge(m_id, "POL-FMEA", edge_type="governed_by_policy")

            # Add associated Risk node
            risk_id = f"RISK-{m_id}"
            self.graph.add_node(
                risk_id,
                node_type="Risk",
                label=f"Risk: {mod.name}",
                rpn=mod.rpn,
                severity=mod.fmea_severity,
                occurrence=mod.fmea_occurrence,
                detection=mod.fmea_detection,
            )
            self.graph.add_edge(risk_id, m_id, edge_type="threatens_module")

            # Precedence edges: blocks
            for dep in mod.dependencies:
                if dep in self.modules:
                    self.graph.add_edge(dep, m_id, edge_type="blocks")

            # Skill matching edges
            for d_id, dev in self.developers.items():
                if any(skill in dev.skills for skill in mod.required_skills):
                    self.graph.add_edge(d_id, m_id, edge_type="requires_skill")

        # 4. Add Milestone Nodes
        milestones = [
            ("MS-FOUNDATION", "Milestone", "Phase 1: Cloud & Security Baseline", 45),
            ("MS-CORE-LEDGER", "Milestone", "Phase 2: Core Ledger & Transactions", 110),
            ("MS-GO-LIVE", "Milestone", "Phase 3: Production Customer Go-Live", 170),
        ]
        for ms_id, ms_type, label, target_day in milestones:
            self.graph.add_node(ms_id, node_type=ms_type, label=label, target_day=target_day)

        # Link modules to milestones
        self.graph.add_edge("MOD-01", "MS-FOUNDATION", edge_type="gates_milestone")
        self.graph.add_edge("MOD-02", "MS-FOUNDATION", edge_type="gates_milestone")
        self.graph.add_edge("MOD-04", "MS-CORE-LEDGER", edge_type="gates_milestone")
        self.graph.add_edge("MOD-07", "MS-GO-LIVE", edge_type="gates_milestone")

    def perform_bfs_decision_replay(self, trigger_id: str = "TRIGGER-BUDGET-CUT") -> Dict[str, Any]:
        """
        Executes Breadth-First Search (BFS) starting from a Trigger event:
        - Depth 0: Trigger Event
        - Depth 1: Affected Module(s)
        - Depth 2: Blocked Dependent Task / Modules
        - Depth 3: Milestone at Risk
        - Depth 4: Recommended Alternative
        """
        # Ensure trigger node exists
        trigger_meta = {
            "TRIGGER-BUDGET-CUT": ("Trigger", "Budget Cut (-25% / -$112,500)", "MOD-09"),
            "TRIGGER-DEV-OUTAGE": ("Trigger", "Principal Architect Unavailable (Dr. Rostova)", "MOD-01"),
            "TRIGGER-DEADLINE-PULL": ("Trigger", "Executive Mandate: Accelerate Launch by 20 Days", "MOD-07"),
        }

        t_type, t_label, target_module = trigger_meta.get(
            trigger_id, ("Trigger", f"Ad-hoc Shock: {trigger_id}", "MOD-04")
        )

        self.graph.add_node(trigger_id, node_type=t_type, label=t_label)
        self.graph.add_edge(trigger_id, target_module, edge_type="triggers_reallocation")

        # Recommendation node at Depth 4
        rec_id = f"REC-{trigger_id}"
        rec_label = "Activate Strategy A (De-scope lower priority modules & reallocate talent)"
        self.graph.add_node(rec_id, node_type="Recommendation", label=rec_label)

        # BFS level-by-level traversal
        visited = set()
        queue = [(trigger_id, 0)]
        depth_levels: Dict[int, List[Dict[str, Any]]] = {0: [], 1: [], 2: [], 3: [], 4: []}
        trace_edges: List[Dict[str, Any]] = []

        while queue:
            node, depth = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)

            node_attrs = self.graph.nodes[node]
            depth_levels.setdefault(depth, []).append({
                "id": node,
                "label": node_attrs.get("label", node),
                "node_type": node_attrs.get("node_type", "Unknown"),
                "depth": depth,
                "description": node_attrs.get("description", ""),
            })

            if depth < 3:
                for neighbor in self.graph.neighbors(node):
                    if neighbor not in visited:
                        edge_data = self.graph.get_edge_data(node, neighbor, default={})
                        trace_edges.append({
                            "source": node,
                            "target": neighbor,
                            "edge_type": edge_data.get("edge_type", "causal_link"),
                            "depth": depth + 1,
                        })
                        queue.append((neighbor, depth + 1))
            elif depth == 3:
                # Direct causal link to Recommendation
                self.graph.add_edge(node, rec_id, edge_type="triggers_recommendation")
                trace_edges.append({
                    "source": node,
                    "target": rec_id,
                    "edge_type": "triggers_recommendation",
                    "depth": 4,
                })
                if rec_id not in visited:
                    depth_levels[4].append({
                        "id": rec_id,
                        "label": rec_label,
                        "node_type": "Recommendation",
                        "depth": 4,
                        "description": "Preserves core architecture while restoring project feasibility.",
                    })
                    visited.add(rec_id)

        # Generate step-by-step natural language explanation
        explanation_steps = [
            f"Step 0: System injected perturbation '{t_label}'.",
            f"Step 1: Impact propagates directly to component '{target_module}' ({self.modules.get(target_module, SoftwareModule(id='x', name=target_module, estimated_cost=0, estimated_duration_days=1, deadline_day=1, strategic_alignment=0, market_potential=0, customer_value=0, technical_feasibility=0, financial_viability=0, risk_adjusted_potential=0, fmea_severity=1, fmea_occurrence=1, fmea_detection=1)).name}).",
            f"Step 2: Precedence dependency graph triggers blockage on downstream components that require {target_module} as an architectural prerequisite.",
            "Step 3: Critical path slip propagates to project delivery milestones, threatening scheduled Go-Live.",
            f"Step 4: Decision intelligence recommends {rec_label}.",
        ]

        return {
            "trigger_id": trigger_id,
            "trigger_label": t_label,
            "depth_levels": depth_levels,
            "trace_edges": trace_edges,
            "explanation_steps": explanation_steps,
            "total_nodes_traversed": len(visited),
        }

    def export_graph_json(self) -> Dict[str, Any]:
        """Serializes entire Knowledge Graph into React Flow compatible node-link schema."""
        nodes = []
        for n_id, attrs in self.graph.nodes(data=True):
            nodes.append({
                "id": n_id,
                "data": {"label": attrs.get("label", n_id), **attrs},
                "type": attrs.get("node_type", "default"),
            })

        edges = []
        for u, v, attrs in self.graph.edges(data=True):
            edges.append({
                "id": f"e-{u}-{v}",
                "source": u,
                "target": v,
                "label": attrs.get("edge_type", ""),
                "animated": attrs.get("edge_type") == "triggers_reallocation",
            })

        return {"nodes": nodes, "edges": edges}
