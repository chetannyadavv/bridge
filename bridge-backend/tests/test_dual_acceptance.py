"""
Bug fix tests: a dispute must only become RESOLVED once BOTH the
cardholder and merchant have accepted the settlement recommendation.
Previously, dispute.status was set to RESOLVED on ANY single acceptance
— meaning the counterparty's screen (reading the same dispute.status
field) would incorrectly show "Dispute resolved" even though they
themselves had never agreed to anything.
"""


def _dispute_with_recommendation(client, suffix):
    dispute_id = client.post(
        "/disputes",
        json={
            "transaction_id": f"txn_DUAL_{suffix}",
            "merchant_name": "Dual Accept Co",
            "amount": "64.20",
            "currency": "USD",
            "reason": "Item not received",
        },
    ).json()["id"]
    client.post(
        f"/disputes/{dispute_id}/evidence",
        json={
            "uploader": "cardholder",
            "type": "TEXT",
            "credibility": "CUSTOMER_STATEMENT",
            "summary": "Never arrived.",
        },
    )
    return dispute_id


def test_single_cardholder_accept_does_not_resolve(client):
    dispute_id = _dispute_with_recommendation(client, "1")

    r = client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "cardholder"})
    assert r.status_code == 200
    assert r.json()["accepted_by"] == ["cardholder"]

    dispute = client.get(f"/disputes/{dispute_id}").json()
    assert dispute["status"] != "RESOLVED"


def test_single_merchant_accept_does_not_resolve(client):
    dispute_id = _dispute_with_recommendation(client, "2")

    r = client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "merchant"})
    assert r.status_code == 200
    assert r.json()["accepted_by"] == ["merchant"]

    dispute = client.get(f"/disputes/{dispute_id}").json()
    assert dispute["status"] != "RESOLVED"


def test_both_parties_accepting_resolves_cardholder_then_merchant(client):
    dispute_id = _dispute_with_recommendation(client, "3")

    client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "cardholder"})
    assert client.get(f"/disputes/{dispute_id}").json()["status"] != "RESOLVED"

    r = client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "merchant"})
    assert set(r.json()["accepted_by"]) == {"cardholder", "merchant"}
    assert client.get(f"/disputes/{dispute_id}").json()["status"] == "RESOLVED"


def test_both_parties_accepting_resolves_merchant_then_cardholder(client):
    """Order must not matter — same as the Decision Engine's own
    determinism requirement, applied here to the acceptance flow."""
    dispute_id = _dispute_with_recommendation(client, "4")

    client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "merchant"})
    assert client.get(f"/disputes/{dispute_id}").json()["status"] != "RESOLVED"

    r = client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "cardholder"})
    assert set(r.json()["accepted_by"]) == {"cardholder", "merchant"}
    assert client.get(f"/disputes/{dispute_id}").json()["status"] == "RESOLVED"


def test_duplicate_accept_from_same_role_is_idempotent(client):
    dispute_id = _dispute_with_recommendation(client, "5")

    client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "cardholder"})
    r = client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "cardholder"})

    assert r.json()["accepted_by"] == ["cardholder"]
    assert client.get(f"/disputes/{dispute_id}").json()["status"] != "RESOLVED"


def test_timeline_reflects_partial_then_full_acceptance(client):
    dispute_id = _dispute_with_recommendation(client, "6")

    client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "cardholder"})
    timeline = client.get(f"/disputes/{dispute_id}/timeline").json()
    titles = [e["title"] for e in timeline]
    assert "Settlement Accepted" in titles
    assert "Dispute Resolved" not in titles

    client.post(f"/disputes/{dispute_id}/recommendation/accept", json={"role": "merchant"})
    timeline = client.get(f"/disputes/{dispute_id}/timeline").json()
    titles = [e["title"] for e in timeline]
    assert titles.count("Settlement Accepted") == 1
    assert titles.count("Dispute Resolved") == 1
