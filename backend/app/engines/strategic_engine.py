import numpy as np
from typing import List, Dict, Any, Tuple
from app.models.schemas import SoftwareModule, CriterionWeights

CRITERIA_KEYS = [
    "strategic_alignment",
    "market_potential",
    "customer_value",
    "technical_feasibility",
    "financial_viability",
    "risk_adjusted_potential",
]

# Random Index (RI) lookup table for Saaty's AHP (n = 1..10)
RI_TABLE = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
}


class StrategicPrioritisationEngine:
    """
    Layer L1: Strategic Prioritisation Engine
    - Multi-criteria priority score P_i = sum_j (w_j * x_{ij}) where sum_j w_j = 1
    - Analytic Hierarchy Process (AHP) pairwise comparison calculator with Consistency Ratio (CR < 0.10)
    - BCG-inspired quadrant classification (Stars, Cash Cows, Question Marks, Dogs) with tagged proxy indicators
    """

    @classmethod
    def calculate_priority_score(cls, module: SoftwareModule, weights: CriterionWeights) -> float:
        """
        Calculates P_i = sum_j (w_j * x_{ij})
        Subject to sum_j w_j = 1
        """
        w_sum = (
            weights.strategic_alignment
            + weights.market_potential
            + weights.customer_value
            + weights.technical_feasibility
            + weights.financial_viability
            + weights.risk_adjusted_potential
        )
        if w_sum <= 0:
            w_sum = 1.0

        p_i = (
            (weights.strategic_alignment / w_sum) * module.strategic_alignment
            + (weights.market_potential / w_sum) * module.market_potential
            + (weights.customer_value / w_sum) * module.customer_value
            + (weights.technical_feasibility / w_sum) * module.technical_feasibility
            + (weights.financial_viability / w_sum) * module.financial_viability
            + (weights.risk_adjusted_potential / w_sum) * module.risk_adjusted_potential
        )
        return round(float(p_i), 4)

    @classmethod
    def compute_ahp_weights(cls, pairwise_matrix: List[List[float]]) -> Dict[str, Any]:
        """
        Derives weights w_j using Saaty's Analytic Hierarchy Process (principal eigenvector method)
        and computes the Consistency Ratio (CR).
        Validates CR < 0.10 for acceptable consistency.
        """
        matrix = np.array(pairwise_matrix, dtype=float)
        n = matrix.shape[0]

        if matrix.shape[0] != matrix.shape[1]:
            raise ValueError("Pairwise comparison matrix must be square (n x n)")

        # Eigenvalue and eigenvector calculation
        eig_vals, eig_vecs = np.linalg.eig(matrix)
        max_idx = int(np.argmax(np.real(eig_vals)))
        max_eig_val = float(np.real(eig_vals[max_idx]))
        principal_vector = np.real(eig_vecs[:, max_idx])

        # Normalize principal eigenvector to sum to 1.0
        weights = principal_vector / np.sum(principal_vector)
        weights = np.maximum(weights, 0.0)  # non-negative
        weights = weights / np.sum(weights)

        # Consistency Index (CI) and Consistency Ratio (CR)
        if n > 2:
            ci = (max_eig_val - n) / (n - 1)
            ri = RI_TABLE.get(n, 1.49)
            cr = ci / ri if ri > 0 else 0.0
        else:
            ci = 0.0
            cr = 0.0

        weight_dict = {}
        for idx, key in enumerate(CRITERIA_KEYS[:n]):
            weight_dict[key] = round(float(weights[idx]), 4)

        return {
            "weights": weight_dict,
            "lambda_max": round(max_eig_val, 4),
            "consistency_index": round(float(ci), 4),
            "consistency_ratio": round(float(cr), 4),
            "is_consistent": bool(cr < 0.10),
            "dimension": n,
        }

    @classmethod
    def classify_bcg_quadrant(
        cls, module: SoftwareModule, median_growth: float = 0.70, median_position: float = 0.70
    ) -> Dict[str, Any]:
        """
        Classifies module into BCG-inspired quadrant:
        - Growth Potential (Y-axis proxy): 0.5 * market_potential + 0.5 * risk_adjusted_potential
        - Relative Position / Competitiveness (X-axis proxy): 0.4 * strategic_alignment + 0.3 * customer_value + 0.3 * technical_feasibility
        
        Quadrants:
        - Stars: High Growth, High Position (Strategic flagships requiring aggressive resource allocation)
        - Question Marks: High Growth, Low Position (High potential, requires selective feasibility investments)
        - Cash Cows: Low Growth, High Position (Mature/core enablers delivering steady strategic foundation)
        - Dogs: Low Growth, Low Position (Candidates for de-scoping, deferral, or cancellation)
        """
        growth_proxy = round(0.50 * module.market_potential + 0.50 * module.risk_adjusted_potential, 3)
        position_proxy = round(
            0.40 * module.strategic_alignment + 0.30 * module.customer_value + 0.30 * module.technical_feasibility, 3
        )

        if growth_proxy >= median_growth and position_proxy >= median_position:
            quadrant = "Stars"
            recommended_action = "Protect & Prioritize (High Capital & Top Talent Allocation)"
        elif growth_proxy >= median_growth and position_proxy < median_position:
            quadrant = "Question Marks"
            recommended_action = "Selective Investment / R&D Spike to Resolve Feasibility"
        elif growth_proxy < median_growth and position_proxy >= median_position:
            quadrant = "Cash Cows"
            recommended_action = "Maintain Foundation with Lean Staffing"
        else:
            quadrant = "Dogs"
            recommended_action = "De-scope, Defer, or Prime for Counterfactual Trade-off"

        return {
            "module_id": module.id,
            "module_name": module.name,
            "growth_proxy": growth_proxy,
            "position_proxy": position_proxy,
            "quadrant": quadrant,
            "recommended_action": recommended_action,
            "proxy_indicator_tags": [
                "Growth = f(Market Potential, Risk-Adjusted Potential) [Proxy]",
                "Position = f(Strategic Alignment, Customer Value, Feasibility) [Proxy]",
                f"Source: {module.source_origin}"
            ]
        }

    @classmethod
    def analyze_portfolio(
        cls, modules: List[SoftwareModule], weights: CriterionWeights
    ) -> List[Dict[str, Any]]:
        """Analyzes all modules, calculating P_i, BCG classification, and ranking."""
        analyzed = []
        for m in modules:
            p_i = cls.calculate_priority_score(m, weights)
            bcg = cls.classify_bcg_quadrant(m)
            analyzed.append({
                "module": m,
                "priority_score": p_i,
                "bcg_quadrant": bcg["quadrant"],
                "growth_proxy": bcg["growth_proxy"],
                "position_proxy": bcg["position_proxy"],
                "recommended_action": bcg["recommended_action"],
                "proxy_indicator_tags": bcg["proxy_indicator_tags"]
            })

        # Sort descending by priority score
        analyzed.sort(key=lambda x: x["priority_score"], reverse=True)
        for rank, item in enumerate(analyzed, start=1):
            item["strategic_rank"] = rank
        return analyzed
