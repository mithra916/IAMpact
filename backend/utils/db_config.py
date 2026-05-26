import os
import psycopg2

# ----------------------------
# Database Configuration
# ----------------------------
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "iampact"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", "changeme"),  # change to your actual password
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

# ----------------------------
# Connection Helper
# ----------------------------
def get_connection():
    """Establish and return a PostgreSQL connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print("❌ Database connection failed:", e)
        return None
