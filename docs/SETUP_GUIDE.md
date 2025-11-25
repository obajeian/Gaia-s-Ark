# Gaia's Ark - Setup Guide

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.10+ installed
- Node.js 18+ installed
- Git (optional)

### 1. Backend Setup
```bash
# Navigate to backend directory
cd "Gaia's Ark Platform/backend"

# Install Python dependencies
pip install -r requirements.txt

# Initialize data and train model
python data_preprocessor.py
python carbon_model.py

# Start the API server
python api.py
```

The backend will be available at `http://localhost:8000`

### 2. Frontend Setup
```bash
# Navigate to frontend directory (new terminal)
cd "Gaia's Ark Platform/frontend"

# Install Node.js dependencies
npm install

# Start the development server
npm start
```

The frontend will be available at `http://localhost:3000`

### 3. Verify Installation
1. Open browser to `http://localhost:3000`
2. You should see a 3D Earth with mangrove data points
3. Click on any green/yellow/red point to see carbon analysis
4. Check API documentation at `http://localhost:8000/docs`

## Detailed Installation

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Ubuntu 18.04+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Internet**: Required for initial package downloads only

### Backend Installation

#### Step 1: Python Environment
```bash
# Check Python version
python --version  # Should be 3.10+

# Create virtual environment (recommended)
python -m venv gaia_env

# Activate virtual environment
# Windows:
gaia_env\Scripts\activate
# macOS/Linux:
source gaia_env/bin/activate
```

#### Step 2: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

**Dependencies installed:**
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pandas (data processing)
- Scikit-learn (machine learning)
- NumPy (numerical computing)
- Pydantic (data validation)

#### Step 3: Initialize Database
```bash
# Process existing mangrove data
python data_preprocessor.py
```

**Expected output:**
```
INFO:__main__:Loaded 100 mangrove records
INFO:__main__:Saved 100 records to database
Processed 100 mangrove records
```

#### Step 4: Train ML Model
```bash
# Train carbon prediction model
python carbon_model.py
```

**Expected output:**
```
INFO:__main__:Model trained - MSE: 125.45, R²: 0.847
INFO:__main__:Model saved to models/carbon_model.pkl
Model training completed: {'mse': 125.45, 'r2': 0.847}
```

#### Step 5: Start API Server
```bash
# Start FastAPI server
python api.py
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Frontend Installation

#### Step 1: Node.js Environment
```bash
# Check Node.js version
node --version  # Should be 18+
npm --version   # Should be 8+
```

#### Step 2: Install Dependencies
```bash
cd frontend
npm install
```

**Dependencies installed:**
- React (UI framework)
- Three.js (3D graphics)
- Axios (HTTP client)

#### Step 3: Start Development Server
```bash
npm start
```

**Expected output:**
```
Compiled successfully!

You can now view gaia-ark-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.100:3000
```

## Configuration

### Backend Configuration
Create `.env` file in backend directory:
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database Configuration
DATABASE_PATH=data/gaia_ark.db

# Model Configuration
MODEL_PATH=models/carbon_model.pkl

# Logging
LOG_LEVEL=INFO
```

### Frontend Configuration
No configuration required for local development.

## Data Setup

### Using Existing Data
The system includes sample mangrove data from Kenya's coast. No additional setup required.

### Adding Custom Data

#### CSV Format
Create `custom_data.csv`:
```csv
region,latitude,longitude,mangrove_area,biomass_density,soil_carbon,year,species
Custom_001,-4.0435,39.6682,2.5,150.0,45.0,2025,Rhizophora mucronata
Custom_002,-4.1234,39.7890,1.8,120.0,38.0,2025,Avicennia marina
```

#### Load Custom Data
```python
# In data_preprocessor.py, modify load_mangrove_data()
def load_mangrove_data(self, data_path="path/to/custom_data.csv"):
    df = pd.read_csv(data_path)
    # Process as needed
    return df
```

### GeoJSON Format
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "region": "Custom_001",
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

## Testing

### Backend Testing
```bash
# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/stats
curl http://localhost:8000/mapdata

# Test prediction endpoint
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "mangrove_area": 2.5,
    "biomass_density": 150.0,
    "soil_carbon": 45.0,
    "latitude": -4.0435,
    "longitude": 39.6682
  }'
```

### Frontend Testing
1. Open `http://localhost:3000`
2. Verify 3D Earth loads
3. Check data points are visible
4. Test region selection
5. Verify data panel updates

## Troubleshooting

### Common Issues

#### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue**: `sqlite3.OperationalError: no such table: mangrove_data`
```bash
# Solution: Initialize database
python data_preprocessor.py
```

**Issue**: `FileNotFoundError: [Errno 2] No such file or directory: 'models/carbon_model.pkl'`
```bash
# Solution: Train model
python carbon_model.py
```

#### Frontend Issues

**Issue**: `npm ERR! code ENOENT`
```bash
# Solution: Install Node.js dependencies
npm install
```

**Issue**: `Module not found: Can't resolve 'three'`
```bash
# Solution: Install Three.js
npm install three
```

**Issue**: Network error when fetching data
- Verify backend is running on port 8000
- Check CORS configuration
- Ensure no firewall blocking

### Performance Issues

#### Slow API Response
```bash
# Check database size
ls -la data/gaia_ark.db

# Monitor API logs
tail -f api.log
```

#### Slow 3D Rendering
- Reduce number of data points
- Lower Three.js quality settings
- Check WebGL support in browser

### Logging

#### Backend Logs
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Frontend Logs
Open browser developer tools (F12) and check console for errors.

## Development

### Code Structure
```
backend/
├── api.py              # FastAPI application
├── data_preprocessor.py # Data loading and processing
├── carbon_model.py     # ML model training and prediction
├── utils/
│   ├── geo_utils.py    # Geospatial utilities
│   └── model_utils.py  # ML utilities
├── models/             # Trained model artifacts
└── data/              # Database and data files

frontend/
├── src/
│   ├── App.js         # Main application
│   ├── components/
│   │   ├── EarthViewer.js  # 3D Earth component
│   │   └── DataPanel.js    # Analytics panel
│   └── App.css        # Styling
└── public/            # Static assets
```

### Adding New Features

#### Backend: New API Endpoint
```python
@app.get("/new-endpoint")
async def new_endpoint():
    return {"message": "New feature"}
```

#### Frontend: New Component
```javascript
import React from 'react';

const NewComponent = () => {
  return <div>New Feature</div>;
};

export default NewComponent;
```

### Database Management

#### View Data
```bash
# Install SQLite browser or use command line
sqlite3 data/gaia_ark.db
.tables
SELECT * FROM mangrove_data LIMIT 5;
```

#### Backup Data
```bash
# Backup database
cp data/gaia_ark.db data/gaia_ark_backup.db

# Backup models
cp -r models/ models_backup/
```

## Production Deployment (Future)

### Docker Deployment
```bash
# Build containers
docker build -t gaia-ark-backend ./backend
docker build -t gaia-ark-frontend ./frontend

# Run with docker-compose
docker-compose up -d
```

### Cloud Deployment
- Backend: AWS Lambda, Google Cloud Run, or Heroku
- Frontend: Netlify, Vercel, or AWS S3 + CloudFront
- Database: AWS RDS, Google Cloud SQL, or managed SQLite

### Environment Variables
```bash
# Production backend
export API_HOST=0.0.0.0
export API_PORT=8000
export DATABASE_URL=postgresql://...
export MODEL_STORAGE_URL=s3://...

# Production frontend
export REACT_APP_API_URL=https://api.gaias-ark.com
```

## Support

### Getting Help
1. Check this setup guide
2. Review error logs
3. Check GitHub issues (if available)
4. Contact development team

### Reporting Issues
Include:
- Operating system and version
- Python/Node.js versions
- Error messages and logs
- Steps to reproduce

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request