# AI-Driven Predictive Maintenance & Adaptive Production Scheduler

This prototype demonstrates a pipeline for generating synthetic sensor data, training a failure prediction model, scheduling maintenance/production with Gurobi, simulating execution with SimPy, and visualising results via a Flask API and a React dashboard.

## Setup

### Python
1. Create a virtual environment (optional).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Front End
```
cd dashboard
npm install
```

## Running the Pipeline

1. **Generate data**
   ```bash
   python data_generator.py
   ```
2. **Train predictive model**
   ```bash
   python predictive_model.py
   ```
3. **Run scheduler**
   ```bash
   python scheduler.py
   ```
4. **Run simulation**
   ```bash
   python simulation.py
   ```
5. **Start API**
   ```bash
   python app.py
   ```
6. **Start React dashboard**
   ```bash
   cd dashboard && npm start
   ```

The dashboard provides buttons to trigger the API endpoints and displays the risk heatmap, schedule Gantt chart, and simulation report.
