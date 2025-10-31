import pandas as pd
from db_config import get_db_connection

def migrate_enriched_logs(csv_path):
    conn = get_db_connection()
    if not conn:
        print("❌ No DB connection.")
        return

    df = pd.read_csv(csv_path)
    print(f"📊 Loaded {len(df)} rows from {csv_path}")

    cursor = conn.cursor()

    insert_query = """
        INSERT INTO logs_enriched (src_ip, ti_score, ti_country, ti_asn, alert_score, prelim_priority)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    for _, row in df.iterrows():
        cursor.execute(insert_query, (
            row.get("src_ip"),
            row.get("ti_score"),
            row.get("ti_country"),
            row.get("ti_asn"),
            row.get("alert_score"),
            row.get("prelim_priority")
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Migration complete! Data stored in MySQL successfully.")

if __name__ == "__main__":
    migrate_enriched_logs("../data/enriched_logs.csv")
