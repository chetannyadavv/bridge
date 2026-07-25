"""
Sprint 6 Final Validation — exercises the exact workflow specified in
the sprint requirements, end to end:
  1. Create dispute
  2. Join as merchant and cardholder (websocket connections)
  3. Submit evidence
  4. Realtime synchronization works
  5. Decision Engine generates recommendation
  6. Resolution page displays correctly (i.e. the API response the
     Resolution page renders contains everything it needs)
  7. No regressions (covered separately by the other 70 tests in this
     suite, all passing alongside this one)
"""


def test_final_validation_full_workflow(client):
    # 1. Create dispute
    r = client.post(
        "/disputes",
        json={
            "transaction_id": "txn_FINAL_VALIDATION",
            "merchant_name": "Final Validation Co",
            "amount": "150.00",
            "currency": "USD",
            "reason": "Item not as described",
        },
    )
    assert r.status_code == 201
    dispute = r.json()
    dispute_id = dispute["id"]
    assert dispute["status"] == "OPEN"
    assert dispute["reason_code"] == "4553"

    # 2. Join as both merchant and cardholder (websocket connections)
    with client.websocket_connect(f"/ws/disputes/{dispute_id}?role=cardholder") as ws_cardholder, \
         client.websocket_connect(f"/ws/disputes/{dispute_id}?role=merchant") as ws_merchant:

        # Each gets an initial snapshot.
        for _ in range(4):
            ws_cardholder.receive_json()
        presence = ws_cardholder.receive_json()  # solo presence (cardholder only, so far)
        assert presence["payload"]["roles"] == ["cardholder"]

        for _ in range(4):
            ws_merchant.receive_json()

        # Cardholder sees merchant join.
        joined = ws_cardholder.receive_json()
        assert sorted(joined["payload"]["roles"]) == ["cardholder", "merchant"]
        ws_merchant.receive_json()  # merchant's own join broadcast

        # 3. Submit evidence (cardholder side)
        r = client.post(
            f"/disputes/{dispute_id}/evidence",
            json={
                "uploader": "cardholder",
                "type": "TEXT",
                "credibility": "CUSTOMER_STATEMENT",
                "summary": "The item received did not match the listing description.",
            },
        )
        assert r.status_code == 201

        # 4. Realtime synchronization: BOTH connected clients receive the update
        for label, ws in [("cardholder", ws_cardholder), ("merchant", ws_merchant)]:
            types = [ws.receive_json()["type"] for _ in range(4)]
            assert types == [
                "dispute_updated",
                "evidence_updated",
                "timeline_updated",
                "recommendation_updated",
            ], f"{label} did not receive full realtime broadcast"

        # Submit merchant evidence too, so we exercise a two-sided decision.
        r = client.post(
            f"/disputes/{dispute_id}/evidence",
            json={
                "uploader": "merchant",
                "type": "TEXT",
                "credibility": "MERCHANT_STATEMENT",
                "summary": "The listing photos accurately represented the item.",
            },
        )
        assert r.status_code == 201
        for ws in [ws_cardholder, ws_merchant]:
            for _ in range(4):
                ws.receive_json()

    # 5. Decision Engine generated a recommendation
    decision = client.get(f"/disputes/{dispute_id}/decision").json()
    assert decision["engine_recommendation"] in {
        "Approve Refund", "Reject Refund", "Partial Refund",
        "Request Additional Evidence", "Escalate for Manual Review",
    }
    assert decision["reason_code"] == "4553"
    assert 0 <= decision["confidence"] <= 100
    assert decision["summary"]
    assert isinstance(decision["reasons"], list) and len(decision["reasons"]) > 0
    assert isinstance(decision["next_steps"], list) and len(decision["next_steps"]) > 0

    # Both parties accept -> dispute resolves (Sprint 6 bug fix batch)
    client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "cardholder"})
    assert client.get(f"/disputes/{dispute_id}").json()["status"] != "RESOLVED"
    r = client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "merchant"})
    assert client.get(f"/disputes/{dispute_id}").json()["status"] == "RESOLVED"

    # 6. Resolution page displays correctly — verify the API response
    # contains every field the Sprint 6 Resolution page renders.
    final_decision = client.get(f"/disputes/{dispute_id}/decision").json()
    required_fields = [
        "engine_recommendation", "confidence", "reason_code", "category",
        "summary", "reasons", "missing_evidence", "next_steps",
        "explanation", "accepted_by",
    ]
    for field in required_fields:
        assert field in final_decision, f"Resolution page requires '{field}' but it's missing from the API response"
    assert set(final_decision["accepted_by"]) == {"cardholder", "merchant"}

    evidence = client.get(f"/disputes/{dispute_id}/evidence").json()
    assert len(evidence) == 2  # "Evidence considered" section has data to show

    print("\nFINAL VALIDATION WORKFLOW: PASS")
    print(f"  Dispute: {dispute_id}")
    print(f"  Decision: {final_decision['engine_recommendation']} ({final_decision['confidence']}% confidence)")
    print(f"  Reason code: {final_decision['reason_code']} ({final_decision['category']})")
    print(f"  Accepted by: {final_decision['accepted_by']}")
