# Strategic Shield: Decision Support System

Strategic Shield is a sophisticated decision support system designed for optimizing the strategic allocation of missile assets. It features a modern web interface with interactive mapping capabilities and uses advanced mathematical optimization with exponential constraints to determine the most effective deployment of various missile types across a network of sites to counter threats in different geopolitical conflict scenarios.

## ✅ **Project Status: FULLY OPERATIONAL**

The system has been successfully implemented and tested with the following results:
- **Individual Scenarios**: ✅ All 3 scenarios working (Greece-Bulgaria, Armenia-Russia, Israel-US)
- **Robust Optimization**: ✅ Probability-weighted optimization across all scenarios
- **Database Pipeline**: ✅ Excel → SQLite → Gurobi → SQLite → API
- **API Endpoints**: ✅ All endpoints functional and tested
- **Interactive Frontend**: ✅ React-based web interface with real-time mapping
- **Complete Integration**: ✅ Full stack application with modern UI/UX
- **Test Results**: 
  - Individual scenarios: ~360 missiles per scenario
  - Robust optimization: Single allocation optimized for all scenarios

## Key Features

- **🗺️ Interactive Mapping:** Real-time visualization of deployment sites and targets with color-coded markers
- **🎮 Modern Web Interface:** React-based frontend with intuitive scenario selection and optimization controls
- **📊 Data-Driven Pipeline:** Complete automation from Excel input to web API output
- **🎯 Scenario-Based Analysis:** Multiple conflict scenarios with target-specific optimization
- **🌍 Geopolitical Intelligence:** Qatar sites automatically inactive in US-Israel Coalition (realistic alliance dynamics)
- **🧮 Advanced Mathematical Model:** Uses logarithmic and exponential constraints for exact diminishing returns calculations
- **⚡ High-Performance Solver:** Gurobi-powered nonconvex optimization with exact `0.9^N` and `0.8^M` calculations
- **🔗 RESTful API:** Clean HTTP endpoints for integration with frontend applications
- **📈 Real-Time Results:** Instant access to optimization results through database queries

## Technology Stack

### Backend
- **Backend:** Python 3.8+
- **Mathematical Solver:** Gurobi (with NonConvex=2 for exponential constraints)
- **Data Processing:** pandas, NumPy
- **Database:** SQLite (production-ready, portable)
- **API Framework:** FastAPI with automatic OpenAPI documentation
- **Database ORM:** SQLAlchemy 2.0

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite for fast development and builds
- **Mapping:** Leaflet with React-Leaflet for interactive maps
- **HTTP Client:** Axios for API communication
- **Styling:** Modern CSS with component-based architecture

## Complete System Architecture

```
📊 Excel File (data.xlsx)
    ↓ [ETL Pipeline]
💾 SQLite Database (strategic_shield.db)
    ↓ [Optimization Engine]
🧮 Gurobi Solver (Mathematical Model)
    ↓ [Results Storage]
💾 SQLite Database (Allocation Table)
    ↓ [FastAPI Backend]
🌐 JSON API (RESTful Endpoints)
    ↓ [React Frontend]
🗺️ Interactive Web Interface
    ├── 🔵 Deployment Sites (Blue Markers)
    ├── 🔴 Target Points (Red Markers)
    ├── 📊 Results Tables
    └── 🎛️ Control Panel
```

## Quick Start

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Initialize database and load data
python run_etl.py

# Start API server
uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Access the Application
- **Web Interface:** http://localhost:3000
- **API Documentation:** http://127.0.0.1:8000/docs

## Web Interface Features

### 🗺️ Interactive Map
- **Blue Markers (🔵):** Turkish deployment sites with capacity information
- **Gray Markers (⚫):** Qatar sites (inactive in US-Israel Coalition due to geopolitical alignment)
- **Red Markers (🔴):** Enemy targets with priority levels
- **Scenario-Specific Targets:** Automatically updates based on selected scenario
- **Robust View:** Shows all targets from all scenarios when "Robust" is selected
- **Smart Site Activation:** Qatar automatically excluded from optimization in Scenario 3
- **Geographic Accuracy:** Precise coordinate mapping for strategic visualization

### 🎛️ Control Panel
- **Scenario Selector:** Choose between 3 conflict scenarios or robust optimization
- **Optimization Button:** Run calculations with real-time loading indicators
- **Results Display:** Comprehensive tables showing missile allocation results

### 📊 Real-Time Results
- **Deployment Summary:** Site-by-site missile allocation breakdown
- **Performance Metrics:** Objective values and optimization statistics
- **Instant Updates:** Results appear immediately after optimization completion

## Mathematical Model

The system implements a sophisticated mixed-integer nonconvex optimization model:

### Objective Function
- **Attack Bonus**: `∑π_t × 10d × ∑w_m×a_m × (1-0.9^N_{t,m})/(1-0.9)`
- **Defense Bonus**: `∑δ_i × 20d × ∑w_m×a_m × (1-0.8^x_{i,m})/(1-0.8)`

### Key Constraints
1. **Site Capacity**: `∑x_{i,m} ≤ capacity_i`
2. **Missile Stock**: `∑x_{i,m} ≤ stock_m`  
3. **Minimum Defense**: `∑x_{i,m} ≥ 1` (no site left undefended)
4. **Exponential Constraints**: Exact `0.9^N` and `0.8^M` calculations using `ln/exp`

## API Endpoints

The API provides endpoints for individual scenarios and robust optimization.

### 🏠 Welcome
- **GET** `/` → `{"message": "Welcome to the Strategic Shield API"}`

### 🚀 Individual Scenario Optimization
- **POST** `/optimization/run/{scenario_id}`
- **Description:** Runs optimization for a specific scenario (1, 2, or 3)
- **Example:** `POST /optimization/run/1`

### 📊 Individual Scenario Results
- **GET** `/optimization/results/{scenario_id}`
- **Description:** Gets results for a specific scenario
- **Example:** `GET /optimization/results/1`

### 🎯 Robust Optimization
- **POST** `/optimization/run/robust`
- **Description:** Runs probability-weighted optimization across ALL scenarios
- **Probabilities Used:**
  - Greece-Bulgaria Coalition: 0.20 (NATO internal, unlikely)
  - Armenia-Russia Coalition: 0.35 (regional tension, medium)
  - Israel-US Coalition: 0.45 (Middle East dynamics, higher)

### 📈 Robust Results
- **GET** `/optimization/results/robust`
- **Description:** Gets the robust allocation that works best across all scenarios

### 🗺️ Map Data Endpoints
- **GET** `/map/deployment-sites` → All Turkish deployment sites with coordinates
- **GET** `/map/targets/{scenario_id}` → Targets for specific scenario
- **GET** `/map/targets/all` → All targets from all scenarios (for robust view)

### 📚 Interactive Documentation
- **Swagger UI:** `http://127.0.0.1:8000/docs`

## Test Results Summary

### ✅ Complete System Validation
- **Database Creation**: ✅ All tables created and populated
- **Individual Scenarios**: ✅ All 3 scenarios optimized successfully
- **Robust Optimization**: ✅ Cross-scenario optimization working
- **Qatar Intelligence**: ✅ Geopolitical site deactivation working (Scenario 3)
- **API Endpoints**: ✅ All 9 endpoints responding correctly
- **Frontend Integration**: ✅ React interface fully functional
- **Interactive Mapping**: ✅ Real-time marker updates working
- **Data Persistence**: ✅ All results saved and retrievable

### 📈 Optimization Results
**Individual Scenarios:**
- **Scenario 1** (Greece-Bulgaria): ~360 missiles, objective 6.7M
- **Scenario 2** (Armenia-Russia): ~360 missiles, optimized for eastern threats  
- **Scenario 3** (Israel-US): ~360 missiles, Qatar sites excluded (geopolitical realism)

**Robust Optimization:**
- **Cross-Scenario**: Single allocation optimized for all scenarios
- **Qatar Exclusion**: Qatar sites removed for cross-scenario compatibility
- **Realistic Probabilities**: Based on geopolitical analysis
- **Balanced Defense**: Works well regardless of which conflict occurs

### 🗺️ Map Visualization
- **Deployment Sites**: 30+ Turkish sites with blue markers
- **Qatar Intelligence**: Qatar sites show gray in US-Israel Coalition (inactive due to US alliance)
- **Target Coverage**: Scenario-specific red markers showing enemy positions
- **Real-Time Updates**: Markers update instantly when scenarios change
- **Geopolitical Accuracy**: Realistic alliance considerations in site activation
- **Geographic Accuracy**: Precise coordinate mapping for strategic planning

## Database Schema

7 main tables store all system data:
- **DeploymentSite, MissileType, MissileInventory**
- **Target, Scenario, ScenarioTarget** 
- **Allocation** (results from optimization)

## Mathematical Implementation

Uses exact exponential constraints:
- **Attack diminishing returns**: `0.9^N` via `ln/exp` constraints
- **Defense diminishing returns**: `0.8^M` via `ln/exp` constraints
- **Nonconvex solver**: Gurobi with NonConvex=2 parameter

## System Requirements

### Prerequisites
- **Python 3.8+**
- **Node.js 16+**
- **Gurobi Optimizer** with valid license

### Input Data Format
Ensure `SHIELD/data.xlsx` contains these sheets:
- **`DEPLOYMENT SITE`**: Turkish site info and priorities
- **`MISSILE TYPES`**: Missile specifications and inventory  
- **`TARGET SITE`**: Scenario targets with coordinates

## Production Deployment

The system is designed for production use with:
- **Portable Database**: SQLite for easy deployment
- **Fast Frontend**: React with Vite for optimal performance
- **RESTful API**: Scalable FastAPI backend
- **Real-time Updates**: Instant optimization results
- **Geographic Visualization**: Strategic map-based interface



---

**Strategic Shield** - Advanced Decision Support for Strategic Defense with Interactive Mapping
