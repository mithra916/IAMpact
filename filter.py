##1# Day 1: Basic Filtering and Sampling of IAM Logs

import pandas as pd
import os

# Ensure data folder exists
os.makedirs("../data", exist_ok=True)

# Load raw IAM logs (from Kaggle)
df = pd.read_csv("../data/logs.csv")

# Basic filtering: remove internal/service users
df_filtered = df[df['userIdentitytype'] != 'AWSService']

# Sample to reduce size for Streamlit
df_sample = df_filtered.sample(min(100000, len(df_filtered)), random_state=42)

# Save filtered sample for next days
df_sample.to_csv("../data/filtered_logs.csv", index=False)

print("✅ Day 1 complete: filtered & sampled logs saved to data/filtered_logs.csv")
