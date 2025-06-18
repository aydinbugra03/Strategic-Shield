# AI-Driven Predictive Maintenance & Adaptive Production Scheduler

This prototype demonstrates a small pipeline for generating synthetic machine sensor data, predicting failures, scheduling production and maintenance, and simulating shop-floor operations.

## Structure

- `data_generator.py` – create synthetic temperature/vibration data with failure labels.
- `predictive_model.py` – train a RandomForest model to predict failures.
- `scheduler.py` – build an optimization model with Gurobi to schedule jobs and preventive maintenance.
- `simulation.py` – run a discrete-event simulation of the machines using SimPy.
- `app.py` – Flask API providing endpoints for each step with Swagger docs.
- `dashboard/` – React front-end visualising risk and schedules.

## Setup

### Python

Install dependencies (preferably in a virtual environment):

```bash
pip install -r requirements.txt
```

### Node / React

Install front-end dependencies:

```bash
cd dashboard
npm install
```

## Usage

1. **Generate Data**
   ```bash
   python data_generator.py
   ```
   Creates `synthetic_data.csv`.

2. **Train Predictive Model**
   ```bash
   python predictive_model.py
   ```
   Trains RandomForest and saves `failure_model.joblib`.

3. **Run Scheduler**
   ```bash
   python scheduler.py
   ```
   Optimizes maintenance & production and outputs `schedule.json`.

4. **Run Simulation**
   ```bash
   python simulation.py
   ```
   Generates `simulation_report.json` with downtime statistics.

5. **Start the API**
   ```bash
   python app.py
   ```
   Swagger UI is available at `http://localhost:5000/apidocs`.

6. **Dashboard**
   ```bash
   cd dashboard
   npm start
   ```
   Opens a React app showing the heatmap and Gantt chart.

## Requirements

See `requirements.txt` for Python packages and `dashboard/package.json` for React packages.
