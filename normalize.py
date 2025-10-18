import pandas as pd
import os

# Load filtered sample
df = pd.read_csv("../data/filtered_logs.csv")

# Normalize relevant fields
df_normalized = pd.DataFrame()
df_normalized['timestamp'] = pd.to_datetime(df['eventTime'])
df_normalized['user'] = df['userIdentityuserName'].fillna(df['userIdentityprincipalId'])
df_normalized['action'] = df['eventName']
df_normalized['src_ip'] = df['sourceIPAddress']
df_normalized['result'] = df['errorCode'].fillna('NoError')

# Save normalized logs
os.makedirs("../data", exist_ok=True)
df_normalized.to_csv("../data/normalized_logs.csv", index=False)

print("✅ Day 2 complete: normalized logs saved to data/normalized_logs.csv")
