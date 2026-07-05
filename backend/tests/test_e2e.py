"""End-to-end test simulating a full user prediction flow.

Simulates: user opens app → health check passes → submits housing features →
backend validates → returns prediction (or structured error if no model).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.98,
    "AveBedrms": 1.02, "Population": 322.0, "AveOccup": 2.55,
    "Latitude": 37.88, "Longitude": -122.23,
}


class TestEndToEndPredictionFlow:
    """Simulate the complete prediction flow end-to-end."""

    def test_full_flow_health_then_predict(self):
        """Step 1: Health check confirms the service is up.
        Step 2: Submit valid housing features.
        Step 3: Verify the response structure is correct.
        """
        # Step 1 — health check
        health_resp = client.get("/health")
        assert health_resp.status_code == 200
        assert health_resp.json()["status"] == "ok"

        # Step 2 — submit prediction
        predict_resp = client.post("/predict", json=VALID_PAYLOAD)

        # Step 3 — verify structured response (503 expected, no model loaded)
        assert predict_resp.status_code in (200, 503)
        data = predict_resp.json()

        if predict_resp.status_code == 200:
            assert "prediction" in data
            assert isinstance(data["prediction"], (int, float))
        else:
            assert "detail" in data
            assert len(data["detail"]) > 0

    def test_full_flow_invalid_input_handled_gracefully(self):
        """User submits bad data → backend returns 422 with validation details."""
        # Step 1 — health check
        health_resp = client.get("/health")
        assert health_resp.status_code == 200

        # Step 2 — submit invalid data (missing all required fields)
        predict_resp = client.post("/predict", json={})
        assert predict_resp.status_code == 422
        data = predict_resp.json()
        assert "detail" in data
        # Should list all missing fields
        assert len(data["detail"]) >= 8

    def test_full_flow_service_unavailable_is_handled(self):
        """When no model is loaded, the user gets a clear error message,
        not a crash or empty response."""
        # Step 1 — health check must still pass
        health_resp = client.get("/health")
        assert health_resp.status_code == 200

        # Step 2 — predict returns 503 with a human-readable message
        predict_resp = client.post("/predict", json=VALID_PAYLOAD)
        assert predict_resp.status_code == 503
        assert predict_resp.json()["detail"] == "No production model available yet."
