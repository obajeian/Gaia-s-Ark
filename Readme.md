# 🌍 Gaia's Ark - Mangrove Carbon Sequestration MVP v2.1

A local-first, zero-cost environmental intelligence platform focused on mangrove carbon sequestration analysis. Built with machine learning and interactive 3D visualization for research and conservation planning.

## 🌟 Key Features

- **🌍 3D Earth Visualization**: Interactive globe using Three.js WebGL
- **🧠 ML-Powered Predictions**: Random Forest model for carbon sequestration
- **📊 Real-time Analytics**: Instant carbon stock calculations and confidence scores
- **🗄️ Local Database**: SQLite-powered data storage (zero external dependencies)
- **🚀 FastAPI Backend**: High-performance REST API with automatic documentation
- **🌐 Google Earth Engine**: Optional GEE integration for satellite data
- **💰 Zero Cost**: Completely offline-capable, no paid services required

## 🏗️ Clean Architecture

```
Gaia's Ark Platform/
├── backend/                    # Python FastAPI Backend
│   ├── api.py                 # Main FastAPI application
│   ├── data_preprocessor.py   # Data loading and validation
│   ├── carbon_model.py        # ML model training and prediction
│   ├── gee_connector.py       # Google Earth Engine integration
│   ├── utils/
│   │   ├── geo_utils.py       # Geospatial calculations
│   │   └── model_utils.py     # ML utilities
│   ├── models/               # Trained ML artifacts
│   └── requirements.txt      # Python dependencies
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── App.js            # Main application
│   │   ├── App.css           # Dark theme styling
│   │   └── components/
│   │       ├── EarthViewer.js # 3D Earth (Three.js)
│   │       └── DataPanel.js   # Analytics panel
│   └── package.json          # Node.js dependencies
├── data/                      # Local Data Storage
│   ├── processed/            # Processed GeoJSON files
│   └── raw/                  # Raw CSV data
├── docs/                      # Documentation
└── scripts/                   # Utility scripts
    └── monitor_gee_tasks.py   # GEE task monitoring
```

## 🚀 Quick Start

### Option 1: One-Click Launch
```bash
cd "Gaia's Ark Platform"
python run_system.py
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python data_preprocessor.py
python carbon_model.py
python api.py
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

## 🌐 Google Earth Engine Setup (Optional)

1. **Create GEE Account**: Visit https://earthengine.google.com/
2. **Authenticate**: Run `earthengine authenticate`
3. **Set Project ID**: Update `project_id` in `gee_connector.py`
4. **Enable GEE Data**: Set `use_gee=True` in data_preprocessor.py

## 🌐 Access Points

- **🎮 Main Application**: http://localhost:3000
- **📡 API Documentation**: http://localhost:8000/docs
- **📊 API Health Check**: http://localhost:8000/health

## 🧠 Machine Learning Pipeline

- **Algorithm**: Random Forest Regressor (100 trees)
- **Features**: Area, biomass density, soil carbon, location
- **Target**: Carbon stock prediction (tonnes C)
- **Performance**: R² = 0.847, RMSE = 11.2 tonnes

## 📡 API Endpoints

- `GET /health` - System health check
- `GET /stats` - Platform statistics
- `GET /mapdata` - All mangrove data for visualization
- `POST /predict` - Carbon prediction for parameters
- `GET /insight/{region}` - Detailed region analysis
- `GET /model/info` - ML model information

## 🎮 User Interface

### 3D Earth Viewer
- Interactive globe with mangrove data points
- Color-coded by carbon sequestration potential
- Click regions for detailed analysis

### Analytics Panel
- Platform statistics and region details
- Carbon analysis with ML predictions
- Conservation recommendations

## 📚 Documentation

- **📖 [Setup Guide](docs/SETUP_GUIDE.md)**: Detailed installation instructions
- **🏗️ [Architecture Overview](docs/ARCHITECTURE_OVERVIEW.md)**: System design and data flow
- **⚙️ [Technical Specification](docs/TECHNICAL_SPECIFICATION.md)**: API and ML specifications
- **🤖 [Model Card](docs/MODEL_CARD.md)**: ML model documentation and limitations

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.