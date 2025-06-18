import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
import joblib


def train_model(csv_path: str = "synthetic_data.csv", model_path: str = "models/predictive_model.pkl"):
    df = pd.read_csv(csv_path)
    X = df[["machine", "temperature", "vibration"]]
    y = df["failure"]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_val)
    y_proba = clf.predict_proba(X_val)[:, 1]
    acc = accuracy_score(y_val, y_pred)
    auc = roc_auc_score(y_val, y_proba)
    print(f"Validation Accuracy: {acc:.4f}")
    print(f"Validation ROC-AUC: {auc:.4f}")

    joblib.dump(clf, model_path)
    print(f"Model saved to {model_path}")

    return clf


def main():
    train_model()


if __name__ == "__main__":
    main()
