from flask import Blueprint, jsonify
from backend.utils.db_config import get_connection
import pandas as pd

alerts_bp = Blueprint("alerts", __name__)

@alerts_bp.route("/api/alerts/", methods=["GET"])
def get_alerts():
    conn = get_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500

    try:
        query = """
        SELECT e.id,
               e.timestamp,
               u.username,
               a.action_name AS action,
               e.prelim_priority,
               e.alert_score,
               i.src_ip
        FROM enriched_logs e
        LEFT JOIN users u ON e.user_id = u.user_id
        LEFT JOIN actions a ON e.action_id = a.action_id
        LEFT JOIN ip_details i ON e.ip_id = i.ip_id
        ORDER BY e.timestamp DESC
        LIMIT 100;
        """

        df = pd.read_sql(query, conn)
        conn.close()

        # --- Friendly display names ---
        display_names = {
            "backup": "Backup Service Account",
            "level6": "Production IAM Role",
            "securitymokey": "Security Monitor Bot",
            "admin": "Admin Account",
            "unknown": "Unidentified User"
        }

        alerts = []
        for _, row in df.iterrows():
            raw_user = str(row["username"]).strip() if row["username"] else "Unknown"
            user = display_names.get(raw_user.lower(), raw_user.capitalize())

            alerts.append({
                "id": int(row["id"]),
                "timestamp": str(row["timestamp"]) if row["timestamp"] else "—",
                "user": user,
                "action": row["action"] or "—",
                "prelim_priority": row["prelim_priority"] or "LOW",
                "alert_score": float(row["alert_score"]) if row["alert_score"] is not None else 0,
                "src_ip": row["src_ip"] or "—"
            })

        return jsonify(alerts)

    except Exception as e:
        print("❌ DB error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500
