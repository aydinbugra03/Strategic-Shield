import pandas as pd
import numpy as np


def generate_sensor_data(days=30, freq='6H', machines=3, seed=42):
    """Generate synthetic sensor data for multiple machines."""
    np.random.seed(seed)
    timestamps = pd.date_range(start=pd.Timestamp.today().floor('D'),
                               periods=int(24/6*days),
                               freq=freq)
    data = []
    for machine in range(1, machines + 1):
        temp_base = 60 + 10 * np.random.rand()
        vib_base = 5 + np.random.rand()
        for ts in timestamps:
            temp = temp_base + np.random.randn() * 5
            vib = vib_base + np.random.randn() * 0.5
            # Failure probability increases with temperature and vibration
            prob_fail = 1 / (1 + np.exp(-(0.05*(temp-70) + 0.5*(vib-5))))
            fail = np.random.rand() < prob_fail * 0.1  # scale down for realism
            data.append({
                'timestamp': ts,
                'machine': f'M{machine}',
                'temperature': temp,
                'vibration': vib,
                'failure': int(fail)
            })
    df = pd.DataFrame(data)
    return df


def main():
    df = generate_sensor_data()
    csv_path = 'synthetic_data.csv'
    df.to_csv(csv_path, index=False)
    print(f"Generated data saved to {csv_path}")


if __name__ == '__main__':
    main()
