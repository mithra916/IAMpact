from flask import Blueprint, jsonify
import pandas as pd
from utils.db_config import get_connection

stats_bp = Blueprint("stats", __name__)

@stats_bp.route("/api/stats/", methods=["GET"])
def get_stats():
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB not connected"}), 500

    # ✅ Join enriched_logs with users to get usernames
    query = """
        SELECT el.*, u.username
        FROM enriched_logs el
        LEFT JOIN users u ON el.user_id = u.user_id;
    """
    
    try:
        df = pd.read_sql(query, conn)
        conn.close()
    except Exception as e:
        return jsonify({"error": f"Query failed: {str(e)}"}), 500

    if df.empty:
        return jsonify({"error": "No data found"}), 404

    # Normalize column names
    df.columns = [c.lower() for c in df.columns]

    total_alerts = len(df)
    critical_alerts = len(df[df["prelim_priority"].str.upper() == "HIGH"]) if "prelim_priority" in df.columns else 0
    unique_users = df["username"].nunique() if "username" in df.columns else df["user_id"].nunique()
    avg_risk = round(df["alert_score"].mean(), 2) if "alert_score" in df.columns else 0

    return jsonify({
        "total_alerts": total_alerts,
        "critical_alerts": critical_alerts,
        "unique_users": unique_users,
        "avg_risk_score": avg_risk
    })
