from flask import Blueprint, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from backend.utils.db_config import get_connection

logs_bp = Blueprint("logs", __name__)

@logs_bp.route("/api/logs", methods=["GET"])
def get_logs():
    conn = get_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB not connected"})
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM enriched_logs ORDER BY timestamp DESC LIMIT 50;")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        print("❌ Error fetching logs:", e)
        return jsonify({"status": "error", "message": str(e)})
