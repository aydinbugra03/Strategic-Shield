from flask import Flask, request, jsonify
from flasgger import Swagger

import data_generator
import predictive_model
import scheduler
import simulation

app = Flask(__name__)
swagger = Swagger(app)


@app.route('/generate', methods=['POST'])
def generate():
    """Generate synthetic sensor data
    ---
    post:
      description: Generate new sensor data
      responses:
        200:
          description: path to csv
    """
    path = data_generator.generate_sensor_data()
    return jsonify({'csv_path': path})


@app.route('/predict', methods=['POST'])
def predict():
    """Predict failure risks for posted data
    ---
    post:
      parameters:
        - in: body
          name: payload
          schema:
            type: array
            items:
              type: object
              properties:
                temperature:
                  type: number
                vibration:
                  type: number
                machine_id:
                  type: integer
      responses:
        200:
          description: predictions
    """
    payload = request.get_json()
    model = predictive_model.joblib.load('models/predictive_model.joblib')
    X = [[p['temperature'], p['vibration'], p['machine_id']] for p in payload]
    probs = model.predict_proba(X)[:, 1].tolist()
    return jsonify({'predictions': probs})


@app.route('/schedule', methods=['POST'])
def schedule_route():
    """Run the scheduler and return JSON schedule
    ---
    post:
      responses:
        200:
          description: schedule
    """
    path = scheduler.demo_schedule()
    with open(path) as f:
        data = f.read()
    return jsonify({'schedule': data})


@app.route('/simulate', methods=['POST'])
def simulate_route():
    """Run simulation based on schedule and predictive model
    ---
    post:
      responses:
        200:
          description: simulation results
    """
    result = simulation.simulate()
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
