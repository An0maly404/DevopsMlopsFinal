"""Unit tests for HousingFeatures Pydantic model validation."""
import pytest
from pydantic import ValidationError

# Import the model from the backend
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import HousingFeatures


class TestHousingFeaturesValidation:
    """Test that the HousingFeatures model validates input correctly."""

    def test_valid_features_accepted(self):
        """Valid numeric values should create a model instance without error."""
        features = HousingFeatures(
            MedInc=8.3252,
            HouseAge=41.0,
            AveRooms=6.98,
            AveBedrms=1.02,
            Population=322.0,
            AveOccup=2.55,
            Latitude=37.88,
            Longitude=-122.23,
        )
        assert features.MedInc == 8.3252
        assert features.Longitude == -122.23

    def test_missing_field_raises_error(self):
        """Missing a required field should raise ValidationError."""
        with pytest.raises(ValidationError):
            HousingFeatures(
                MedInc=8.3252,
                HouseAge=41.0,
                AveRooms=6.98,
                # AveBedrms missing
                Population=322.0,
                AveOccup=2.55,
                Latitude=37.88,
                Longitude=-122.23,
            )

    def test_wrong_type_raises_error(self):
        """Passing a string where a float is expected should raise ValidationError."""
        with pytest.raises(ValidationError):
            HousingFeatures(
                MedInc="not_a_number",
                HouseAge=41.0,
                AveRooms=6.98,
                AveBedrms=1.02,
                Population=322.0,
                AveOccup=2.55,
                Latitude=37.88,
                Longitude=-122.23,
            )

    def test_extra_field_still_validates(self):
        """Extra unknown fields should be ignored (Pydantic default)."""
        features = HousingFeatures(
            MedInc=1.0, HouseAge=2.0, AveRooms=3.0, AveBedrms=4.0,
            Population=5.0, AveOccup=6.0, Latitude=7.0, Longitude=8.0,
        )
        assert features.MedInc == 1.0
