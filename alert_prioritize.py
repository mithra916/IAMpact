import pandas as pd
import os

INPUT_PATH = "../data/scored_logs.csv"
OUTPUT_PATH = "../data/final_alerts.csv"

if not os.path.exists(INPUT_PATH):
    raise FileNotFoundError(f"{INPUT_PATH} missing. Run ml_score.py first.")

print("🔹 Loading scored logs...")
df = pd.read_csv(INPUT_PATH)

# === Ensure necessary columns ===
if "alert_score" not in df.columns:
    df["alert_score"] = 0
if "prelim_priority" not in df.columns:
    df["prelim_priority"] = "MEDIUM"
if "action" not in df.columns:
    df["action"] = "unknown_action"
if "timestamp" not in df.columns:
    df["timestamp"] = pd.Timestamp.now()

# === Risk weighting ===
priority_weights = {"LOW": 0.5, "MEDIUM": 1.0, "HIGH": 1.5, "CRITICAL": 2.0}
df["priority_multiplier"] = df["prelim_priority"].map(priority_weights).fillna(1.0)

# === Calculate final score ===
df["final_risk_score"] = (df["alert_score"] * df["priority_multiplier"] * 100).round(2)

# === Categorize alerts ===
def categorize(score):
    if score >= 140:
        return "CRITICAL"
    elif score >= 80:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"

df["final_priority"] = df["final_risk_score"].apply(categorize)

# === Generate recommendations ===
def recommend(priority, action):
    if priority == "CRITICAL":
        return f"🚨 Immediate action required: investigate '{action}'"
    elif priority == "HIGH":
        return f"⚠️ Review IAM permissions for '{action}'"
    elif priority == "MEDIUM":
        return f"🔍 Monitor event: '{action}'"
    else:
        return f"✅ No immediate action for '{action}'"

df["auto_recommendation"] = df.apply(lambda x: recommend(x["final_priority"], x["action"]), axis=1)

# === Save final enriched output ===
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

print(f"✅ Final alerts generated: {OUTPUT_PATH}")
print("\nFinal Priority Breakdown:\n", df["final_priority"].value_counts())
