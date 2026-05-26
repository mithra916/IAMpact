import pandas as pd, numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder
from pathlib import Path
import joblib

DATA = Path(__file__).resolve().parents[1] / "data" / "scored_logs.csv"
MODEL = Path(__file__).resolve().parents[1] / "models"
MODEL.mkdir(exist_ok=True)
IF_FILE = MODEL / "iforest.pkl"
ENC_FILE = MODEL / "encoder.pkl"

def load_df():
    df = pd.read_csv(DATA)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["final_risk_score"] = pd.to_numeric(df["final_risk_score"], errors="coerce").fillna(0)
    df["ti_score"] = pd.to_numeric(df.get("ti_score", 0), errors="coerce").fillna(0)
    df["hour"] = df["timestamp"].dt.hour.fillna(0).astype(int)
    df["weekday"] = df["timestamp"].dt.weekday.fillna(0).astype(int)
    df["is_console"] = df["action"].str.contains("ConsoleLogin", case=False, na=False).astype(int)
    return df

def encode(df):
    enc = OneHotEncoder(handle_unknown="ignore", sparse=False)
    df["action_top"] = df["action"].fillna("OTHER")
    actions = df[["action_top"]]
    if ENC_FILE.exists():
        enc = joblib.load(ENC_FILE)
        mat = enc.transform(actions)
    else:
        mat = enc.fit_transform(actions)
        joblib.dump(enc, ENC_FILE)
    cols = enc.get_feature_names_out(["action"])
    return np.hstack([df[["final_risk_score","ti_score","hour","weekday","is_console"]].values, mat]), cols

def train_or_load(X):
    if IF_FILE.exists():
        clf = joblib.load(IF_FILE)
    else:
        clf = IsolationForest(contamination=0.02, random_state=42)
        clf.fit(X)
        joblib.dump(clf, IF_FILE)
    return clf

def main():
    df = load_df()
    X, cols = encode(df)
    clf = train_or_load(X)
    scores = -clf.decision_function(X)
    norm = (scores - scores.min()) / (scores.max() - scores.min() + 1e-9)
    df["ml_score"] = norm
    df["ml_flag"] = (df["ml_score"] > 0.7).astype(int)
    df["final_risk_score"] += df["ml_score"] * 5
    df.to_csv(DATA, index=False)
    print(f"✅ ML anomaly scores added → {DATA}")

if __name__ == "__main__":
    main()
