from flask import Blueprint, jsonify
from backend.utils.db_config import get_connection
import pandas as pd

ai_bp = Blueprint("ai_bp", __name__)

def generate_agentic_insights():
    """Simple AI-like heuristic for now. Later replaced with real model."""
    conn = get_connection()
    query = """
    SELECT u.username, e.alert_score, e.prelim_priority, e.ti_country
    FROM enriched_logs e
    LEFT JOIN users u ON e.user_id = u.user_id
    LEFT JOIN ip_details i ON e.ip_id = i.ip_id
    WHERE e.alert_score IS NOT NULL
    ORDER BY e.alert_score DESC
    LIMIT 100;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # 🧩 Map technical usernames to readable display names
    display_names = {
        "backup": "Backup Service Account",
        "Level6": "Production IAM Role",
        "securityMonkey": "Security Monitor Bot",
        "admin": "Admin Account"
    }

    insights = []
    for _, row in df.iterrows():
        raw_user = row["username"] or "Unknown"
        user = display_names.get(raw_user.strip(), raw_user.capitalize())  # fallback to capitalized name

        score = float(row["alert_score"]) if row["alert_score"] is not None else 0
        priority = row["prelim_priority"] or "LOW"
        country = row["ti_country"] or "Unknown"

        # 🧠 “AI-like” reasoning logic for recommendations
        if score > 0.8:
            rec = f"🚨 High risk activity detected for {user}. Recommend MFA review or session lockdown."
        elif priority.upper() == "HIGH":
            rec = f"⚠️ Review {user}'s actions — repeated high-priority alerts from {country}."
        else:
            rec = f"✅ Normal pattern detected for {user}, no immediate action required."

        insights.append({"user": user, "recommendation": rec})

    # In case there's no data
    if not insights:
        insights.append({
            "user": "System",
            "recommendation": "No data available to generate insights."
        })

    return insights


@ai_bp.route("/api/insights/agentic", methods=["GET"])
def get_agentic_insights():
    try:
        data = generate_agentic_insights()
        return jsonify({"status": "success", "insights": data})
    except Exception as e:
        print("❌ Agentic AI Error:", e)
        return jsonify({"status": "error", "message": str(e)})
