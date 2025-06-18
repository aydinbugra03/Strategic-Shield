from flask import Flask, jsonify, request
from flasgger import Swagger
import pandas as pd
import joblib
import json

import data_generator
import predictive_model
import scheduler
import simulation

app = Flask(__name__)
swagger = Swagger(app)


@app.route('/generate', methods=['POST'])
def generate():
    """Generate synthetic data
    ---
    responses:
      200:
        description: Path to CSV file
    """
    df = data_generator.generate_sensor_data()
    path = 'synthetic_data.csv'
    df.to_csv(path, index=False)
    return jsonify({'csv_path': path})


@app.route('/predict', methods=['POST'])
def predict():
    """Predict failure probability for new data
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            temperature:
              type: number
            vibration:
              type: number
    responses:
      200:
        description: Prediction result
    """
    model = joblib.load(predictive_model.MODEL_PATH)
    data = request.get_json()
    X = pd.DataFrame([data])
    prob = model.predict_proba(X)[0, 1]
    return jsonify({'failure_risk': prob})


@app.route('/schedule', methods=['POST'])
def run_schedule():
    """Run the production & maintenance scheduler
    ---
    responses:
      200:
        description: Schedule JSON
    """
    sched = scheduler.schedule()
    with open('schedule.json', 'w') as f:
        json.dump(sched, f, indent=2)
    return jsonify(sched)


@app.route('/simulate', methods=['POST'])
def run_simulation():
    """Run discrete-event simulation
    ---
    responses:
      200:
        description: Simulation report
    """
    with open('schedule.json') as f:
        sched = json.load(f)
    stats = simulation.simulate(sched)
    return jsonify(stats)


if __name__ == '__main__':
    app.run(debug=True)
