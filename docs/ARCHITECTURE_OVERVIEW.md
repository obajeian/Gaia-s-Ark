# Gaia's Ark - Architecture Overview

## System Architecture

Gaia's Ark is a local-first, zero-cost mangrove carbon sequestration intelligence platform built with a modular, scalable architecture.

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Three.js)             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   EarthViewer   │  │   DataPanel     │  │  Controls   │ │
│  │   (3D Globe)    │  │  (Analytics)    │  │   (UI)      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │      API        │  │  Carbon Model   │  │ Data Proc.  │ │
│  │   (FastAPI)     │  │ (RandomForest)  │  │ (Pandas)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   DATA LAYER (SQLite)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Mangrove Data   │  │   ML Models     │  │   Cache     │ │
│  │   (SQLite)      │  │   (.pkl)        │  │  (Memory)   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Flow

### 1. Data Processing Pipeline
```
Raw Data (GeoJSON) → DataPreprocessor → Validation → SQLite Database
                                    ↓
                            Feature Engineering → ML Training → Model Artifacts
```

### 2. Prediction Pipeline
```
User Input → API Endpoint → Carbon Model → Prediction + Confidence → Response
```

### 3. Visualization Pipeline
```
Database → API → Frontend → Three.js → 3D Earth + Data Points
```

## Core Components

### Backend Components

#### 1. Data Preprocessor (`data_preprocessor.py`)
- **Purpose**: Load, validate, and prepare mangrove data
- **Input**: GeoJSON files, CSV data
- **Output**: Cleaned SQLite database
- **Key Functions**:
  - `load_mangrove_data()`: Load from various sources
  - `validate_schema()`: Data quality checks
  - `save_to_db()`: Store processed data

#### 2. Carbon Model (`carbon_model.py`)
- **Purpose**: ML-powered carbon sequestration prediction
- **Algorithm**: Random Forest Regressor
- **Features**: Area, biomass density, soil carbon, location
- **Output**: Carbon stock prediction + confidence score
- **Key Functions**:
  - `train_model()`: Train ML model
  - `predict_carbon()`: Generate predictions
  - `calculate_carbon_stock()`: Physics-based calculations

#### 3. API Layer (`api.py`)
- **Purpose**: RESTful API for frontend communication
- **Framework**: FastAPI
- **Endpoints**:
  - `GET /mapdata`: All mangrove data for visualization
  - `POST /predict`: Carbon prediction for parameters
  - `GET /insight/{region}`: Detailed region analysis
  - `GET /stats`: Platform statistics

#### 4. Utility Modules
- **geo_utils.py**: Geospatial calculations, distance functions
- **model_utils.py**: ML utilities, validation metrics

### Frontend Components

#### 1. EarthViewer (`EarthViewer.js`)
- **Purpose**: 3D Earth visualization with mangrove data
- **Technology**: Three.js WebGL
- **Features**:
  - Interactive 3D globe
  - Mangrove data points with color coding
  - Mouse controls (rotation, zoom)
  - Click-to-select regions

#### 2. DataPanel (`DataPanel.js`)
- **Purpose**: Display analytics and insights
- **Features**:
  - Platform statistics
  - Region details
  - Carbon analysis with confidence
  - ML-generated recommendations

#### 3. App (`App.js`)
- **Purpose**: Main application orchestration
- **Features**:
  - State management
  - API communication
  - Component coordination

## Data Flow

### 1. Initialization
1. Backend starts and processes existing data
2. ML model trains on available data
3. Frontend loads and displays 3D Earth
4. API serves initial statistics

### 2. User Interaction
1. User clicks on mangrove region in 3D view
2. Frontend sends region ID to API
3. Backend retrieves data and generates ML prediction
4. Response includes detailed analysis and recommendations
5. DataPanel updates with new information

### 3. Prediction Workflow
1. Extract region characteristics (area, biomass, soil carbon, location)
2. Apply feature engineering (interactions, derived features)
3. ML model generates carbon stock prediction
4. Calculate confidence score based on model uncertainty
5. Generate change rate estimate
6. Return structured prediction response

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **SQLite**: Lightweight, serverless database
- **Pandas**: Data manipulation and analysis
- **Scikit-learn**: Machine learning algorithms
- **NumPy**: Numerical computing

### Frontend
- **React**: Component-based UI framework
- **Three.js**: 3D graphics and WebGL
- **Axios**: HTTP client for API communication

### Development
- **Python 3.10+**: Backend runtime
- **Node.js 18+**: Frontend build tools
- **Git**: Version control

## Deployment Architecture

### Local Development
```
localhost:3000 (React Dev Server) → localhost:8000 (FastAPI)
                                        ↓
                                   SQLite Database
                                        ↓
                                   ML Model Files
```

### Production (Future)
```
CDN/Static Hosting → API Gateway → Container/Lambda
                                        ↓
                                   Database Service
                                        ↓
                                   Model Storage
```

## Security Considerations

### Current (Local-First)
- No external API dependencies
- Local data storage only
- No authentication required
- CORS configured for localhost

### Future Enhancements
- API authentication (JWT)
- Data encryption at rest
- Rate limiting
- Input validation and sanitization

## Performance Characteristics

### Backend
- **Startup Time**: ~2-3 seconds (model loading)
- **Prediction Latency**: ~50-100ms per request
- **Memory Usage**: ~200-500MB (model + data)
- **Concurrent Users**: 10-50 (single instance)

### Frontend
- **Initial Load**: ~2-5 seconds (Three.js initialization)
- **Rendering**: 60 FPS (WebGL optimized)
- **Memory Usage**: ~100-300MB (3D scene + data)
- **Browser Support**: Modern browsers with WebGL

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Model artifacts can be shared
- Database can be replicated
- Frontend is static (CDN-ready)

### Vertical Scaling
- ML model can utilize multiple CPU cores
- Database queries are optimized
- Memory usage is bounded
- GPU acceleration possible (future)

## Monitoring and Observability

### Current Implementation
- Basic logging (Python logging)
- Error handling and validation
- Performance timing (manual)

### Future Enhancements
- Structured logging (JSON)
- Metrics collection (Prometheus)
- Distributed tracing
- Health checks and alerts