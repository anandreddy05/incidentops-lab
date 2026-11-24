from fastapi.testclient import TestClient

from incidentops_lab_api.main import app


def test_liveness_endpoint():
    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_request_id_is_returned():
    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")
