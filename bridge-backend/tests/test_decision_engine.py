from app.decision_engine.decision_engine import evaluate, Recommendation
from app.models.evidence import Evidence, UploaderRole, EvidenceType, CredibilityLabel


def _evidence(uploader: UploaderRole, credibility: CredibilityLabel, eid: str = "ev_1") -> Evidence:
    return Evidence(
        id=eid,
        dispute_id="dsp_test",
        uploader=uploader,
        type=EvidenceType.TEXT,
        credibility=credibility,
        summary="test evidence",
    )


def test_unrecognized_reason_code_escalates_with_low_confidence():
    result = evaluate("9999", [])
    assert result.recommendation == Recommendation.ESCALATE_FOR_MANUAL_REVIEW
    assert result.confidence == 20
    assert result.category is None
    assert result.validation is None


def test_none_reason_code_escalates():
    result = evaluate(None, [])
    assert result.recommendation == Recommendation.ESCALATE_FOR_MANUAL_REVIEW


def test_no_evidence_requests_additional_evidence():
    result = evaluate("4554", [])
    assert result.recommendation == Recommendation.REQUEST_ADDITIONAL_EVIDENCE
    assert result.category == "Goods Not Received"
    assert result.confidence >= 35  # confirms it did NOT get overridden to escalation


def test_cardholder_only_approves_refund():
    evidence = [_evidence(UploaderRole.cardholder, CredibilityLabel.CUSTOMER_STATEMENT)]
    result = evaluate("4554", evidence)
    assert result.recommendation == Recommendation.APPROVE_REFUND
    assert result.confidence > 50  # cardholder satisfied should raise confidence above baseline


def test_merchant_only_rejects_refund():
    evidence = [_evidence(UploaderRole.merchant, CredibilityLabel.GPS_CONFIRMED)]
    result = evaluate("4554", evidence)
    assert result.recommendation == Recommendation.REJECT_REFUND


def test_both_sides_satisfied_yields_partial_refund():
    evidence = [
        _evidence(UploaderRole.cardholder, CredibilityLabel.CUSTOMER_STATEMENT, "ev_1"),
        _evidence(UploaderRole.merchant, CredibilityLabel.TIMESTAMPED_RECEIPT, "ev_2"),
    ]
    result = evaluate("4554", evidence)
    assert result.recommendation == Recommendation.PARTIAL_REFUND


def test_confidence_is_always_clamped_0_to_100():
    result_low = evaluate("4554", [])
    assert 0 <= result_low.confidence <= 100

    evidence = [
        _evidence(UploaderRole.cardholder, CredibilityLabel.CUSTOMER_STATEMENT, "ev_1"),
        _evidence(UploaderRole.merchant, CredibilityLabel.TIMESTAMPED_RECEIPT, "ev_2"),
        _evidence(UploaderRole.merchant, CredibilityLabel.GPS_CONFIRMED, "ev_3"),
        _evidence(UploaderRole.merchant, CredibilityLabel.VERIFIED_TRANSACTION, "ev_4"),
    ]
    result_high = evaluate("4554", evidence)
    assert 0 <= result_high.confidence <= 100


def test_low_confidence_override_forces_escalation():
    # The six v1 reason codes' scoring range never naturally dips below
    # the escalation threshold except via an unrecognized reason code
    # (tested above) — this is a defensive safety net for future reason
    # codes with different scoring, and is tested directly here against
    # the internal decision function rather than through evaluate().
    from app.decision_engine.decision_engine import _decide_recommendation
    from app.decision_engine.evidence_validator import EvidenceValidationResult

    low_confidence_validation = EvidenceValidationResult(
        cardholder_satisfied=True,
        merchant_satisfied=False,
        cardholder_missing=(),
        merchant_missing=(CredibilityLabel.GPS_CONFIRMED,),
        cardholder_matched=("ev_1",),
        merchant_matched=(),
        conflict=False,
    )
    result = _decide_recommendation(low_confidence_validation, confidence=10)
    assert result == Recommendation.ESCALATE_FOR_MANUAL_REVIEW


def test_confidence_at_exactly_threshold_does_not_escalate():
    from app.decision_engine.decision_engine import _decide_recommendation, LOW_CONFIDENCE_ESCALATION_THRESHOLD
    from app.decision_engine.evidence_validator import EvidenceValidationResult

    validation = EvidenceValidationResult(
        cardholder_satisfied=True,
        merchant_satisfied=False,
        cardholder_missing=(),
        merchant_missing=(CredibilityLabel.GPS_CONFIRMED,),
        cardholder_matched=("ev_1",),
        merchant_matched=(),
        conflict=False,
    )
    result = _decide_recommendation(validation, confidence=LOW_CONFIDENCE_ESCALATION_THRESHOLD)
    assert result == Recommendation.APPROVE_REFUND


def test_extra_corroborating_evidence_increases_confidence_but_caps():
    baseline = evaluate(
        "4554",
        [
            _evidence(UploaderRole.cardholder, CredibilityLabel.CUSTOMER_STATEMENT, "ev_1"),
            _evidence(UploaderRole.merchant, CredibilityLabel.TIMESTAMPED_RECEIPT, "ev_2"),
        ],
    )
    with_extra = evaluate(
        "4554",
        [
            _evidence(UploaderRole.cardholder, CredibilityLabel.CUSTOMER_STATEMENT, "ev_1"),
            _evidence(UploaderRole.merchant, CredibilityLabel.TIMESTAMPED_RECEIPT, "ev_2"),
            _evidence(UploaderRole.merchant, CredibilityLabel.GPS_CONFIRMED, "ev_3"),
            _evidence(UploaderRole.merchant, CredibilityLabel.VERIFIED_TRANSACTION, "ev_4"),
        ],
    )
    assert with_extra.confidence >= baseline.confidence


def test_result_is_deterministic_for_identical_input():
    evidence = [_evidence(UploaderRole.cardholder, CredibilityLabel.CUSTOMER_STATEMENT)]
    result_a = evaluate("4554", evidence)
    result_b = evaluate("4554", evidence)
    assert result_a == result_b
