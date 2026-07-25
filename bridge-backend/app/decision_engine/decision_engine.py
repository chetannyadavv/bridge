from dataclasses import dataclass
from enum import Enum

from app.decision_engine.reason_codes import ReasonCodeRule, get_reason_code_rule
from app.decision_engine.evidence_validator import EvidenceValidationResult, validate_evidence
from app.models.evidence import Evidence, CredibilityLabel

CORROBORATING_LABELS = {
    CredibilityLabel.VERIFIED_TRANSACTION,
    CredibilityLabel.GPS_CONFIRMED,
    CredibilityLabel.TIMESTAMPED_RECEIPT,
}

LOW_CONFIDENCE_ESCALATION_THRESHOLD = 35
UNRECOGNIZED_REASON_CODE_CONFIDENCE = 20


class Recommendation(str, Enum):
    """The five allowed recommendations, per spec."""

    APPROVE_REFUND = "Approve Refund"
    REJECT_REFUND = "Reject Refund"
    PARTIAL_REFUND = "Partial Refund"
    REQUEST_ADDITIONAL_EVIDENCE = "Request Additional Evidence"
    ESCALATE_FOR_MANUAL_REVIEW = "Escalate for Manual Review"


@dataclass(frozen=True)
class DecisionResult:
    reason_code: str | None
    category: str | None
    recommendation: Recommendation
    confidence: int  # 0-100
    validation: EvidenceValidationResult | None


def _score_confidence(
    rule: ReasonCodeRule, validation: EvidenceValidationResult, evidence_items: list[Evidence]
) -> int:
    """
    Deterministic, additive, and fully explainable — every point added or
    subtracted traces back to a specific, named factor (see
    recommendation_formatter.py's `reasons` output).
    """
    confidence = 50
    confidence += 15 if validation.cardholder_satisfied else -5
    confidence += 15 if validation.merchant_satisfied else -5
    if validation.conflict:
        confidence -= 10

    # Reward corroboration beyond the bare minimum, capped — more
    # verified/system-sourced evidence should modestly increase trust,
    # without letting evidence *count* dominate the score (the spec
    # explicitly calls for evaluating quality, not count).
    #
    # "Minimum needed" is 1 corroborating item per side whose requirement
    # includes a corroborating label — not the number of alternative
    # labels listed for that side (a side can be satisfied by any ONE of
    # several accepted forms of proof; counting every alternative as
    # "required" would make this bonus never trigger for reason codes
    # that accept more than one corroborating label, like 4554).
    corroborating_present = sum(1 for e in evidence_items if e.credibility in CORROBORATING_LABELS)
    corroborating_required = sum(
        1
        for side_required in (rule.cardholder_required, rule.merchant_required)
        if any(label in CORROBORATING_LABELS for label in side_required)
    )
    bonus_items = max(0, corroborating_present - corroborating_required)
    confidence += min(bonus_items * 2, 10)

    return max(0, min(100, confidence))


def _decide_recommendation(validation: EvidenceValidationResult, confidence: int) -> Recommendation:
    if not validation.cardholder_satisfied and not validation.merchant_satisfied:
        recommendation = Recommendation.REQUEST_ADDITIONAL_EVIDENCE
    elif validation.cardholder_satisfied and not validation.merchant_satisfied:
        recommendation = Recommendation.APPROVE_REFUND
    elif not validation.cardholder_satisfied and validation.merchant_satisfied:
        recommendation = Recommendation.REJECT_REFUND
    else:
        recommendation = Recommendation.PARTIAL_REFUND

    # Safety override: regardless of category above, very low confidence
    # always escalates rather than automating an uncertain outcome.
    if confidence < LOW_CONFIDENCE_ESCALATION_THRESHOLD:
        return Recommendation.ESCALATE_FOR_MANUAL_REVIEW
    return recommendation


def evaluate(reason_code: str | None, evidence_items: list[Evidence]) -> DecisionResult:
    """
    Reason Code Registry -> Evidence Validator -> Decision Engine, per
    the architecture in Bridge Decision Engine Specification v1.0. Pure
    function — takes already-fetched data rather than a DB session, so
    it needs no database to unit test.
    """
    rule = get_reason_code_rule(reason_code)

    if rule is None:
        return DecisionResult(
            reason_code=reason_code,
            category=None,
            recommendation=Recommendation.ESCALATE_FOR_MANUAL_REVIEW,
            confidence=UNRECOGNIZED_REASON_CODE_CONFIDENCE,
            validation=None,
        )

    validation = validate_evidence(rule, evidence_items)
    confidence = _score_confidence(rule, validation, evidence_items)
    recommendation = _decide_recommendation(validation, confidence)

    return DecisionResult(
        reason_code=rule.code,
        category=rule.category,
        recommendation=recommendation,
        confidence=confidence,
        validation=validation,
    )
