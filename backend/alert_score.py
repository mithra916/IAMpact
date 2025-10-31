"""
alert_score.py – combines enriched IAM logs with ML-based scoring
Generates final_alerts.csv ready for dashboard or database insertion
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

DATA_PATH = "../data/enriched_logs.csv"
OUT_PATH  = "../data/final_alerts.csv"

def load_data(path=DATA_PATH):
    print(f"📘 Loading enriched logs from: {path}")
    df = pd.read_csv(path)
    # fill missing numeric columns
    df["alert_score"] = df["alert_score"].fillna(0)
    df["ti_score"] = df["ti_score"].fillna(0)
    df["ip_score"] = df["ip_score"].fillna(0)
    df["result_flag"] = df["result_flag"].fillna(0)
    return df

def prepare_features(df: pd.DataFrame):
    # numeric fusion features
    features = df[["alert_score", "ti_score", "ip_score", "result_flag"]]
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(features)
    return X_scaled

def assign_priority(prob):
    """prob = model probability for malicious"""
    if prob > 0.85:
        return "CRITICAL"
    elif prob > 0.6:
        return "HIGH"
    elif prob > 0.3:
        return "MEDIUM"
    else:
        return "LOW"

def train_model(df):
    print("⚙️  Training lightweight ML model...")
    X = prepare_features(df)
    # use existing column 'prelim_priority' to generate a simple label
    y = df["prelim_priority"].map({"LOW":0,"MEDIUM":1,"HIGH":2,"CRITICAL":3}).fillna(0)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print(classification_report(y_test, preds))

    # Predict for full dataset
    probs = model.predict_proba(X)
    # use max class prob to derive continuous risk
    max_prob = np.max(probs, axis=1)
    df["final_score"] = (max_prob * 100).round(2)
    df["final_priority"] = df["final_score"].apply(lambda x: assign_priority(x/100))
    return df

def main():
    df = load_data()
    df_final = train_model(df)
    df_final.to_csv(OUT_PATH, index=False)
    print(f"✅ Final alert scoring complete → {OUT_PATH}")
    print(df_final[["timestamp","user","src_ip","final_priority"]].head(10))

if __name__ == "__main__":
    print("🚀 Running Alert Scoring and Fusion Layer...")
    main()
