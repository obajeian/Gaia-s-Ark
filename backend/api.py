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
async def get_map_data(year: Optional[int] = 2025):
    """Get all mangrove data for map visualization, filtered by year"""
    try:
        # Use absolute path for database to avoid CWD issues
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "data", "gaia_ark.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if year:
            cursor.execute("SELECT * FROM mangrove_data WHERE year = ?", (year,))
        else:
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
                "year": record['year'],
                "species": record.get('species', 'Unknown'),
                "predicted_carbon": prediction['predicted_carbon_stock'],
                "confidence": prediction['confidence_score']
            })
        
        return {"data": results, "count": len(results), "year": year}
    
    except Exception as e:
        logger.error(f"Map data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/insight/{region}")
async def get_region_insight(region: str):
    """Get detailed insights for a specific region, including history"""
    try:
        # Use absolute path for database
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "data", "gaia_ark.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Fetch all years for this region, sorted by year
        cursor.execute("SELECT * FROM mangrove_data WHERE region = ? ORDER BY year ASC", (region,))
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        
        if not rows:
            raise HTTPException(status_code=404, detail="Region not found")
        
        history = []
        latest_record = None
        
        for row_data in rows:
            row = dict(zip(columns, row_data))
            prediction = carbon_model.predict_carbon(
                row['mangrove_area'],
                row['biomass_density'],
                row['soil_carbon'],
                row['latitude'],
                row['longitude']
            )
            
            record_entry = {
                "year": row['year'],
                "mangrove_area": row['mangrove_area'],
                "biomass_density": row['biomass_density'],
                "soil_carbon": row['soil_carbon'],
                "predicted_carbon": prediction['predicted_carbon_stock']
            }
            history.append(record_entry)
            latest_record = row # Last one is latest due to sort
            
        # Analyze trend
        trend = "stable"
        if len(history) > 1:
            first = history[0]['predicted_carbon']
            last = history[-1]['predicted_carbon']
            if last > first * 1.1:
                trend = "increasing"
            elif last < first * 0.9:
                trend = "decreasing"
        
        return {
            "region": region,
            "location": {"latitude": latest_record['latitude'], "longitude": latest_record['longitude']},
            "latest_stats": {
                "year": latest_record['year'],
                "area_hectares": latest_record['mangrove_area'],
                "biomass_density": latest_record['biomass_density'],
                "species": latest_record.get('species', 'Unknown')
            },
            "carbon_trend": trend,
            "history": history,
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
    """Get platform statistics (based on latest year 2025)"""
    try:
        # Use absolute path for database
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "data", "gaia_ark.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Only get latest year stats
        cursor.execute("SELECT * FROM mangrove_data WHERE year = 2025")
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
            "species_count": len(species_set),
            "data_year": 2025
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