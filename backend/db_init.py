import psycopg2
import pandas as pd
from psycopg2.extras import execute_values
from pathlib import Path

# ----------------------------
# CONFIGURATION
# ----------------------------
DB_CONFIG = {
    "dbname": "iampact",
    "user": "postgres",
    "password": "changeme",   # ⚠️ change this to your actual password
    "host": "localhost",
    "port": 5432
}

# Path to your dataset
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "enriched_logs.csv"

# ----------------------------
# CONNECT TO DATABASE
# ----------------------------
def get_conn():
    return psycopg2.connect(**DB_CONFIG)

# ----------------------------
# MAIN LOADER
# ----------------------------
def load_data():
    print("🚀 Loading dataset:", DATA_PATH)
    df = pd.read_csv(DATA_PATH)
    print(f"✅ Loaded {len(df)} rows")

    conn = get_conn()
    cur = conn.cursor()

    # 1️⃣ Insert unique users
    print("🧑 Adding users...")
    users = df["user"].dropna().unique().tolist()
    execute_values(
        cur,
        "INSERT INTO users (username) VALUES %s ON CONFLICT DO NOTHING;",
        [(u,) for u in users]
    )
    conn.commit()

    # 2️⃣ Insert unique actions
    print("⚙️ Adding actions...")
    actions = df["action"].dropna().unique().tolist()
    execute_values(
        cur,
        "INSERT INTO actions (action_name) VALUES %s ON CONFLICT DO NOTHING;",
        [(a,) for a in actions]
    )
    conn.commit()

    # 3️⃣ Insert unique IP details (deduplicate fully)
    print("🌍 Adding IP details...")
    ips = (
        df[["src_ip", "country", "ti_score"]]
        .dropna(subset=["src_ip"])
        .drop_duplicates(subset=["src_ip"])
    )

    # Insert IP details safely (no batch conflict)
    for _, row in ips.iterrows():
        cur.execute(
            """
            INSERT INTO ip_details (src_ip, country, ti_score)
            VALUES (%s, %s, %s)
            ON CONFLICT (src_ip)
            DO UPDATE SET
                country = EXCLUDED.country,
                ti_score = EXCLUDED.ti_score;
            """,
            (row["src_ip"], row["country"], int(row["ti_score"]))
        )
    conn.commit()

    # 4️⃣ Insert enriched logs (fact table)
    print("🧩 Adding enriched logs...")
    for _, row in df.iterrows():
        cur.execute(
            """
            INSERT INTO enriched_logs (
                timestamp, user_id, action_id, ip_id, result, result_flag,
                alert_score, prelim_priority, ti_country
            )
            SELECT
                %s,
                u.user_id,
                a.action_id,
                i.ip_id,
                %s,
                %s,
                %s,
                %s,
                %s
            FROM users u, actions a, ip_details i
            WHERE u.username = %s
            AND a.action_name = %s
            AND i.src_ip = %s;
            """,
            (
                row["timestamp"],
                row["result"],
                row.get("result_flag", 0),
                row.get("alert_score", 0),
                row.get("prelim_priority", "low"),
                row["country"],
                row["user"],
                row["action"],
                row["src_ip"]
            )
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ All data successfully inserted into normalized tables!")

# ----------------------------
# ENTRY POINT
# ----------------------------
if __name__ == "__main__":
    load_data()
