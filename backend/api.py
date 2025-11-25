from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from carbon_model import CarbonModel
from data_preprocessor import DataPreprocessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Gaia's Ark - Mangrove Carbon Sequestration API",
    description="Local-first environmental intelligence platform for mangrove carbon analysis",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
carbon_model = CarbonModel()
data_processor = DataPreprocessor()

class PredictionRequest(BaseModel):
    mangrove_area: float
    biomass_density: float
    soil_carbon: float
    latitude: float
    longitude: float

class MangroveData(BaseModel):
    region: str
    latitude: float
    longitude: float
    mangrove_area: float
    biomass_density: float
    soil_carbon: float
    year: int
    species: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize data and models on startup"""
    try:
        # Process data if database doesn't exist
        df = data_processor.process_data()
        
        # Train model if it doesn't exist
        carbon_model.load_model()
        
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.get("/")
async def root():
    return {
        "message": "Gaia's Ark - Mangrove Carbon Sequestration Platform",
        "version": "2.1.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    from datetime import datetime
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/predict")
async def predict_carbon(request: PredictionRequest):
    """Predict carbon sequestration for given mangrove parameters"""
    try:
        result = carbon_model.predict_carbon(
            request.mangrove_area,
            request.biomass_density,
            request.soil_carbon,
            request.latitude,
            request.longitude
        )
        return result
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mapdata")
async def get_map_data():
    """Get all mangrove data for map visualization"""
    try:
        # Use absolute path for database to avoid CWD issues
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "data", "gaia_ark.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mangrove_data")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        
        # Add carbon predictions for each record
        results = []
        for row in rows:
            record = dict(zip(columns, row))
            prediction = carbon_model.predict_carbon(
                record['mangrove_area'],
                record['biomass_density'],
                record['soil_carbon'],
                record['latitude'],
                record['longitude']
            )
            
            results.append({
                "region": record['region'],
                "latitude": record['latitude'],
                "longitude": record['longitude'],
                "mangrove_area": record['mangrove_area'],
                "biomass_density": record['biomass_density'],
                "soil_carbon": record['soil_carbon'],
                "species": record.get('species', 'Unknown'),
                "predicted_carbon": prediction['predicted_carbon_stock'],
                "confidence": prediction['confidence_score']
            })
        
        return {"data": results, "count": len(results)}
    
    except Exception as e:
        logger.error(f"Map data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/insight/{region}")
async def get_region_insight(region: str):
    """Get detailed insights for a specific region"""
    try:
        # Use absolute path for database
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "data", "gaia_ark.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mangrove_data WHERE region = ?", (region,))
        row_data = cursor.fetchone()
        columns = [description[0] for description in cursor.description]
        conn.close()
        
        if not row_data:
            raise HTTPException(status_code=404, detail="Region not found")
        
        row = dict(zip(columns, row_data))
        prediction = carbon_model.predict_carbon(
            row['mangrove_area'],
            row['biomass_density'],
            row['soil_carbon'],
            row['latitude'],
            row['longitude']
        )
        
        return {
            "region": region,
            "location": {"latitude": row['latitude'], "longitude": row['longitude']},
            "mangrove_characteristics": {
                "area_hectares": row['mangrove_area'],
                "biomass_density": row['biomass_density'],
                "soil_carbon": row['soil_carbon'],
                "species": row.get('species', 'Unknown')
            },
            "carbon_analysis": prediction,
            "recommendations": [
                "Monitor biomass density changes",
                "Protect soil carbon stores",
                "Prevent deforestation"
            ]
        }
    
    except Exception as e:
        logger.error(f"Insight error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_statistics():
    """Get platform statistics"""
    try:
        # Use absolute path for database
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "data", "gaia_ark.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mangrove_data")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        
        # Calculate statistics
        total_carbon = 0
        total_area = 0
        total_biomass = 0
        species_set = set()
        
        for row in rows:
            record = dict(zip(columns, row))
            prediction = carbon_model.predict_carbon(
                record['mangrove_area'],
                record['biomass_density'],
                record['soil_carbon'],
                record['latitude'],
                record['longitude']
            )
            total_carbon += prediction['predicted_carbon_stock']
            total_area += record['mangrove_area']
            total_biomass += record['biomass_density']
            if record.get('species'):
                species_set.add(record['species'])
        
        return {
            "total_regions": len(rows),
            "total_area_hectares": round(total_area, 2),
            "total_carbon_stock_tonnes": round(total_carbon, 2),
            "average_biomass_density": round(total_biomass / len(rows) if rows else 0, 2),
            "species_count": len(species_set)
        }
    
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/info")
async def get_model_info():
    """Get information about the ML model"""
    try:
        feature_importance = carbon_model.get_feature_importance()
        return {
            "model_type": "Random Forest Regressor",
            "features": list(feature_importance.keys()),
            "feature_importance": feature_importance,
            "status": "trained" if carbon_model.model else "not_trained"
        }
    except Exception as e:
        logger.error(f"Model info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)