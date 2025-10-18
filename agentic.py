import pandas as pd
import os

df = pd.read_csv("../data/scored_logs.csv")

# Mini Agentic AI: suggest action
def suggest_action(row):
    if row['prelim_priority'] == 'HIGH' and row['ti_score'] > 5:
        return 'Investigate Immediately'
    elif row['prelim_priority'] == 'HIGH':
        return 'Check User Activity'
    else:
        return 'Monitor'

df['final_priority'] = df['prelim_priority']
df['suggested_action'] = df.apply(suggest_action, axis=1)

df.to_csv("../data/final_alerts.csv", index=False)
print("✅ Day 5 complete: final alerts saved to data/final_alerts.csv")
