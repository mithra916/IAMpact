from flask import Blueprint, jsonify

insights_bp = Blueprint("insights", __name__)

@insights_bp.route("/api/insights/", methods=["GET"])
def get_insights():
    # Example data (replace with your DB or analysis results)
    user_risks = {
        "admin": 0.85,
        "backup": 0.65,
        "level6": 0.25,
        "securityMonkey": 0.15
    }
    display_names={
        "admin":"Adminstrator",
        "backup":"Backup Service Account",
        "level6":"Production IAM Role",
        "securityMonkey":"Security Monitoring Bot"
    }

    insights = []

    for user, risk in user_risks.items():
        if risk > 0.7:
            msg = "🚨 High-risk IAM behavior detected. Recommend MFA review or session lockdown."
        elif risk > 0.4:
            msg = "⚠️ Elevated access pattern observed. Recommend permission audit."
        else:
            msg = "✅ Normal IAM activity observed. No immediate action required."

        insights.append({
            "entity": user.capitalize(),  # Just capitalizes the name
            "risk_score": round(risk, 2),
            "summary": msg
        })

    # Sort by risk_score (high to low)
    insights.sort(key=lambda x: x["risk_score"], reverse=True)

    return jsonify(insights)
