# Gaia's Ark - Technical Specification

## API Specification

### Base URL
```
http://localhost:8000
```

### Authentication
None required for local deployment.

### Content Type
All requests and responses use `application/json`.

## API Endpoints

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### 2. Platform Statistics
```http
GET /stats
```

**Response:**
```json
{
  "total_regions": 100,
  "total_area_hectares": 2500.75,
  "total_carbon_stock_tonnes": 12500.50,
  "average_biomass_density": 150.25,
  "species_count": 5
}
```

### 3. Map Data
```http
GET /mapdata
```

**Response:**
```json
{
  "data": [
    {
      "region": "Kenya_Coast_001",
      "latitude": -4.0435,
      "longitude": 39.6682,
      "mangrove_area": 2.5,
      "biomass_density": 150.0,
      "soil_carbon": 45.0,
      "species": "Rhizophora mucronata",
      "predicted_carbon": 75.25,
      "confidence": 0.85
    }
  ],
  "count": 100
}
```

### 4. Carbon Prediction
```http
POST /predict
```

**Request Body:**
```json
{
  "mangrove_area": 2.5,
  "biomass_density": 150.0,
  "soil_carbon": 45.0,
  "latitude": -4.0435,
  "longitude": 39.6682
}
```

**Response:**
```json
{
  "predicted_carbon_stock": 75.25,
  "confidence_score": 0.85,
  "change_rate": 2.3
}
```

### 5. Region Insights
```http
GET /insight/{region}
```

**Response:**
```json
{
  "region": "Kenya_Coast_001",
  "location": {
    "latitude": -4.0435,
    "longitude": 39.6682
  },
  "mangrove_characteristics": {
    "area_hectares": 2.5,
    "biomass_density": 150.0,
    "soil_carbon": 45.0,
    "species": "Rhizophora mucronata"
  },
  "carbon_analysis": {
    "predicted_carbon_stock": 75.25,
    "confidence_score": 0.85,
    "change_rate": 2.3
  },
  "recommendations": [
    "Monitor biomass density changes",
    "Protect soil carbon stores",
    "Prevent deforestation"
  ]
}
```

### 6. Model Information
```http
GET /model/info
```

**Response:**
```json
{
  "model_type": "Random Forest Regressor",
  "features": [
    "mangrove_area",
    "biomass_density", 
    "soil_carbon",
    "latitude",
    "longitude",
    "area_biomass_interaction",
    "coastal_distance"
  ],
  "feature_importance": {
    "biomass_density": 0.35,
    "soil_carbon": 0.25,
    "mangrove_area": 0.20,
    "area_biomass_interaction": 0.12,
    "coastal_distance": 0.05,
    "latitude": 0.02,
    "longitude": 0.01
  },
  "status": "trained"
}
```

## Machine Learning Design

### Model Architecture
- **Algorithm**: Random Forest Regressor
- **Framework**: Scikit-learn
- **Features**: 7 engineered features
- **Target**: Carbon stock (tonnes C)

### Feature Engineering
```python
# Base features
features = [
    'mangrove_area',      # Hectares
    'biomass_density',    # kg/m²
    'soil_carbon',        # tonnes C/ha
    'latitude',           # Decimal degrees
    'longitude'           # Decimal degrees
]

# Derived features
area_biomass_interaction = mangrove_area * biomass_density
coastal_distance = abs(longitude - 39.5)  # Distance from Kenya coast
```

### Model Parameters
```python
RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
```

### Training Process
1. **Data Loading**: Load from SQLite database
2. **Feature Engineering**: Create interaction terms
3. **Train/Test Split**: 80/20 split
4. **Model Training**: Fit Random Forest
5. **Validation**: Calculate metrics (MSE, R²)
6. **Model Persistence**: Save to `.pkl` file

### Prediction Pipeline
```python
def predict_carbon(area, biomass, soil_carbon, lat, lon):
    # Feature preparation
    features = prepare_features(area, biomass, soil_carbon, lat, lon)
    
    # Model prediction
    prediction = model.predict([features])[0]
    
    # Confidence calculation
    confidence = calculate_confidence(prediction, features)
    
    # Change rate estimation
    change_rate = estimate_change_rate(features)
    
    return {
        'predicted_carbon_stock': prediction,
        'confidence_score': confidence,
        'change_rate': change_rate
    }
```

## Data Formats

### Database Schema
```sql
CREATE TABLE mangrove_data (
    id INTEGER PRIMARY KEY,
    region TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    mangrove_area REAL NOT NULL,
    biomass_density REAL NOT NULL,
    soil_carbon REAL NOT NULL,
    year INTEGER NOT NULL,
    species TEXT,
    family TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Input Data Format (CSV)
```csv
region,latitude,longitude,mangrove_area,biomass_density,soil_carbon,year,species
Kenya_Coast_001,-4.0435,39.6682,2.5,150.0,45.0,2025,Rhizophora mucronata
Kenya_Coast_002,-4.1234,39.7890,1.8,120.0,38.0,2025,Avicennia marina
```

### GeoJSON Format
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "region": "Kenya_Coast_001",
        "biomass_density": 150.0,
        "soil_carbon": 45.0,
        "species": "Rhizophora mucronata"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [39.6682, -4.0435]
      }
    }
  ]
}
```

## Frontend Specifications

### Component Architecture
```
App
├── EarthViewer (Three.js 3D Globe)
│   ├── Scene Management
│   ├── Camera Controls
│   ├── Data Point Rendering
│   └── Interaction Handling
└── DataPanel (Analytics Display)
    ├── Statistics Grid
    ├── Region Details
    ├── Carbon Analysis
    └── Recommendations
```

### Three.js Implementation
```javascript
// Earth geometry
const earthGeometry = new THREE.SphereGeometry(1, 64, 64);
const earthMaterial = new THREE.MeshPhongMaterial({
  color: 0x2233ff,
  shininess: 100,
  transparent: true,
  opacity: 0.8
});

// Data point rendering
data.forEach(point => {
  const lat = (point.latitude * Math.PI) / 180;
  const lon = (point.longitude * Math.PI) / 180;
  const radius = 1.02;
  
  const x = radius * Math.cos(lat) * Math.cos(lon);
  const y = radius * Math.sin(lat);
  const z = radius * Math.cos(lat) * Math.sin(lon);
  
  // Color based on carbon value
  const carbonValue = point.predicted_carbon || 50;
  const normalizedCarbon = Math.min(1, carbonValue / 100);
  const color = new THREE.Color();
  color.setHSL(0.3 * normalizedCarbon, 1, 0.5);
});
```

### State Management
```javascript
// App-level state
const [mangroveData, setMangroveData] = useState([]);
const [selectedRegion, setSelectedRegion] = useState(null);
const [loading, setLoading] = useState(true);
const [stats, setStats] = useState(null);

// API communication
const fetchData = async () => {
  const response = await fetch('http://localhost:8000/mapdata');
  const result = await response.json();
  setMangroveData(result.data || []);
};
```

## Performance Specifications

### Backend Performance
- **Startup Time**: < 5 seconds
- **API Response Time**: < 200ms (95th percentile)
- **Memory Usage**: < 500MB
- **CPU Usage**: < 50% (single core)
- **Concurrent Requests**: 50+ requests/second

### Frontend Performance
- **Initial Load**: < 10 seconds
- **Frame Rate**: 60 FPS (WebGL rendering)
- **Memory Usage**: < 300MB
- **Bundle Size**: < 2MB (gzipped)

### Database Performance
- **Query Time**: < 50ms (typical)
- **Database Size**: < 100MB (100k records)
- **Concurrent Connections**: 10+

## Error Handling

### API Error Responses
```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Common Error Codes
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (region not found)
- `500`: Internal Server Error (model/database error)

### Frontend Error Handling
```javascript
try {
  const response = await fetch('/api/endpoint');
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const data = await response.json();
} catch (error) {
  console.error('API Error:', error);
  // Show user-friendly error message
}
```

## Security Specifications

### Input Validation
```python
class PredictionRequest(BaseModel):
    mangrove_area: float = Field(gt=0, le=1000)
    biomass_density: float = Field(gt=0, le=500)
    soil_carbon: float = Field(gt=0, le=200)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
```

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Deployment Specifications

### System Requirements
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.10+
- **Node.js**: 18+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB available space
- **Network**: Internet for initial setup only

### Environment Variables
```bash
# Backend (.env)
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_PATH=data/gaia_ark.db
MODEL_PATH=models/carbon_model.pkl
LOG_LEVEL=INFO

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

### Docker Configuration (Future)
```dockerfile
# Backend Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend Dockerfile  
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```