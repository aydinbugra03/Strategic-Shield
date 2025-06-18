import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_data(days: int = 30, freq_hours: int = 6, machines: int = 3) -> pd.DataFrame:
    """Generate synthetic sensor data and failure labels."""
    records = []
    start = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(days=days)
    timestamps = [start + timedelta(hours=i * freq_hours) for i in range(int(days * 24 / freq_hours))]
    for m in range(1, machines + 1):
        temp_base = 70 + 5 * np.random.randn()
        vib_base = 0.5 + 0.1 * np.random.randn()
        for ts in timestamps:
            temp = temp_base + np.random.randn() * 5
            vib = vib_base + np.random.randn() * 0.05
            # failure probability increases with high temperature and vibration
            prob_fail = max(0, min(1, 0.01 * (temp - 65) + 0.5 * (vib - 0.5)))
            failure = np.random.rand() < prob_fail
            records.append({
                "timestamp": ts,
                "machine": m,
                "temperature": round(temp, 2),
                "vibration": round(vib, 3),
                "failure": int(failure)
            })
    df = pd.DataFrame(records)
    return df


def main():
    df = generate_data()
    csv_path = "synthetic_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"Generated data saved to {csv_path}")


if __name__ == "__main__":
    main()
