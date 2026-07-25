from app.decision_engine.decision_engine import evaluate, DecisionResult, Recommendation  # noqa: F401
from app.decision_engine.reason_codes import infer_reason_code  # noqa: F401


class DecisionEngine:
    """Thin wrapper so callers can do `engine = DecisionEngine(); engine.compute(dispute, evidence_items)`."""

    def compute(self, dispute, evidence_items):
        return evaluate(dispute.reason_code, evidence_items)
