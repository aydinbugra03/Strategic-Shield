import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score


DATA_CSV = 'synthetic_data.csv'
MODEL_PATH = 'failure_model.joblib'


def load_data(path=DATA_CSV):
    df = pd.read_csv(path, parse_dates=['timestamp'])
    X = df[['temperature', 'vibration']]
    y = df['failure']
    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_model(X_train, y_train):
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    return clf


def evaluate_model(clf, X_test, y_test):
    preds = clf.predict(X_test)
    proba = clf.predict_proba(X_test)[:, 1]
    acc = accuracy_score(y_test, preds)
    auc = roc_auc_score(y_test, proba)
    print(f"Accuracy: {acc:.3f}\nROC-AUC: {auc:.3f}")


def main():
    X_train, X_test, y_train, y_test = load_data()
    clf = train_model(X_train, y_train)
    evaluate_model(clf, X_test, y_test)
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == '__main__':
    main()
