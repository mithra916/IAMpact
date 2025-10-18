'''import pandas as pd
import random
import os

df = pd.read_csv("../data/normalized_logs.csv")

# Mock Threat Intelligence: score 0–10
df['ti_score'] = df['src_ip'].apply(lambda x: random.randint(0, 10))

# Mock GeoIP: randomly assign countries
countries = ['US', 'IN', 'GB', 'DE', 'CN', 'Unknown']
df['country'] = df['src_ip'].apply(lambda x: random.choice(countries))

# Save enriched logs
df.to_csv("../data/enriched_logs.csv", index=False)

print("✅ Day 3 complete: enriched logs saved to data/enriched_logs.csv")
'''


# ===============================
# ti_enrich.py — Real Threat Intelligence Enrichment (AbuseIPDB)
# ===============================

import pandas as pd
import requests
import time
import os

DATA_PATH = "../data/enriched_logs.csv"
OUTPUT_PATH = "../data/enriched_logs.csv"
API_KEY = "2930aab2aed88333e2376b6ec0346e75e2cf43404978138882d4e378284a2bb7736fbf3521955c8e"  # 🔑 Replace this with your key
API_URL = "https://api.abuseipdb.com/api/v2/check"

def fetch_ti_for_ip(ip):
    """Query AbuseIPDB for a single IP address."""
    try:
        headers = {
            "Accept": "application/json",
            "Key": API_KEY
        }
        params = {
            "ipAddress": ip,
            "maxAgeInDays": 30
        }
        response = requests.get(API_URL, headers=headers, params=params, timeout=8)
        if response.status_code == 200:
            data = response.json()["data"]
            ti_score = data.get("abuseConfidenceScore", 0)
            country = data.get("countryCode", "Unknown")
            return ti_score, country
        else:
            return 0, "Unknown"
    except Exception as e:
        print(f"⚠️ TI lookup failed for {ip}: {e}")
        return 0, "Unknown"

def enrich_with_ti(df):
    """Enrich dataframe with Threat Intelligence fields."""
    ti_scores = []
    countries = []

    unique_ips = df["src_ip"].dropna().unique().tolist()
    cache = {}

    for i, ip in enumerate(unique_ips, start=1):
        if ip in cache:
            ti_scores.append(cache[ip][0])
            countries.append(cache[ip][1])
            continue

        score, country = fetch_ti_for_ip(ip)
        cache[ip] = (score, country)

        print(f"🔹 [{i}/{len(unique_ips)}] {ip} → {score} ({country})")

        # polite rate limit to avoid AbuseIPDB throttling
        time.sleep(1.2)

    # Map back to dataframe
    df["ti_score"] = df["src_ip"].map(lambda ip: cache.get(ip, (0, "Unknown"))[0])
    df["country"] = df["src_ip"].map(lambda ip: cache.get(ip, (0, "Unknown"))[1])

    # Normalize + flag
    df["ip_score"] = df["ti_score"] / 100.0
    df["result_flag"] = df["ti_score"].apply(lambda x: "Suspicious" if x > 70 else "Benign")

    return df

# ===============================
# Main Execution
# ===============================
if __name__ == "__main__":
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"{DATA_PATH} not found. Please run Day 2 first.")

    print("🔍 Loading enriched logs for TI lookup...")
    df = pd.read_csv(DATA_PATH)

    if "src_ip" not in df.columns:
        raise KeyError("src_ip column not found in logs!")

    print(f"🕵️ Found {df['src_ip'].nunique()} unique IPs to enrich.")
    df = enrich_with_ti(df)

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Threat Intelligence enrichment complete! Saved to {OUTPUT_PATH}")
