"""
Full-stack regression tests, run against a real (SQLite-backed) FastAPI
app via TestClient — the same technique used for manual verification in
Sprints 3 and 4, now formalized as pytest.
"""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_seed_data_present_and_has_reason_codes(client):
    r = client.get("/disputes")
    assert r.status_code == 200
    disputes = r.json()

    seeded = next(d for d in disputes if d["id"] == "dsp_8841")
    assert seeded["reason"] == "Item not as described"
    assert seeded["reason_code"] == "4553"  # Not as Described

    for seed_id in ("dsp_8841", "dsp_8790", "dsp_8705", "dsp_8622"):
        assert any(d["id"] == seed_id for d in disputes), f"Seed dispute {seed_id} missing"


def test_create_dispute_infers_reason_code_from_free_text(client):
    r = client.post(
        "/disputes",
        json={
            "transaction_id": "txn_S5_1",
            "merchant_name": "Test Merchant",
            "amount": "75.00",
            "currency": "USD",
            "reason": "Item not received",
        },
    )
    assert r.status_code == 201
    dispute = r.json()
    assert dispute["reason_code"] == "4554"


def test_create_dispute_accepts_explicit_reason_code_override(client):
    r = client.post(
        "/disputes",
        json={
            "transaction_id": "txn_S5_2",
            "merchant_name": "Test Merchant",
            "amount": "40.00",
            "currency": "USD",
            "reason": "Other",
            "reason_code": "4513",
        },
    )
    assert r.status_code == 201
    assert r.json()["reason_code"] == "4513"


def test_create_dispute_with_unmapped_reason_has_null_reason_code(client):
    r = client.post(
        "/disputes",
        json={
            "transaction_id": "txn_S5_3",
            "merchant_name": "Test Merchant",
            "amount": "10.00",
            "currency": "USD",
            "reason": "Other",
        },
    )
    assert r.status_code == 201
    assert r.json()["reason_code"] is None


def test_full_decision_flow_cardholder_only_approves(client):
    dispute_id = client.post(
        "/disputes",
        json={
            "transaction_id": "txn_S5_4",
            "merchant_name": "Flow Test Co",
            "amount": "200.00",
            "currency": "USD",
            "reason": "Item not received",  # -> 4554
        },
    ).json()["id"]

    r = client.post(
        f"/disputes/{dispute_id}/evidence",
        json={
            "uploader": "cardholder",
            "type": "TEXT",
            "credibility": "CUSTOMER_STATEMENT",
            "summary": "Never arrived.",
        },
    )
    assert r.status_code == 201

    recs = client.get(f"/disputes/{dispute_id}/recommendation").json()
    assert len(recs) == 1
    latest = recs[-1]

    assert latest["recommendation"] == "FULL_REFUND"
    assert latest["percentage"] == 100

    assert latest["reason_code"] == "4554"
    assert latest["category"] == "Goods Not Received"
    assert latest["engine_recommendation"] == "Approve Refund"
    assert latest["confidence"] > 0
    assert "Merchant:" in "".join(latest["missing_evidence"])
    assert len(latest["next_steps"]) > 0


def test_full_decision_flow_both_sides_yields_partial_refund(client):
    dispute_id = client.post(
        "/disputes",
        json={
            "transaction_id": "txn_S5_5",
            "merchant_name": "Flow Test Co",
            "amount": "300.00",
            "currency": "USD",
            "reason": "Item not as described",  # -> 4553
        },
    ).json()["id"]

    client.post(
        f"/disputes/{dispute_id}/evidence",
        json={
            "uploader": "cardholder",
            "type": "TEXT",
            "credibility": "CUSTOMER_STATEMENT",
            "summary": "Not what was listed.",
        },
    )
    r = client.post(
        f"/disputes/{dispute_id}/evidence",
        json={
            "uploader": "merchant",
            "type": "TEXT",
            "credibility": "MERCHANT_STATEMENT",
            "summary": "Listing was accurate.",
        },
    )
    assert r.status_code == 201

    latest = client.get(f"/disputes/{dispute_id}/recommendation").json()[-1]
    assert latest["recommendation"] == "PARTIAL_REFUND"
    assert latest["percentage"] == 50
    assert latest["engine_recommendation"] == "Partial Refund"
    assert latest["missing_evidence"] == []


def test_decision_endpoint_returns_latest_recommendation(client):
    dispute_id = client.post(
        "/disputes",
        json={
            "transaction_id": "txn_S5_6",
            "merchant_name": "Flow Test Co",
            "amount": "50.00",
            "currency": "USD",
            "reason": "Duplicate charge",  # -> 4512
        },
    ).json()["id"]

    client.post(
        f"/disputes/{dispute_id}/evidence",
        json={
            "uploader": "merchant",
            "type": "SYSTEM_RECORD",
            "credibility": "VERIFIED_TRANSACTION",
            "summary": "Only one charge on record.",
        },
    )

    r = client.get(f"/disputes/{dispute_id}/decision")
    assert r.status_code == 200
    decision = r.json()
    assert decision["engine_recommendation"] == "Reject Refund"
    assert decision["reason_code"] == "4512"


def test_decision_endpoint_escalates_unmapped_reason_code(client):
    dispute_id = client.post(
        "/disputes",
        json={
            "transaction_id": "txn_S5_7",
            "merchant_name": "Flow Test Co",
            "amount": "20.00",
            "currency": "USD",
            "reason": "Other",
        },
    ).json()["id"]

    client.post(
        f"/disputes/{dispute_id}/evidence",
        json={
            "uploader": "cardholder",
            "type": "TEXT",
            "credibility": "CUSTOMER_STATEMENT",
            "summary": "Charge doesn't match any standard dispute reason.",
        },
    )

    r = client.get(f"/disputes/{dispute_id}/decision")
    assert r.status_code == 200
    decision = r.json()
    assert decision["engine_recommendation"] == "Escalate for Manual Review"
    assert decision["confidence"] == 20
    assert decision["category"] is None


def test_unmapped_reason_code_escalates_for_manual_review(client):
    dispute_id = client.post(
        "/disputes",
        json={
            "transaction_id": "txn_S5_8",
            "merchant_name": "Flow Test Co",
            "amount": "60.00",
            "currency": "USD",
            "reason": "Other",  # no reason code mapping
        },
    ).json()["id"]

    client.post(
        f"/disputes/{dispute_id}/evidence",
        json={
            "uploader": "cardholder",
            "type": "TEXT",
            "credibility": "CUSTOMER_STATEMENT",
            "summary": "Some claim.",
        },
    )

    latest = client.get(f"/disputes/{dispute_id}/recommendation").json()[-1]
    assert latest["engine_recommendation"] == "Escalate for Manual Review"
    assert latest["category"] is None


def test_regression_full_dispute_lifecycle(client):
    dispute_id = client.post(
        "/disputes",
        json={
            "transaction_id": "txn_REG_LIFECYCLE",
            "merchant_name": "Regression Co",
            "amount": "80.00",
            "currency": "USD",
            "reason": "Item not received",
        },
    ).json()["id"]

    timeline = client.get(f"/disputes/{dispute_id}/timeline").json()
    assert [e["title"] for e in timeline] == ["Dispute Created"]

    assert client.get(f"/disputes/{dispute_id}").json()["status"] == "OPEN"

    client.post(
        f"/disputes/{dispute_id}/evidence",
        json={
            "uploader": "cardholder",
            "type": "TEXT",
            "credibility": "CUSTOMER_STATEMENT",
            "summary": "Never showed up.",
        },
    )
    assert client.get(f"/disputes/{dispute_id}").json()["status"] == "IN_NEGOTIATION"
    timeline = client.get(f"/disputes/{dispute_id}/timeline").json()
    titles = [e["title"] for e in timeline]
    assert titles == ["Dispute Created", "Evidence Uploaded", "Recommendation Pending"]
    timestamps = [e["timestamp"] for e in timeline]
    assert timestamps == sorted(timestamps)

    # Accepting (one party only): must NOT resolve the dispute yet.
    r = client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "cardholder"})
    assert r.status_code == 200
    assert r.json()["accepted_by"] == ["cardholder"]
    assert client.get(f"/disputes/{dispute_id}").json()["status"] == "IN_NEGOTIATION"

    # Second party accepts: NOW it resolves.
    r = client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "merchant"})
    assert r.status_code == 200
    assert set(r.json()["accepted_by"]) == {"cardholder", "merchant"}
    assert client.get(f"/disputes/{dispute_id}").json()["status"] == "RESOLVED"


def test_regression_evidence_endpoints(client):
    r = client.get("/disputes/dsp_8841/evidence")
    assert r.status_code == 200
    assert len(r.json()) == 5  # unchanged seeded evidence count


def test_regression_404_for_unknown_dispute(client):
    assert client.get("/disputes/does_not_exist").status_code == 404
    assert client.get("/disputes/does_not_exist/timeline").status_code == 404
    assert client.get("/disputes/does_not_exist/evidence").status_code == 404
    assert client.get("/disputes/does_not_exist/recommendation").status_code == 404
    assert client.get("/disputes/does_not_exist/decision").status_code == 404


def test_regression_accept_with_no_recommendation_yet_returns_400(client):
    dispute_id = client.post(
        "/disputes",
        json={
            "transaction_id": "txn_REG_NOACCEPT",
            "merchant_name": "Regression Co",
            "amount": "15.00",
            "currency": "USD",
            "reason": "Other",
        },
    ).json()["id"]
    r = client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "cardholder"})
    assert r.status_code == 400


def test_regression_websocket_still_broadcasts_after_sprint5_changes(client):
    with client.websocket_connect("/ws/disputes/dsp_8841?role=cardholder") as ws:
        types = [ws.receive_json()["type"] for _ in range(4)]
        assert types == [
            "dispute_updated",
            "evidence_updated",
            "timeline_updated",
            "recommendation_updated",
        ]
        presence = ws.receive_json()
        assert presence == {"type": "presence_updated", "payload": {"roles": ["cardholder"]}}
