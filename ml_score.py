import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
import os

# === CONFIG ===
DATA_PATH = "../data/enriched_logs.csv"
OUTPUT_PATH = "../data/scored_logs.csv"
MAX_ROWS_FOR_TRAIN = 200000
IFOREST_CONTAMINATION = 0.05

# === 1. Load enriched logs ===
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"{DATA_PATH} not found. Please run Day 3 first.")

print("🔹 Loading enriched logs...")
df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=["ti_score", "src_ip", "result"], how="any")

# === 2. Feature Engineering ===
def encode_ip(ip):
    try:
        parts = [int(p) for p in str(ip).split(".") if p.isdigit()]
        return sum(parts) / len(parts)
    except Exception:
        return 0

df["ip_score"] = df["src_ip"].apply(encode_ip)
df["result_flag"] = df["result"].apply(lambda x: 1 if "Error" in str(x) or "Exception" in str(x) else 0)

features = ["ti_score", "ip_score", "result_flag"]
X = df[features].copy()

# === 3. Train IsolationForest ===
print("🔹 Training IsolationForest on IAM log features...")

# Sample subset if dataset is too large
if len(X) > MAX_ROWS_FOR_TRAIN:
    X_train = X.sample(MAX_ROWS_FOR_TRAIN, random_state=42)
else:
    X_train = X

clf = IsolationForest(
    n_estimators=100,
    contamination=IFOREST_CONTAMINATION,
    random_state=42
)
clf.fit(X_train)

# === 4. Score logs ===
def score_iforest(clf, X):
    raw = clf.decision_function(X)
    inv = -raw
    minv, maxv = inv.min(), inv.max()
    if abs(maxv - minv) < 1e-9:
        print("⚠️ IsolationForest produced constant scores — using random jitter fallback.")
        norm = np.random.random(len(inv)) * 0.1
    else:
        norm = (inv - minv) / (maxv - minv)
    return norm

df["alert_score"] = score_iforest(clf, X)

# === 5. Rule-based priority ===
def rule_based_priority(row):
    if row["ti_score"] > 7 or row["result_flag"] == 1 or row["alert_score"] > 0.7:
        return "HIGH"
    elif row["alert_score"] > 0.4:
        return "MEDIUM"
    else:
        return "LOW"

df["prelim_priority"] = df.apply(rule_based_priority, axis=1)

# === 6. Save scored logs ===
os.makedirs("data", exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

print(f"✅ ML Scoring completed. Saved to: {OUTPUT_PATH}")
print(df["prelim_priority"].value_counts())
print(df["alert_score"].describe())
