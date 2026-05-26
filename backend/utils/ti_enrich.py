import os
import requests
import pandas as pd
from pathlib import Path
from time import sleep

# ---------------------- CONFIG ----------------------
API_KEY = os.getenv("ABUSEIPDB_KEY")
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "scored_logs.csv"
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "enriched_logs.csv"
RATE_LIMIT_DELAY = 1  # seconds between API calls

# ---------------------- HELPERS ----------------------
def normalize_ip(ip):
    """Ensure IP has 4 octets (e.g., 5.205 → 5.205.0.0)."""
    ip = str(ip).strip()
    if not ip or ip.lower() in ["-", "unknown", "none", "nan"]:
        return None
    parts = ip.split(".")
    # Remove invalid parts
    parts = [p for p in parts if p.isdigit()]
    if len(parts) < 4:
        parts += ["0"] * (4 - len(parts))
    try:
        parts = [str(min(int(p), 255)) for p in parts[:4]]
        return ".".join(parts)
    except ValueError:
        return None


def abuse_check(ip):
    """Query AbuseIPDB API for reputation info."""
    if not API_KEY or not ip:
        return None
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": API_KEY, "Accept": "application/json"}
    params = {"ipAddress": ip, "maxAgeInDays": 90}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=8)
        r.raise_for_status()
        data = r.json().get("data", {})
        return {
            "abuseConfidenceScore": data.get("abuseConfidenceScore", 0),
            "country": data.get("countryCode", "NA"),
            "asn": data.get("asn", "NA")
        }
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error checking IP {ip}: {e}")
        return None


def map_score(conf):
    """Convert confidence score (0–100) → 1–10 scale."""
    if conf < 10: return 1
    elif conf < 30: return 3
    elif conf < 60: return 6
    elif conf < 80: return 8
    else: return 10


# ---------------------- MAIN ----------------------
def main():
    print("🚀 Running Threat Intelligence enrichment...")
    if not DATA_PATH.exists():
        print(f"❌ Data file not found: {DATA_PATH}")
        return

    print(f"📘 Loading logs from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)

    # Normalize IPs
    df["src_ip"] = df["src_ip"].fillna("unknown").apply(normalize_ip)
    valid_ips = [ip for ip in df["src_ip"].dropna().unique() if ip.count(".") == 3]
    print(f"🔍 Found {len(valid_ips)} valid IPs to check...")

    if not valid_ips:
        print(f"⚠️ No valid IPs found! Skipping enrichment.")
        df.to_csv(OUT_PATH, index=False)
        print(f"✅ Saved clean copy → {OUT_PATH}")
        return

    results = {}
    for i, ip in enumerate(valid_ips, 1):
        print(f"🔹 [{i}/{len(valid_ips)}] Checking {ip}...")
        res = abuse_check(ip)
        if res:
            results[ip] = res
        sleep(RATE_LIMIT_DELAY)

    # Map results back to DataFrame
    df["ti_score"] = df["src_ip"].apply(lambda x: map_score(results.get(x, {}).get("abuseConfidenceScore", 0)))
    df["ti_country"] = df["src_ip"].apply(lambda x: results.get(x, {}).get("country", "NA"))
    df["ti_asn"] = df["src_ip"].apply(lambda x: results.get(x, {}).get("asn", "NA"))

    # Save enriched data
    df.to_csv(OUT_PATH, index=False)
    print(f"✅ Threat-Intel enrichment complete → {OUT_PATH}")


if __name__ == "__main__":
    main()
