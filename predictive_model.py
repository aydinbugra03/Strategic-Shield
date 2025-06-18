import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score


def train_model(csv_path: str = "data/synthetic_data.csv", model_path: str = "models/predictive_model.joblib") -> str:
    """Train a failure prediction model from the synthetic data."""
    df = pd.read_csv(csv_path)
    X = df[["temperature", "vibration", "machine_id"]]
    y = df["failure"]

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_val)
    y_prob = clf.predict_proba(X_val)[:, 1]
    acc = accuracy_score(y_val, y_pred)
    auc = roc_auc_score(y_val, y_prob)

    print(f"Validation Accuracy: {acc:.3f}")
    print(f"Validation ROC-AUC: {auc:.3f}")

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(clf, model_path)
    print(f"Model saved to {model_path}")
    return model_path


if __name__ == "__main__":
    train_model()
