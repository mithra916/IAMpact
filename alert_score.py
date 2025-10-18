# tools/recompute_alert_score.py
import pandas as pd
import numpy as np
import os

p = "data/scored_logs.csv"
if not os.path.exists(p):
    raise SystemExit("data/scored_logs.csv missing")

df = pd.read_csv(p)
# ensure numeric
df['ti_score'] = pd.to_numeric(df.get('ti_score',0), errors='coerce').fillna(0)
df['alert_score'] = pd.to_numeric(df.get('alert_score',0), errors='coerce').fillna(0)

if df['alert_score'].max() == 0:
    print("Recomputing alert_score fallback...")
    # rule score: role-change or error
    df['is_role_change'] = df['action'].astype(str).str.contains('role|attach|assume', case=False).astype(int)
    df['error_flag'] = df['result'].astype(str).str.contains('Error|Exception|Denied', case=False).astype(int)
    base = (df['ti_score'] / (df['ti_score'].max()+1)) * 0.6
    rule = (df['is_role_change'] * 0.5) + (df['error_flag'] * 0.4)
    jitter = np.random.RandomState(42).rand(len(df))*0.05
    combined = base + rule + jitter
    df['alert_score'] = (combined / combined.max()).fillna(0)
    df['prelim_priority'] = df['alert_score'].apply(lambda s: 'HIGH' if s>=0.5 else ('MEDIUM' if s>=0.25 else 'LOW'))
    df.to_csv(p, index=False)
    print("Wrote recomputed scores to", p)
else:
    print("alert_score already non-zero, nothing changed.")
