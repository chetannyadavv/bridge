from app.decision_engine.evidence_validator import validate_evidence
from app.decision_engine.reason_codes import REASON_CODE_REGISTRY
from app.models.evidence import Evidence, UploaderRole, EvidenceType, CredibilityLabel

RULE_4554 = REASON_CODE_REGISTRY["4554"]  # Goods Not Received


def _evidence(uploader: UploaderRole, credibility: CredibilityLabel, eid: str = "ev_1") -> Evidence:
    # Plain in-memory ORM instances — no DB/session needed, since
    # validate_evidence is a pure function over the objects it's given.
    return Evidence(
        id=eid,
        dispute_id="dsp_test",
        uploader=uploader,
        type=EvidenceType.TEXT,
        credibility=credibility,
        summary="test evidence",
    )


def test_no_evidence_neither_side_satisfied():
    result = validate_evidence(RULE_4554, [])
    assert result.cardholder_satisfied is False
    assert result.merchant_satisfied is False
    assert result.conflict is False


def test_cardholder_only_satisfies_cardholder_side_only():
    evidence = [_evidence(UploaderRole.cardholder, CredibilityLabel.CUSTOMER_STATEMENT)]
    result = validate_evidence(RULE_4554, evidence)
    assert result.cardholder_satisfied is True
    assert result.merchant_satisfied is False
    assert result.conflict is False
    assert result.merchant_missing == RULE_4554.merchant_required


def test_merchant_only_satisfies_merchant_side_only():
    evidence = [_evidence(UploaderRole.merchant, CredibilityLabel.GPS_CONFIRMED)]
    result = validate_evidence(RULE_4554, evidence)
    assert result.cardholder_satisfied is False
    assert result.merchant_satisfied is True
    assert result.conflict is False


def test_both_sides_satisfied_flags_conflict():
    evidence = [
        _evidence(UploaderRole.cardholder, CredibilityLabel.CUSTOMER_STATEMENT, "ev_1"),
        _evidence(UploaderRole.merchant, CredibilityLabel.TIMESTAMPED_RECEIPT, "ev_2"),
    ]
    result = validate_evidence(RULE_4554, evidence)
    assert result.cardholder_satisfied is True
    assert result.merchant_satisfied is True
    assert result.conflict is True


def test_any_one_of_multiple_accepted_merchant_labels_satisfies():
    # 4554 accepts TIMESTAMPED_RECEIPT, GPS_CONFIRMED, or VERIFIED_TRANSACTION
    # — any single one should satisfy the merchant side.
    for label in RULE_4554.merchant_required:
        evidence = [_evidence(UploaderRole.merchant, label)]
        result = validate_evidence(RULE_4554, evidence)
        assert result.merchant_satisfied is True, f"{label} should satisfy merchant side"


def test_wrong_uploader_role_does_not_satisfy_other_side():
    # A merchant submitting a customer-statement-labeled item shouldn't
    # count toward the cardholder's requirement — sides are validated
    # independently by uploader, not just by label.
    evidence = [_evidence(UploaderRole.merchant, CredibilityLabel.CUSTOMER_STATEMENT)]
    result = validate_evidence(RULE_4554, evidence)
    assert result.cardholder_satisfied is False


def test_system_uploaded_evidence_does_not_satisfy_either_party_side():
    evidence = [_evidence(UploaderRole.system, CredibilityLabel.VERIFIED_TRANSACTION)]
    result = validate_evidence(RULE_4554, evidence)
    assert result.cardholder_satisfied is False
    assert result.merchant_satisfied is False


def test_matched_ids_are_returned_for_satisfied_side():
    evidence = [_evidence(UploaderRole.cardholder, CredibilityLabel.CUSTOMER_STATEMENT, "ev_abc")]
    result = validate_evidence(RULE_4554, evidence)
    assert result.cardholder_matched == ("ev_abc",)


def test_unverified_evidence_does_not_satisfy_a_specific_required_label():
    evidence = [_evidence(UploaderRole.merchant, CredibilityLabel.UNVERIFIED)]
    result = validate_evidence(RULE_4554, evidence)
    assert result.merchant_satisfied is False
