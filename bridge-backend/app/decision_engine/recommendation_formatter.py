from dataclasses import dataclass

from app.decision_engine.decision_engine import DecisionResult, Recommendation

_NEXT_STEPS_BY_RECOMMENDATION: dict[Recommendation, list[str]] = {
    Recommendation.APPROVE_REFUND: [
        "Issue the refund to the cardholder.",
        "Notify the merchant of the resolution.",
    ],
    Recommendation.REJECT_REFUND: [
        "Notify the cardholder that the claim is not supported by the evidence on file.",
        "Close the dispute.",
    ],
    Recommendation.PARTIAL_REFUND: [
        "Issue a partial refund reflecting the balance of evidence.",
        "Notify both parties of the resolution.",
    ],
    Recommendation.REQUEST_ADDITIONAL_EVIDENCE: [
        "Request the missing evidence listed above from the relevant party.",
        "Re-run the decision once new evidence is submitted.",
    ],
    Recommendation.ESCALATE_FOR_MANUAL_REVIEW: [
        "Route this dispute to a human analyst for manual review.",
        "Do not take automated action until reviewed.",
    ],
}


@dataclass(frozen=True)
class FormattedRecommendation:
    reason_code: str | None
    category: str | None
    recommendation: str
    confidence: int
    summary: str
    reasons: list[str]
    missing_evidence: list[str]
    next_steps: list[str]


def _missing_evidence_list(decision: DecisionResult) -> list[str]:
    if decision.validation is None:
        return ["Reason code not recognized — cannot determine required evidence."]

    missing: list[str] = []
    for label in decision.validation.cardholder_missing:
        missing.append(f"Cardholder: {label.value.replace('_', ' ').title()}")
    for label in decision.validation.merchant_missing:
        missing.append(f"Merchant: {label.value.replace('_', ' ').title()}")
    return missing


def _reasons_list(decision: DecisionResult) -> list[str]:
    if decision.validation is None:
        return [f"Reason code '{decision.reason_code}' is not in the registry."]

    v = decision.validation
    reasons = [
        "Cardholder evidence requirement satisfied."
        if v.cardholder_satisfied
        else "Cardholder evidence requirement not satisfied.",
        "Merchant evidence requirement satisfied."
        if v.merchant_satisfied
        else "Merchant evidence requirement not satisfied.",
    ]
    if v.conflict:
        reasons.append(
            "Both parties submitted substantiated evidence for opposing positions, "
            "which increases uncertainty in the outcome."
        )
    return reasons


def _summary(decision: DecisionResult) -> str:
    if decision.category is None:
        return (
            f"The reason code '{decision.reason_code}' is not recognized by the decision engine "
            "— escalating for manual review."
        )

    return (
        f"{decision.category} (reason code {decision.reason_code}): recommending "
        f"{decision.recommendation.value.lower()} with {decision.confidence}% confidence."
    )


def format_recommendation(decision: DecisionResult) -> FormattedRecommendation:
    """
    Recommendation Formatter — deterministic templating, no free-text
    generation. Produces exactly the "Required Output" fields from
    Bridge Decision Engine Specification v1.0: Reason Code,
    Recommendation, Confidence, Summary, Reasons, Missing Evidence,
    Next Steps.
    """
    return FormattedRecommendation(
        reason_code=decision.reason_code,
        category=decision.category,
        recommendation=decision.recommendation.value,
        confidence=decision.confidence,
        summary=_summary(decision),
        reasons=_reasons_list(decision),
        missing_evidence=_missing_evidence_list(decision),
        next_steps=list(_NEXT_STEPS_BY_RECOMMENDATION[decision.recommendation]),
    )
