"""
Investigation suite for the reported Decision Engine bug (order-dependence
/ staleness). Run against the UNMODIFIED code first to observe actual
behavior before any fix is applied — do not assume the mechanism.

Two evidence-tagging variants are tested throughout, because the actual
frontend (SharedEvidenceBoard.tsx) hardcodes merchant evidence submitted
through the simple text form to MERCHANT_STATEMENT, and reason code 4554's
registry entry does NOT include MERCHANT_STATEMENT as an accepted merchant
proof label. That mismatch is a prime suspect and needs to be tested
separately from the engine's own order-handling logic:

  - "as_ui_sends_it": credibility labels exactly as the current frontend
    UI actually sends them (MERCHANT_STATEMENT / CUSTOMER_STATEMENT).
  - "matching_registry": credibility labels that DO satisfy 4554's
    registry requirements (TIMESTAMPED_RECEIPT for merchant), to isolate
    whether the core evaluate() pipeline itself has an order-dependence
    bug independent of the UI/registry mismatch.
"""

import itertools
import random


def _create_dispute(client, suffix, reason="Item not received"):
    r = client.post(
        "/disputes",
        json={
            "transaction_id": f"txn_INVESTIGATE_{suffix}",
            "merchant_name": "Investigate Co",
            "amount": "100.00",
            "currency": "USD",
            "reason": reason,
        },
    )
    assert r.status_code == 201
    return r.json()["id"]


def _add_cardholder_evidence(client, dispute_id):
    r = client.post(
        f"/disputes/{dispute_id}/evidence",
        json={
            "uploader": "cardholder",
            "type": "TEXT",
            "credibility": "CUSTOMER_STATEMENT",
            "summary": "Item never arrived.",
        },
    )
    assert r.status_code == 201
    return r.json()


def _add_merchant_evidence(client, dispute_id, credibility):
    r = client.post(
        f"/disputes/{dispute_id}/evidence",
        json={
            "uploader": "merchant",
            "type": "SYSTEM_RECORD" if credibility != "MERCHANT_STATEMENT" else "TEXT",
            "credibility": credibility,
            "summary": "Proof of delivery. Tracking shows delivered and signed for.",
        },
    )
    assert r.status_code == 201
    return r.json()


def _latest_recommendation(client, dispute_id):
    recs = client.get(f"/disputes/{dispute_id}/recommendation").json()
    return recs[-1]


def _all_recommendations(client, dispute_id):
    return client.get(f"/disputes/{dispute_id}/recommendation").json()


# ---------------------------------------------------------------------------
# Reproduction of the reported scenarios, exactly as described, using
# MERCHANT_STATEMENT (what the real UI actually sends today).
# ---------------------------------------------------------------------------


def test_repro_scenario_1_cardholder_then_merchant_as_ui_sends_it(client):
    dispute_id = _create_dispute(client, "REPRO1")

    _add_cardholder_evidence(client, dispute_id)
    after_cardholder = _latest_recommendation(client, dispute_id)
    print(f"\n[Scenario 1] After cardholder only: {after_cardholder['engine_recommendation']} "
          f"(confidence={after_cardholder['confidence']})")

    _add_merchant_evidence(client, dispute_id, "MERCHANT_STATEMENT")
    after_merchant = _latest_recommendation(client, dispute_id)
    print(f"[Scenario 1] After cardholder+merchant: {after_merchant['engine_recommendation']} "
          f"(confidence={after_merchant['confidence']})")

    all_recs = _all_recommendations(client, dispute_id)
    print(f"[Scenario 1] Recommendation history length: {len(all_recs)}")
    print(f"[Scenario 1] Missing evidence after merchant submission: {after_merchant['missing_evidence']}")


def test_repro_scenario_2_merchant_then_cardholder_as_ui_sends_it(client):
    dispute_id = _create_dispute(client, "REPRO2")

    _add_merchant_evidence(client, dispute_id, "MERCHANT_STATEMENT")
    after_merchant = _latest_recommendation(client, dispute_id)
    print(f"\n[Scenario 2] After merchant only: {after_merchant['engine_recommendation']} "
          f"(confidence={after_merchant['confidence']})")

    _add_cardholder_evidence(client, dispute_id)
    after_cardholder = _latest_recommendation(client, dispute_id)
    print(f"[Scenario 2] After merchant+cardholder: {after_cardholder['engine_recommendation']} "
          f"(confidence={after_cardholder['confidence']})")


# ---------------------------------------------------------------------------
# Same two scenarios, but with merchant evidence tagged to actually satisfy
# 4554's registry requirement (TIMESTAMPED_RECEIPT) — isolates whether the
# core evaluate() pipeline has an order bug independent of the UI/registry
# mismatch.
# ---------------------------------------------------------------------------


def test_repro_scenario_1_matching_registry(client):
    dispute_id = _create_dispute(client, "REPRO1B")
    _add_cardholder_evidence(client, dispute_id)
    after_cardholder = _latest_recommendation(client, dispute_id)
    print(f"\n[Scenario 1B - matching registry] After cardholder only: "
          f"{after_cardholder['engine_recommendation']}")

    _add_merchant_evidence(client, dispute_id, "TIMESTAMPED_RECEIPT")
    after_merchant = _latest_recommendation(client, dispute_id)
    print(f"[Scenario 1B - matching registry] After cardholder+merchant: "
          f"{after_merchant['engine_recommendation']}")


def test_repro_scenario_2_matching_registry(client):
    dispute_id = _create_dispute(client, "REPRO2B")
    _add_merchant_evidence(client, dispute_id, "TIMESTAMPED_RECEIPT")
    after_merchant = _latest_recommendation(client, dispute_id)
    print(f"\n[Scenario 2B - matching registry] After merchant only: "
          f"{after_merchant['engine_recommendation']}")

    _add_cardholder_evidence(client, dispute_id)
    after_cardholder = _latest_recommendation(client, dispute_id)
    print(f"[Scenario 2B - matching registry] After merchant+cardholder: "
          f"{after_cardholder['engine_recommendation']}")


# ---------------------------------------------------------------------------
# Test 1 — Upload Order Independence (as specified)
# ---------------------------------------------------------------------------


def test_1_upload_order_independence_matching_registry(client):
    dispute_a = _create_dispute(client, "T1A")
    _add_cardholder_evidence(client, dispute_a)
    _add_merchant_evidence(client, dispute_a, "TIMESTAMPED_RECEIPT")
    final_a = _latest_recommendation(client, dispute_a)

    dispute_b = _create_dispute(client, "T1B")
    _add_merchant_evidence(client, dispute_b, "TIMESTAMPED_RECEIPT")
    _add_cardholder_evidence(client, dispute_b)
    final_b = _latest_recommendation(client, dispute_b)

    assert final_a["engine_recommendation"] == final_b["engine_recommendation"], (
        f"Order dependence detected: cardholder-then-merchant={final_a['engine_recommendation']}, "
        f"merchant-then-cardholder={final_b['engine_recommendation']}"
    )
    assert final_a["confidence"] == final_b["confidence"]


def test_1_upload_order_independence_as_ui_sends_it(client):
    """Same test, but with the credibility labels the real UI actually
    sends — expected to reveal the registry-mismatch issue rather than an
    engine bug, if that's the actual root cause."""
    dispute_a = _create_dispute(client, "T1C")
    _add_cardholder_evidence(client, dispute_a)
    _add_merchant_evidence(client, dispute_a, "MERCHANT_STATEMENT")
    final_a = _latest_recommendation(client, dispute_a)

    dispute_b = _create_dispute(client, "T1D")
    _add_merchant_evidence(client, dispute_b, "MERCHANT_STATEMENT")
    _add_cardholder_evidence(client, dispute_b)
    final_b = _latest_recommendation(client, dispute_b)

    assert final_a["engine_recommendation"] == final_b["engine_recommendation"], (
        f"Order dependence detected: cardholder-then-merchant={final_a['engine_recommendation']}, "
        f"merchant-then-cardholder={final_b['engine_recommendation']}"
    )


# ---------------------------------------------------------------------------
# Test 2 — Recompute After Every Submission
# ---------------------------------------------------------------------------


def test_2_recompute_uses_all_evidence_not_just_latest(client):
    dispute_id = _create_dispute(client, "T2")

    _add_cardholder_evidence(client, dispute_id)
    after_cardholder = _latest_recommendation(client, dispute_id)
    assert after_cardholder["engine_recommendation"] == "Approve Refund"

    _add_merchant_evidence(client, dispute_id, "TIMESTAMPED_RECEIPT")
    after_merchant = _latest_recommendation(client, dispute_id)

    # With BOTH sides now satisfied, the recommendation must reflect that
    # — not just the merchant's latest single item in isolation.
    assert after_merchant["engine_recommendation"] == "Partial Refund", (
        f"Expected recomputation using ALL evidence to yield Partial Refund, "
        f"got {after_merchant['engine_recommendation']}"
    )


# ---------------------------------------------------------------------------
# Test 3 — Evidence Accumulation
# ---------------------------------------------------------------------------


def test_3_all_evidence_loaded_before_decision(client):
    dispute_id = _create_dispute(client, "T3")
    _add_cardholder_evidence(client, dispute_id)
    _add_merchant_evidence(client, dispute_id, "TIMESTAMPED_RECEIPT")
    _add_merchant_evidence(client, dispute_id, "GPS_CONFIRMED")

    evidence = client.get(f"/disputes/{dispute_id}/evidence").json()
    assert len(evidence) == 3

    latest = _latest_recommendation(client, dispute_id)
    # missing_evidence must be empty since both sides are fully satisfied
    # by the accumulated evidence set.
    assert latest["missing_evidence"] == []


# ---------------------------------------------------------------------------
# Test 4 — Idempotence
# ---------------------------------------------------------------------------


def test_4_idempotence_of_reading_recommendation(client):
    dispute_id = _create_dispute(client, "T4")
    _add_cardholder_evidence(client, dispute_id)
    _add_merchant_evidence(client, dispute_id, "TIMESTAMPED_RECEIPT")

    r1 = _latest_recommendation(client, dispute_id)
    r2 = _latest_recommendation(client, dispute_id)
    assert r1 == r2


def test_4_idempotence_of_engine_evaluate_directly(client):
    from app.decision_engine.decision_engine import evaluate
    from app.models.evidence import Evidence, UploaderRole, EvidenceType, CredibilityLabel

    evidence = [
        Evidence(id="ev_1", dispute_id="d", uploader=UploaderRole.cardholder,
                 type=EvidenceType.TEXT, credibility=CredibilityLabel.CUSTOMER_STATEMENT, summary="x"),
        Evidence(id="ev_2", dispute_id="d", uploader=UploaderRole.merchant,
                 type=EvidenceType.SYSTEM_RECORD, credibility=CredibilityLabel.TIMESTAMPED_RECEIPT, summary="y"),
    ]
    result1 = evaluate("4554", evidence)
    result2 = evaluate("4554", evidence)
    assert result1 == result2


# ---------------------------------------------------------------------------
# Test 5 — Determinism under randomized upload order (20 trials)
# ---------------------------------------------------------------------------


def test_5_determinism_across_20_randomized_orders(client):
    # Each of the 4 evidence items to submit; order is shuffled.
    items = [
        ("cardholder", "CUSTOMER_STATEMENT"),
        ("merchant", "TIMESTAMPED_RECEIPT"),
        ("merchant", "GPS_CONFIRMED"),
        ("cardholder", "CUSTOMER_STATEMENT"),
    ]

    results = []
    random.seed(42)
    for trial in range(20):
        order = items[:]
        random.shuffle(order)
        dispute_id = _create_dispute(client, f"T5_{trial}")
        for uploader, credibility in order:
            if uploader == "cardholder":
                _add_cardholder_evidence(client, dispute_id)
            else:
                _add_merchant_evidence(client, dispute_id, credibility)
        final = _latest_recommendation(client, dispute_id)
        results.append(final["engine_recommendation"])

    assert len(set(results)) == 1, f"Non-deterministic results across shuffled orders: {set(results)}"


# ---------------------------------------------------------------------------
# Test 6 — State Replacement (old recommendations don't linger as "latest")
# ---------------------------------------------------------------------------


def test_6_new_evaluation_replaces_previous_as_latest(client):
    dispute_id = _create_dispute(client, "T6")
    _add_cardholder_evidence(client, dispute_id)
    first = _latest_recommendation(client, dispute_id)

    _add_merchant_evidence(client, dispute_id, "TIMESTAMPED_RECEIPT")
    second = _latest_recommendation(client, dispute_id)

    assert second["id"] != first["id"]
    assert second["engine_recommendation"] != first["engine_recommendation"] or (
        second["confidence"] != first["confidence"]
    ), "Second evaluation should reflect the updated evidence set"

    all_recs = _all_recommendations(client, dispute_id)
    assert all_recs[-1]["id"] == second["id"], "Latest recommendation in history must be the most recent evaluation"


# ---------------------------------------------------------------------------
# Test 7 — API never returns a stale recommendation after new evidence
# ---------------------------------------------------------------------------


def test_7_api_recommendation_endpoint_reflects_new_evidence_immediately(client):
    dispute_id = _create_dispute(client, "T7")
    _add_cardholder_evidence(client, dispute_id)
    before = client.get(f"/disputes/{dispute_id}/recommendation").json()[-1]

    _add_merchant_evidence(client, dispute_id, "TIMESTAMPED_RECEIPT")
    after = client.get(f"/disputes/{dispute_id}/recommendation").json()[-1]

    assert after["id"] != before["id"]
    assert after["updated_at"] >= before["updated_at"]


def test_7_decision_endpoint_reflects_new_evidence_immediately(client):
    dispute_id = _create_dispute(client, "T7B")
    _add_cardholder_evidence(client, dispute_id)
    before = client.get(f"/disputes/{dispute_id}/decision").json()

    _add_merchant_evidence(client, dispute_id, "TIMESTAMPED_RECEIPT")
    after = client.get(f"/disputes/{dispute_id}/decision").json()

    assert after["id"] != before["id"]
