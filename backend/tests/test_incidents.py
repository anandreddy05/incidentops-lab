from datetime import UTC, datetime


def test_create_incident(client):
    payload = {
        "title": "Payment API returning HTTP 500",
        "description": "Payment requests are failing.",
        "severity": "high",
        "source": "application",
        "fingerprint": "payment-api-http-500",
        "first_seen_at": datetime.now(UTC).isoformat(),
        "last_seen_at": datetime.now(UTC).isoformat(),
    }

    response = client.post("/api/v1/incidents", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == payload["title"]
    assert data["severity"] == "high"
    assert data["status"] == "open"
    assert data["source"] == "application"
    assert data["fingerprint"] == "payment-api-http-500"
    assert "id" in data


def test_get_incident(client):
    payload = {
        "title": "Payment API failure",
        "description": "Payment requests are failing.",
        "severity": "high",
        "source": "application",
        "fingerprint": "payment-api-test",
        "first_seen_at": datetime.now(UTC).isoformat(),
        "last_seen_at": datetime.now(UTC).isoformat(),
    }

    created = client.post("/api/v1/incidents", json=payload)
    assert created.status_code == 201

    incident_id = created.json()["id"]

    response = client.get(f"/api/v1/incidents/{incident_id}")

    assert response.status_code == 200
    assert response.json()["id"] == incident_id
    assert response.json()["title"] == payload["title"]


def test_get_nonexistent_incident(client):
    incident_id = "11111111-1111-4111-8111-111111111111"

    response = client.get(f"/api/v1/incidents/{incident_id}")

    assert response.status_code == 404


def test_list_incidents(client):
    payload = {
        "title": "Database connection failure",
        "description": "Database connections are timing out.",
        "severity": "critical",
        "source": "application",
        "fingerprint": "database-connection-test",
        "first_seen_at": datetime.now(UTC).isoformat(),
        "last_seen_at": datetime.now(UTC).isoformat(),
    }

    created = client.post("/api/v1/incidents", json=payload)
    assert created.status_code == 201

    response = client.get("/api/v1/incidents")

    assert response.status_code == 200

    incidents = response.json()

    assert isinstance(incidents, list)
    assert len(incidents) == 1
    assert incidents[0]["title"] == payload["title"]


def test_partial_update_incident(client):
    payload = {
        "title": "Payment API failure",
        "description": "Payment requests are failing.",
        "severity": "high",
        "source": "application",
        "fingerprint": "payment-patch-test",
        "first_seen_at": datetime.now(UTC).isoformat(),
        "last_seen_at": datetime.now(UTC).isoformat(),
    }

    created = client.post("/api/v1/incidents", json=payload)
    incident_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"status": "investigating"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "investigating"
    assert data["title"] == payload["title"]
    assert data["severity"] == "high"


def test_invalid_incident_status(client):
    payload = {
        "status": "invalid",
    }

    response = client.patch(
        "/api/v1/incidents/11111111-1111-4111-8111-111111111111",
        json=payload,
    )

    assert response.status_code == 422


def test_empty_incident_update(client):
    response = client.patch(
        "/api/v1/incidents/11111111-1111-4111-8111-111111111111",
        json={},
    )

    assert response.status_code == 422


def test_list_incidents_pagination(client):
    for i in range(3):
        payload = {
            "title": f"Test incident {i}",
            "description": "Pagination test",
            "severity": "medium",
            "source": "application",
            "fingerprint": f"pagination-{i}",
            "first_seen_at": datetime.now(UTC).isoformat(),
            "last_seen_at": datetime.now(UTC).isoformat(),
        }

        response = client.post("/api/v1/incidents", json=payload)
        assert response.status_code == 201

    response = client.get("/api/v1/incidents?skip=0&limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get("/api/v1/incidents?skip=2&limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_invalid_pagination(client):
    response = client.get("/api/v1/incidents?skip=-1")
    assert response.status_code == 422

    response = client.get("/api/v1/incidents?limit=0")
    assert response.status_code == 422

    response = client.get("/api/v1/incidents?limit=101")
    assert response.status_code == 422


def test_patch_null_required_field(client):
    created = client.post(
        "/api/v1/incidents",
        json={
            "title": "Payment API failure",
            "description": "Payment requests failing",
            "severity": "high",
            "source": "application",
            "first_seen_at": datetime.now(UTC).isoformat(),
            "last_seen_at": datetime.now(UTC).isoformat(),
        },
    )

    incident_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"title": None},
    )

    assert response.status_code == 422


def test_patch_clear_description(client):
    created = client.post(
        "/api/v1/incidents",
        json={
            "title": "Payment API failure",
            "description": "Payment requests failing",
            "severity": "high",
            "source": "application",
            "first_seen_at": datetime.now(UTC).isoformat(),
            "last_seen_at": datetime.now(UTC).isoformat(),
        },
    )

    incident_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"description": None},
    )

    assert response.status_code == 200
    assert response.json()["description"] is None


def test_invalid_incident_timestamp_range(client):
    payload = {
        "title": "Invalid timestamp incident",
        "description": "Testing timestamp validation",
        "severity": "high",
        "source": "application",
        "first_seen_at": "2026-11-24T12:00:00Z",
        "last_seen_at": "2026-11-24T11:00:00Z",
    }

    response = client.post("/api/v1/incidents", json=payload)

    assert response.status_code == 422
