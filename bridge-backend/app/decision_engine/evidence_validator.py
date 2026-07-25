from dataclasses import dataclass

from app.decision_engine.reason_codes import ReasonCodeRule
from app.models.evidence import Evidence, CredibilityLabel


@dataclass(frozen=True)
class EvidenceValidationResult:
    cardholder_satisfied: bool
    merchant_satisfied: bool
    cardholder_missing: tuple[CredibilityLabel, ...]
    merchant_missing: tuple[CredibilityLabel, ...]
    cardholder_matched: tuple[str, ...]  # matched evidence ids
    merchant_matched: tuple[str, ...]
    conflict: bool


def _labels_by_uploader(
    evidence_items: list[Evidence], uploader: str
) -> dict[CredibilityLabel, list[str]]:
    matches: dict[CredibilityLabel, list[str]] = {}
    for item in evidence_items:
        if item.uploader.value == uploader:
            matches.setdefault(item.credibility, []).append(item.id)
    return matches


def _check_side(
    required: tuple[CredibilityLabel, ...],
    available: dict[CredibilityLabel, list[str]],
) -> tuple[bool, tuple[CredibilityLabel, ...], tuple[str, ...]]:
    """
    A side is satisfied if AT LEAST ONE of its required labels is present
    — evaluating whether the evidence satisfies any accepted form of
    proof, not raw evidence count, per the spec's "Evaluate evidence
    quality, not evidence count."
    """
    matched_ids: list[str] = []
    satisfied = False
    for label in required:
        if label in available:
            satisfied = True
            matched_ids.extend(available[label])

    missing = () if satisfied else tuple(label for label in required if label not in available)
    return satisfied, missing, tuple(matched_ids)


def validate_evidence(rule: ReasonCodeRule, evidence_items: list[Evidence]) -> EvidenceValidationResult:
    """Validates merchant and cardholder evidence separately, per the
    spec — the two sides never affect each other's satisfied/missing
    computation, only the final recommendation combines them."""
    cardholder_available = _labels_by_uploader(evidence_items, "cardholder")
    merchant_available = _labels_by_uploader(evidence_items, "merchant")

    cardholder_satisfied, cardholder_missing, cardholder_matched = _check_side(
        rule.cardholder_required, cardholder_available
    )
    merchant_satisfied, merchant_missing, merchant_matched = _check_side(
        rule.merchant_required, merchant_available
    )

    # Both sides independently substantiating their position is exactly
    # the situation that makes a dispute genuinely hard to call — real
    # evidentiary tension rather than a data gap. It lowers confidence
    # rather than changing which recommendation bucket applies (see
    # decision_engine.py).
    conflict = cardholder_satisfied and merchant_satisfied

    return EvidenceValidationResult(
        cardholder_satisfied=cardholder_satisfied,
        merchant_satisfied=merchant_satisfied,
        cardholder_missing=cardholder_missing,
        merchant_missing=merchant_missing,
        cardholder_matched=cardholder_matched,
        merchant_matched=merchant_matched,
        conflict=conflict,
    )
