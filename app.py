from flask import Flask, jsonify, request
from flasgger import Swagger
import json
import pandas as pd

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
        description: CSV path
    """
    df = data_generator.generate_data()
    csv_path = 'synthetic_data.csv'
    df.to_csv(csv_path, index=False)
    return jsonify({'csv': csv_path})


@app.route('/predict', methods=['POST'])
def predict():
    """Train model and return failure probabilities for provided data
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: data
        schema:
          type: array
          items:
            type: object
    responses:
      200:
        description: Prediction results
    """
    data = request.get_json() or []
    if not data:
        df = pd.read_csv('synthetic_data.csv')
        X = df[["machine", "temperature", "vibration"]]
    else:
        df = pd.DataFrame(data)
        X = df[["machine", "temperature", "vibration"]]
    model = predictive_model.train_model()
    proba = model.predict_proba(X)[:, 1]
    df['failure_risk'] = proba
    return df.to_json(orient='records')


@app.route('/schedule', methods=['POST'])
def schedule_endpoint():
    """Run scheduler
    ---
    responses:
      200:
        description: schedule JSON
    """
    jobs = scheduler.build_jobs()
    try:
        sched = scheduler.schedule(jobs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    path = 'schedule.json'
    with open(path, 'w') as f:
        json.dump(sched, f)
    return jsonify(sched)


@app.route('/simulate', methods=['POST'])
def simulate_endpoint():
    """Run simulation
    ---
    responses:
      200:
        description: Simulation results
    """
    try:
        res = simulation.simulate('schedule.json')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(res)


if __name__ == '__main__':
    app.run(debug=True)
