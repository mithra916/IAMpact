import pandas as pd

def preprocess_logs(csv_path):
    """Clean and normalize logs before database insertion."""
    df = pd.read_csv(csv_path)

    # Standardize column names
    df = df.rename(columns={
        "eventTime": "timestamp",
        "userIdentityuserName": "user",
        "eventName": "action",
        "sourceIPAddress": "src_ip"
    })

    # Ensure all expected columns exist
    for col in ["result", "result_flag", "alert_score", "prelim_priority", "ti_country", "ti_asn"]:
        if col not in df.columns:
            df[col] = None

    # Fix timestamp format
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    print(f"✅ Preprocessing complete. Shape: {df.shape}")
    return df[["timestamp", "user", "action", "src_ip", "result", "result_flag",
               "alert_score", "prelim_priority", "ti_country", "ti_asn"]]
