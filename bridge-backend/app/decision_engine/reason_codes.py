from dataclasses import dataclass

from app.models.evidence import CredibilityLabel


@dataclass(frozen=True)
class ReasonCodeRule:
    """
    One entry in the Reason Code Registry (Bridge Decision Engine
    Specification v1.0, "Supported Reason Codes"). Adding a future AMEX
    reason code means adding one more entry to REASON_CODE_REGISTRY —
    nothing in evidence_validator.py or decision_engine.py needs to
    change to support it. This is the extensibility point the spec
    calls for.
    """

    code: str
    category: str
    typical_recommendation: str
    # "At least one of these credibility labels, from this side, satisfies
    # the requirement" — an "any of" list rather than a single required
    # label, since real evidence for the same claim can arrive in more
    # than one form (e.g. a GPS-confirmed delivery log OR a timestamped
    # receipt both count as merchant proof of fulfillment).
    cardholder_required: tuple[CredibilityLabel, ...]
    merchant_required: tuple[CredibilityLabel, ...]


REASON_CODE_REGISTRY: dict[str, ReasonCodeRule] = {
    "4554": ReasonCodeRule(
        code="4554",
        category="Goods Not Received",
        typical_recommendation="Approve Refund / Request Evidence",
        cardholder_required=(CredibilityLabel.CUSTOMER_STATEMENT,),
        merchant_required=(
            CredibilityLabel.TIMESTAMPED_RECEIPT,
            CredibilityLabel.GPS_CONFIRMED,
            CredibilityLabel.VERIFIED_TRANSACTION,
        ),
    ),
    "4553": ReasonCodeRule(
        code="4553",
        category="Not as Described",
        typical_recommendation="Partial or Approve Refund",
        cardholder_required=(CredibilityLabel.CUSTOMER_STATEMENT,),
        merchant_required=(
            CredibilityLabel.MERCHANT_STATEMENT,
            CredibilityLabel.TIMESTAMPED_RECEIPT,
        ),
    ),
    "4513": ReasonCodeRule(
        code="4513",
        category="Credit Not Presented",
        typical_recommendation="Approve Refund",
        cardholder_required=(CredibilityLabel.CUSTOMER_STATEMENT,),
        merchant_required=(
            CredibilityLabel.VERIFIED_TRANSACTION,
            CredibilityLabel.MERCHANT_STATEMENT,
        ),
    ),
    "4512": ReasonCodeRule(
        code="4512",
        category="Multiple Processing",
        typical_recommendation="Approve Refund",
        cardholder_required=(CredibilityLabel.CUSTOMER_STATEMENT,),
        merchant_required=(CredibilityLabel.VERIFIED_TRANSACTION,),
    ),
    "4540": ReasonCodeRule(
        code="4540",
        category="Card Not Present",
        typical_recommendation="Reject or Manual Review",
        cardholder_required=(CredibilityLabel.CUSTOMER_STATEMENT,),
        merchant_required=(
            CredibilityLabel.GPS_CONFIRMED,
            CredibilityLabel.VERIFIED_TRANSACTION,
        ),
    ),
    "4544": ReasonCodeRule(
        code="4544",
        category="Recurring Billing Cancellation",
        typical_recommendation="Approve Refund",
        cardholder_required=(CredibilityLabel.CUSTOMER_STATEMENT,),
        merchant_required=(
            CredibilityLabel.MERCHANT_STATEMENT,
            CredibilityLabel.TIMESTAMPED_RECEIPT,
        ),
    ),
}


def get_reason_code_rule(code: str | None) -> ReasonCodeRule | None:
    if code is None:
        return None
    return REASON_CODE_REGISTRY.get(code)


# Bridging concern: Sprints 1-4 store a dispute's reason as free text from
# a fixed dropdown (see bridge-frontend CreateDispute.tsx), not an AMEX
# reason code. This maps that free text to the nearest registry code once,
# at dispute-creation time (see dispute_service.create_dispute) — so
# `Dispute.reason_code` is set deterministically once and reused
# thereafter, rather than being re-inferred from text on every decision
# run.

_FREE_TEXT_REASON_TO_CODE: dict[str, str] = {
    "item not received": "4554",
    "item not as described": "4553",
    "duplicate charge": "4512",
    "service not rendered": "4554",
    "unauthorized transaction": "4540",
}


def infer_reason_code(reason_text: str) -> str | None:
    return _FREE_TEXT_REASON_TO_CODE.get(reason_text.strip().lower())
