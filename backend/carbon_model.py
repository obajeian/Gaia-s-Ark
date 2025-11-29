import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from pathlib import Path
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CarbonModel:
    def __init__(self, model_path=None):
        base_dir = Path(__file__).resolve().parent
        if model_path is None:
            self.model_path = base_dir / "models" / "carbon_model.pkl"
        else:
            self.model_path = Path(model_path)
            
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.feature_columns = ['mangrove_area', 'biomass_density', 'soil_carbon', 'latitude', 'longitude']
        
    def load_data(self, db_path=None):
        """Load training data from database"""
        if db_path is None:
            base_dir = Path(__file__).resolve().parent.parent
            db_path = base_dir / "data" / "gaia_ark.db"
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mangrove_data")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        
        # Convert to list of dictionaries
        data = []
        for row in rows:
            record = dict(zip(columns, row))
            data.append(record)
        return data
    
    def calculate_carbon_stock(self, row):
        """Calculate carbon stock using established formulas"""
        # Above-ground biomass (AGB) estimation
        agb = row['biomass_density'] * row['mangrove_area'] * 10000  # Convert ha to m²
        
        # Below-ground biomass (typically 20-30% of AGB for mangroves)
        bgb = agb * 0.25
        
        # Total biomass carbon (carbon content ~47% of biomass)
        biomass_carbon = (agb + bgb) * 0.47
        
        # Soil carbon
        soil_carbon_total = row['soil_carbon'] * row['mangrove_area']
        
        # Total carbon stock (tonnes C)
        total_carbon = (biomass_carbon / 1000) + soil_carbon_total
        
        return total_carbon
    
    def prepare_features(self, data):
        """Prepare features and target variables"""
        # Calculate carbon stock for each record
        for record in data:
            record['carbon_stock'] = self.calculate_carbon_stock(record)
            record['area_biomass_interaction'] = record['mangrove_area'] * record['biomass_density']
            record['coastal_distance'] = abs(record['longitude'] - 39.5)
        
        # Create feature matrix
        feature_cols = self.feature_columns + ['area_biomass_interaction', 'coastal_distance']
        X = np.array([[record[col] for col in feature_cols] for record in data])
        y = np.array([record['carbon_stock'] for record in data])
        
        return X, y, data
    
    def train_model(self):
        """Train the carbon prediction model"""
        data = self.load_data()
        X, y, _ = self.prepare_features(data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Random Forest model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"Model trained - MSE: {mse:.2f}, R²: {r2:.3f}")
        
        # Save model
        joblib.dump(self.model, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
        
        return {'mse': mse, 'r2': r2}
    
    def load_model(self):
        """Load trained model"""
        try:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                logger.info("Model loaded successfully")
            else:
                logger.warning("No trained model found. Training new model...")
                self.train_model()
        except Exception as e:
            logger.error(f"Error loading model: {e}. Retraining...")
            self.train_model()
    
    def predict_carbon(self, mangrove_area, biomass_density, soil_carbon, latitude, longitude):
        try:
            if self.model is None:
                self.load_model()
            
            # Prepare features
            area_biomass_interaction = mangrove_area * biomass_density
            coastal_distance = abs(longitude - 39.5)
            
            features = np.array([[
                mangrove_area, biomass_density, soil_carbon, latitude, longitude,
                area_biomass_interaction, coastal_distance
            ]])
            
            prediction = self.model.predict(features)[0]
            
            # Calculate confidence (simplified)
            # Basic heuristic: higher confidence for values closer to training mean (approx 50-150 range)
            confidence = min(0.95, max(0.6, 1.0 - (abs(prediction - 100) / 200)))
            
            return {
                'predicted_carbon_stock': round(prediction, 2),
                'confidence_score': round(confidence, 3),
                'change_rate': round(np.random.uniform(-2, 5), 2)  # Simulated change rate
            }
        except Exception as e:
            logger.error(f"Error in predict_carbon: {e}")
            # Return a safe fallback or re-raise depending on requirements. 
            # For now, re-raising to let API handle it, but logging first.
            raise e
    
    def get_feature_importance(self):
        """Get feature importance from trained model"""
        if self.model is None:
            self.load_model()
        
        feature_names = self.feature_columns + ['area_biomass_interaction', 'coastal_distance']
        importance = self.model.feature_importances_
        
        return dict(zip(feature_names, importance))

if __name__ == "__main__":
    model = CarbonModel()
    metrics = model.train_model()
    print(f"Model training completed: {metrics}")
    
    # Test prediction
    result = model.predict_carbon(2.5, 150, 45, -4.0, 39.6)
    print(f"Test prediction: {result}")