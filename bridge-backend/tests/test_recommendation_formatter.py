from app.decision_engine.decision_engine import evaluate
from app.decision_engine.recommendation_formatter import format_recommendation
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


def test_all_required_output_fields_present():
    decision = evaluate("4554", [])
    formatted = format_recommendation(decision)
    assert formatted.reason_code == "4554"
    assert formatted.category == "Goods Not Received"
    assert isinstance(formatted.recommendation, str)
    assert 0 <= formatted.confidence <= 100
    assert isinstance(formatted.summary, str) and formatted.summary
    assert isinstance(formatted.reasons, list) and len(formatted.reasons) > 0
    assert isinstance(formatted.missing_evidence, list)
    assert isinstance(formatted.next_steps, list) and len(formatted.next_steps) > 0


def test_missing_evidence_lists_the_correct_side():
    decision = evaluate("4554", [_evidence(UploaderRole.cardholder, CredibilityLabel.CUSTOMER_STATEMENT)])
    formatted = format_recommendation(decision)
    assert all(item.startswith("Merchant:") for item in formatted.missing_evidence)
    assert len(formatted.missing_evidence) > 0


def test_no_missing_evidence_when_both_sides_satisfied():
    decision = evaluate(
        "4554",
        [
            _evidence(UploaderRole.cardholder, CredibilityLabel.CUSTOMER_STATEMENT, "ev_1"),
            _evidence(UploaderRole.merchant, CredibilityLabel.TIMESTAMPED_RECEIPT, "ev_2"),
        ],
    )
    formatted = format_recommendation(decision)
    assert formatted.missing_evidence == []


def test_unrecognized_code_produces_explanatory_summary():
    decision = evaluate("9999", [])
    formatted = format_recommendation(decision)
    assert "9999" in formatted.summary
    assert formatted.category is None


def test_next_steps_are_specific_to_recommendation():
    approve = format_recommendation(
        evaluate("4554", [_evidence(UploaderRole.cardholder, CredibilityLabel.CUSTOMER_STATEMENT)])
    )
    reject = format_recommendation(
        evaluate("4554", [_evidence(UploaderRole.merchant, CredibilityLabel.GPS_CONFIRMED)])
    )
    assert approve.next_steps != reject.next_steps


def test_summary_mentions_confidence_and_category_for_recognized_code():
    decision = evaluate("4553", [])
    formatted = format_recommendation(decision)
    assert "Not as Described" in formatted.summary
    assert "4553" in formatted.summary
    assert str(formatted.confidence) in formatted.summary
