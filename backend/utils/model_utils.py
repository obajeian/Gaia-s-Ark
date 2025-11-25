import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ModelUtils:
    @staticmethod
    def calculate_carbon_coefficients():
        """Standard carbon calculation coefficients for mangroves"""
        return {
            'biomass_to_carbon': 0.47,  # 47% carbon content in biomass
            'belowground_ratio': 0.25,  # BGB = 25% of AGB for mangroves
            'wood_density': {
                'Rhizophora mucronata': 0.85,
                'Avicennia marina': 0.65,
                'Ceriops tagal': 0.75,
                'default': 0.70
            },
            'allometric_a': 0.251,  # Allometric equation coefficient
            'allometric_b': 2.46    # Allometric equation exponent
        }
    
    @staticmethod
    def estimate_biomass_from_dbh(dbh_cm: float, species: str = 'default') -> float:
        """Estimate above-ground biomass from diameter at breast height"""
        coeffs = ModelUtils.calculate_carbon_coefficients()
        wood_density = coeffs['wood_density'].get(species, coeffs['wood_density']['default'])
        
        # Allometric equation: AGB = a * (ρ * D²H)^b
        # Simplified for mangroves: AGB = a * ρ * D^b
        agb = coeffs['allometric_a'] * wood_density * (dbh_cm ** coeffs['allometric_b'])
        return agb
    
    @staticmethod
    def calculate_total_carbon(agb_kg: float, soil_carbon_tha: float, area_ha: float) -> dict:
        """Calculate total carbon stock from biomass and soil carbon"""
        coeffs = ModelUtils.calculate_carbon_coefficients()
        
        # Below-ground biomass
        bgb_kg = agb_kg * coeffs['belowground_ratio']
        
        # Total biomass carbon
        biomass_carbon_kg = (agb_kg + bgb_kg) * coeffs['biomass_to_carbon']
        biomass_carbon_tonnes = biomass_carbon_kg / 1000
        
        # Soil carbon
        soil_carbon_tonnes = soil_carbon_tha * area_ha
        
        # Total carbon
        total_carbon = biomass_carbon_tonnes + soil_carbon_tonnes
        
        return {
            'agb_tonnes': agb_kg / 1000,
            'bgb_tonnes': bgb_kg / 1000,
            'biomass_carbon_tonnes': biomass_carbon_tonnes,
            'soil_carbon_tonnes': soil_carbon_tonnes,
            'total_carbon_tonnes': total_carbon
        }
    
    @staticmethod
    def validate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
        """Calculate model validation metrics"""
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)
        
        # Mean Absolute Percentage Error
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        return {
            'mae': round(mae, 3),
            'mse': round(mse, 3),
            'rmse': round(rmse, 3),
            'r2': round(r2, 3),
            'mape': round(mape, 2)
        }
    
    @staticmethod
    def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
        """Add engineered features for better model performance"""
        df = df.copy()
        
        # Interaction features
        df['area_biomass'] = df['mangrove_area'] * df['biomass_density']
        df['biomass_soil'] = df['biomass_density'] * df['soil_carbon']
        
        # Location-based features
        df['coastal_distance'] = np.abs(df['longitude'] - 39.5)  # Distance from main coast
        df['latitude_abs'] = np.abs(df['latitude'])
        
        # Density categories
        df['biomass_category'] = pd.cut(
            df['biomass_density'], 
            bins=[0, 100, 150, 200, np.inf], 
            labels=['Low', 'Medium', 'High', 'Very High']
        )
        
        # Area categories
        df['area_category'] = pd.cut(
            df['mangrove_area'], 
            bins=[0, 1, 5, 10, np.inf], 
            labels=['Small', 'Medium', 'Large', 'Very Large']
        )
        
        return df
    
    @staticmethod
    def save_model_artifacts(model, scaler, feature_names, model_dir="models"):
        """Save model and preprocessing artifacts"""
        model_dir = Path(model_dir)
        model_dir.mkdir(exist_ok=True)
        
        # Save model
        joblib.dump(model, model_dir / "carbon_model.pkl")
        
        # Save scaler if provided
        if scaler:
            joblib.dump(scaler, model_dir / "scaler.pkl")
        
        # Save feature names
        joblib.dump(feature_names, model_dir / "feature_names.pkl")
        
        logger.info(f"Model artifacts saved to {model_dir}")
    
    @staticmethod
    def load_model_artifacts(model_dir="models"):
        """Load model and preprocessing artifacts"""
        model_dir = Path(model_dir)
        
        model = joblib.load(model_dir / "carbon_model.pkl")
        
        scaler = None
        if (model_dir / "scaler.pkl").exists():
            scaler = joblib.load(model_dir / "scaler.pkl")
        
        feature_names = joblib.load(model_dir / "feature_names.pkl")
        
        return model, scaler, feature_names
    
    @staticmethod
    def calculate_uncertainty(predictions: np.ndarray, model_std: float = None) -> np.ndarray:
        """Calculate prediction uncertainty"""
        if model_std is None:
            # Use coefficient of variation as uncertainty estimate
            model_std = np.std(predictions) / np.mean(predictions)
        
        # Simple uncertainty based on prediction magnitude
        uncertainty = predictions * model_std * np.random.uniform(0.8, 1.2, len(predictions))
        return np.abs(uncertainty)
    
    @staticmethod
    def generate_confidence_intervals(predictions: np.ndarray, uncertainty: np.ndarray, confidence: float = 0.95):
        """Generate confidence intervals for predictions"""
        z_score = 1.96 if confidence == 0.95 else 2.58  # 95% or 99%
        
        lower_bound = predictions - (z_score * uncertainty)
        upper_bound = predictions + (z_score * uncertainty)
        
        return {
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'confidence_level': confidence
        }