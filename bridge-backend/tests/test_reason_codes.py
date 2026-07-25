from app.decision_engine.reason_codes import (
    REASON_CODE_REGISTRY,
    get_reason_code_rule,
    infer_reason_code,
)
from app.models.evidence import CredibilityLabel


def test_registry_has_all_six_spec_codes():
    assert set(REASON_CODE_REGISTRY.keys()) == {"4554", "4553", "4513", "4512", "4540", "4544"}


def test_registry_categories_match_spec():
    assert REASON_CODE_REGISTRY["4554"].category == "Goods Not Received"
    assert REASON_CODE_REGISTRY["4553"].category == "Not as Described"
    assert REASON_CODE_REGISTRY["4513"].category == "Credit Not Presented"
    assert REASON_CODE_REGISTRY["4512"].category == "Multiple Processing"
    assert REASON_CODE_REGISTRY["4540"].category == "Card Not Present"
    assert REASON_CODE_REGISTRY["4544"].category == "Recurring Billing Cancellation"


def test_every_rule_requires_at_least_one_label_per_side():
    for rule in REASON_CODE_REGISTRY.values():
        assert len(rule.cardholder_required) >= 1
        assert len(rule.merchant_required) >= 1


def test_get_reason_code_rule_known_code():
    rule = get_reason_code_rule("4554")
    assert rule is not None
    assert rule.code == "4554"


def test_get_reason_code_rule_unknown_code_returns_none():
    assert get_reason_code_rule("9999") is None


def test_get_reason_code_rule_none_input_returns_none():
    assert get_reason_code_rule(None) is None


def test_infer_reason_code_maps_known_free_text():
    assert infer_reason_code("Item not received") == "4554"
    assert infer_reason_code("Item not as described") == "4553"
    assert infer_reason_code("Duplicate charge") == "4512"
    assert infer_reason_code("Service not rendered") == "4554"
    assert infer_reason_code("Unauthorized transaction") == "4540"


def test_infer_reason_code_is_case_insensitive():
    assert infer_reason_code("ITEM NOT RECEIVED") == "4554"
    assert infer_reason_code("  item not received  ") == "4554"


def test_infer_reason_code_unmapped_text_returns_none():
    assert infer_reason_code("Other") is None
    assert infer_reason_code("Something completely unrecognized") is None


def test_cardholder_requirement_is_always_customer_statement():
    # Every reason code in v1 treats a cardholder statement as the
    # baseline substantiation for a claim.
    for rule in REASON_CODE_REGISTRY.values():
        assert CredibilityLabel.CUSTOMER_STATEMENT in rule.cardholder_required
