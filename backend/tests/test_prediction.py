"""Unit tests for prediction response format and post-processing."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestPredictionFormat:
    """Test the prediction endpoint response structure."""

    def test_predict_returns_json_with_prediction_key_when_no_model(self):
        """Even without a model, the response should be JSON with the correct
        error structure (503 with 'detail' key)."""
        response = client.post("/predict", json={
            "MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.98,
            "AveBedrms": 1.02, "Population": 322.0, "AveOccup": 2.55,
            "Latitude": 37.88, "Longitude": -122.23,
        })
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        assert len(data["detail"]) > 0

    def test_predict_rejects_missing_fields(self):
        """Sending incomplete data should return 422 Unprocessable Entity."""
        response = client.post("/predict", json={
            "MedInc": 8.3252,
        })
        assert response.status_code == 422

    def test_predict_rejects_non_numeric_values(self):
        """Sending string values where floats are expected should return 422."""
        response = client.post("/predict", json={
            "MedInc": "hello", "HouseAge": 41.0, "AveRooms": 6.98,
            "AveBedrms": 1.02, "Population": 322.0, "AveOccup": 2.55,
            "Latitude": 37.88, "Longitude": -122.23,
        })
        assert response.status_code == 422
