# AI-Driven Predictive Maintenance & Adaptive Production Scheduler

Prototype project demonstrating data generation, predictive maintenance using ML, production scheduling with MIP, simulation and a simple dashboard.

## Setup

### Python
1. Create virtual environment and install requirements.
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Generate data
```bash
python data_generator.py
```

3. Train predictive model
```bash
python predictive_model.py
```

4. Run scheduler (requires Gurobi installed/licensed)
```bash
python scheduler.py
```

5. Run simulation
```bash
python simulation.py
```

6. Start API
```bash
python app.py
```

### Frontend
Use Node.js to install dependencies and run the dashboard.
```bash
cd dashboard
npm install
npm start
```

The React app expects the Flask backend on `http://localhost:5000`.

## Files
- `data_generator.py` – create synthetic machine data.
- `predictive_model.py` – train RandomForest model to predict failures.
- `scheduler.py` – build and solve maintenance/production schedule with Gurobi.
- `simulation.py` – discrete event simulation via SimPy.
- `app.py` – Flask API exposing pipeline endpoints.
- `dashboard/` – React single-page application displaying heatmaps and schedule.

## Requirements
See `requirements.txt` and `dashboard/package.json` for Python and JavaScript dependencies.
