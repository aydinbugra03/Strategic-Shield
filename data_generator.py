import os
import numpy as np
import pandas as pd


def generate_sensor_data(output_path: str = "data/synthetic_data.csv", seed: int = 42) -> str:
    """Generate synthetic sensor data for 3 machines at 6 hour intervals."""
    np.random.seed(seed)
    start = pd.Timestamp("2023-01-01")
    periods = 120  # 30 days of data in 6 hour intervals
    freq = "6H"
    records = []
    for machine in range(1, 4):
        for i in range(periods):
            ts = start + pd.Timedelta(hours=6 * i)
            temperature = np.random.normal(loc=70, scale=5)
            vibration = np.random.normal(loc=0.5, scale=0.1)
            # Failure probability increases with high temp and vibration
            prob = 1 / (1 + np.exp(-(temperature - 75) * 0.2 - (vibration - 0.5) * 5))
            failure = np.random.binomial(1, prob * 0.1)  # keep failures relatively rare
            records.append([
                ts,
                machine,
                round(temperature, 2),
                round(vibration, 3),
                failure,
            ])
    df = pd.DataFrame(records, columns=["timestamp", "machine_id", "temperature", "vibration", "failure"])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Synthetic data saved to {output_path}")
    return output_path


if __name__ == "__main__":
    generate_sensor_data()
