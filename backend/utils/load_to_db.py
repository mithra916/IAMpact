import psycopg2
from psycopg2.extras import execute_batch
import pandas as pd
from backend.utils.db_config import DB_CONFIG
import traceback

def setup_database():
    """Create the database and normalized tables if they don't exist."""
    try:
        # First try connecting to create the database
        conn = psycopg2.connect(
            dbname="iampact",
            user=DB_CONFIG["postgres"],
            password=DB_CONFIG["changeme"],
            host=DB_CONFIG["localhost"],
            port=DB_CONFIG["5432"]
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Create database if it doesn't exist
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG["dbname"],))
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {DB_CONFIG['dbname']}")
        
        cur.close()
        conn.close()

        # Now connect to our database and create normalized tables
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL
            );
        """)

        # Create actions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                action_id SERIAL PRIMARY KEY,
                action_name VARCHAR(200) UNIQUE NOT NULL
            );
        """)

        # Create ip_details table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ip_details (
                ip_id SERIAL PRIMARY KEY,
                src_ip VARCHAR(50) UNIQUE NOT NULL,
                country VARCHAR(10),
                ti_score INT
            );
        """)

        # Create enriched_logs table with foreign keys
        cur.execute("""
            CREATE TABLE IF NOT EXISTS enriched_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                user_id INT REFERENCES users(user_id),
                action_id INT REFERENCES actions(action_id),
                ip_id INT REFERENCES ip_details(ip_id),
                result TEXT,
                result_flag BOOLEAN,
                alert_score FLOAT,
                prelim_priority VARCHAR(50),
                ti_country VARCHAR(10)
            );
        """)
        
        conn.commit()
        print("✅ Database and normalized tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Database setup error: {str(e)}")
        return False
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

def insert_logs(logs_df: pd.DataFrame):
    """
    Inserts processed logs directly into the enriched_logs table.
    Uses the denormalized schema with raw values (not IDs).
    """
    try:
        # Ensure database and tables exist
        if not setup_database():
            raise Exception("Failed to setup database. Check credentials and permissions.")
            
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 1. Insert users and get mapping
        print("Adding users...")
        users = logs_df["user"].dropna().unique()
        for user in users:
            cur.execute(
                "INSERT INTO users (username) VALUES (%s) ON CONFLICT (username) DO NOTHING;",
                (user,)
            )
        
        cur.execute("SELECT user_id, username FROM users;")
        user_map = {username: uid for uid, username in cur.fetchall()}
        
        # 2. Insert actions and get mapping
        print("Adding actions...")
        actions = logs_df["action"].dropna().unique()
        for action in actions:
            cur.execute(
                "INSERT INTO actions (action_name) VALUES (%s) ON CONFLICT (action_name) DO NOTHING;",
                (action,)
            )
            
        cur.execute("SELECT action_id, action_name FROM actions;")
        action_map = {name: aid for aid, name in cur.fetchall()}
        
        # 3. Insert IP details and get mapping
        print("Adding IP details...")
        ips = logs_df[["src_ip"]].drop_duplicates()
        for ip in ips["src_ip"]:
            cur.execute(
                "INSERT INTO ip_details (src_ip) VALUES (%s) ON CONFLICT (src_ip) DO NOTHING;",
                (ip,)
            )
            
        cur.execute("SELECT ip_id, src_ip FROM ip_details;")
        ip_map = {ip: ipid for ipid, ip in cur.fetchall()}
        
        # 4. Prepare enriched logs with mapped IDs
        missing_user = set()
        missing_action = set()
        missing_ip = set()
        records = []
        for _, row in logs_df.iterrows():
            u = row.get("user")
            a = row.get("action")
            ip = row.get("src_ip")
            uid = user_map.get(u)
            aid = action_map.get(a)
            iid = ip_map.get(ip)
            if uid is None:
                missing_user.add(u)
            if aid is None:
                missing_action.add(a)
            if iid is None:
                missing_ip.add(ip)
            if uid is not None and aid is not None and iid is not None:
                records.append(
                    (
                        row["timestamp"],
                        uid,
                        aid,
                        iid,
                        row.get("result"),
                        row.get("result_flag"),
                        row.get("alert_score"),
                        row.get("prelim_priority"),
                        row.get("ti_country")
                    )
                )

        # Log summary so we can see why rows were skipped
        print(f"Total incoming rows: {len(logs_df)}")
        print(f"Rows prepared for insert: {len(records)}")
        if missing_user:
            print(f"⚠️ Missing users (sample 10): {list(missing_user)[:10]}")
        if missing_action:
            print(f"⚠️ Missing actions (sample 10): {list(missing_action)[:10]}")
        if missing_ip:
            print(f"⚠️ Missing IPs (sample 10): {list(missing_ip)[:10]}")

        query = """
            INSERT INTO enriched_logs (
                timestamp, user_id, action_id, ip_id, result,
                result_flag, alert_score, prelim_priority, ti_country
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
        """

        execute_batch(cur, query, records, page_size=1000)
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ {len(records)} logs successfully inserted into enriched_logs.")

    except Exception as e:
        print(f"❌ Database insert error: {str(e)}")
        traceback.print_exc()
        if "relation" in str(e) and "does not exist" in str(e):
            print("💡 Hint: Make sure to run schema.sql or allow the script to create normalized tables first")
