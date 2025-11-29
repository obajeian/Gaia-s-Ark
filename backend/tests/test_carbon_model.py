import pytest
import sys
import os
from pathlib import Path
import numpy as np

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from carbon_model import CarbonModel

class TestCarbonModel:
    @pytest.fixture
    def model(self):
        return CarbonModel(model_path="tests/test_model.pkl")

    def test_initialization(self, model):
        assert model is not None
        assert model.feature_columns == ['mangrove_area', 'biomass_density', 'soil_carbon', 'latitude', 'longitude']

    def test_calculate_carbon_stock(self, model):
        # Test with known values
        # AGB = 100 * 1 * 10000 = 1,000,000
        # BGB = 250,000
        # Biomass Carbon = 1,250,000 * 0.47 = 587,500
        # Soil Carbon = 50 * 1 = 50
        # Total = 587.5 + 50 = 637.5
        row = {
            'biomass_density': 100,
            'mangrove_area': 1,
            'soil_carbon': 50
        }
        result = model.calculate_carbon_stock(row)
        assert abs(result - 637.5) < 0.01

    def test_predict_carbon_integration(self, model):
        # This might trigger training if model doesn't exist
        result = model.predict_carbon(
            mangrove_area=10.0,
            biomass_density=150.0,
            soil_carbon=50.0,
            latitude=0.0,
            longitude=0.0
        )
        
        assert 'predicted_carbon_stock' in result
        assert 'confidence_score' in result
        assert 'change_rate' in result
        assert isinstance(result['predicted_carbon_stock'], float)
        assert result['predicted_carbon_stock'] > 0

    def test_predict_carbon_edge_cases(self, model):
        # Test with zero area
        result = model.predict_carbon(0, 0, 0, 0, 0)
        assert result['predicted_carbon_stock'] is not None

    def test_feature_importance(self, model):
        # Ensure model is loaded/trained
        model.predict_carbon(10, 150, 50, 0, 0)
        
        importance = model.get_feature_importance()
        assert isinstance(importance, dict)
        assert len(importance) > 0
        assert 'mangrove_area' in importance
