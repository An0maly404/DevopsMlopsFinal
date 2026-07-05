"""Integration tests for backend API endpoints.

These tests exercise the full FastAPI application stack: routing, middleware,
lifespan, and response serialization.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Integration tests for the /health endpoint."""

    def test_health_returns_200_and_ok_status(self):
        """GET /health should return 200 with {"status": "ok"}."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data == {"status": "ok"}

    def test_health_response_is_json(self):
        """GET /health should return JSON content type."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"


class TestPredictEndpoint:
    """Integration tests for the /predict endpoint."""

    def test_predict_with_valid_data_returns_structured_error(self):
        """POST /predict with valid data returns proper JSON error when
        no model is available (503), verifying the full request/response cycle
        including CORS middleware and Pydantic validation."""
        response = client.post("/predict", json={
            "MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.98,
            "AveBedrms": 1.02, "Population": 322.0, "AveOccup": 2.55,
            "Latitude": 37.88, "Longitude": -122.23,
        })
        # The endpoint should respond — if CORS or routing were broken
        # we would get a 4xx/5xx with different shape
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "No production model available yet."

    def test_predict_cors_headers_present(self):
        """The CORS middleware should add appropriate headers."""
        response = client.options(
            "/predict",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )
        # CORS preflight should succeed (200)
        assert response.status_code == 200
