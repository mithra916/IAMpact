from flask import Flask, jsonify, render_template
from flask_cors import CORS
import psycopg2
import pandas as pd
from pathlib import Path
from backend.routes.logs import logs_bp
from backend.routes.insights_ai import ai_bp
from backend.utils.db_config import get_connection
from backend.routes.alerts import alerts_bp
# ----------------------------
# PATH SETUP
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# ----------------------------
# FLASK CONFIG
# ----------------------------
app = Flask(
    __name__,
    static_folder=str(STATIC_DIR),
    template_folder=str(TEMPLATES_DIR)
)
CORS(app)

# ----------------------------
# DATABASE CONFIG
# ----------------------------
DB_CONFIG = {
    "dbname": "iampact",
    "user": "postgres",
    "password": "changeme",  # 🔒 change to your actual password
    "host": "localhost",
    "port": 5432
}

# Register blueprint for logs API
app.register_blueprint(logs_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(alerts_bp)
# ----------------------------
# DATABASE HELPER
# ----------------------------
def fetch_df(query: str):
    """Run SQL query and return a pandas DataFrame."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("❌ Database error:", e)
        return pd.DataFrame()

# ----------------------------
# FRONTEND ROUTE
# ----------------------------
@app.route("/")
def dashboard():
    """Render main dashboard frontend."""
    return render_template("index.html")

# ----------------------------
# API ROUTES
# ----------------------------

@app.route("/api/alerts/", methods=["GET"])
def get_alerts():
    """Fetch joined log data for display."""
    query = """
        SELECT e.id,
               u.username AS user,
               a.action_name AS action,
               i.src_ip AS src_ip,
               e.result,
               e.alert_score,
               e.prelim_priority,
               e.ti_country,
               e.ti_asn
        FROM enriched_logs e
        LEFT JOIN users u ON e.user_id = u.user_id
        LEFT JOIN actions a ON e.action_id = a.action_id
        LEFT JOIN ip_details i ON e.ip_id = i.ip_id
        ORDER BY e.id DESC
        LIMIT 100;
    """
    df = fetch_df(query)
    return jsonify(df.to_dict(orient="records"))

@app.route("/api/stats/", methods=["GET"])
def get_stats():
    """Return aggregate statistics for dashboard cards."""
    query = """
        SELECT 
            COUNT(*) AS total_alerts,
            SUM(CASE WHEN e.prelim_priority ILIKE 'HIGH' THEN 1 ELSE 0 END) AS critical_alerts,
            COUNT(DISTINCT e.user_id) AS unique_users,
            ROUND(AVG(e.alert_score)::numeric, 6) AS avg_risk_score
        FROM enriched_logs e;
    """
    df = fetch_df(query)
    if df.empty:
        return jsonify({"error": "No data found"}), 404

    stats = df.iloc[0].to_dict()
    
    # 🔥 Fix scaling for readability
    avg_score = float(stats.get("avg_risk_score", 0.0)) * 10000


    return jsonify({
        "total_alerts": int(stats.get("total_alerts", 0)),
        "critical_alerts": int(stats.get("critical_alerts", 0)),
        "unique_users": int(stats.get("unique_users", 0)),
        "avg_risk_score": round(avg_score, 2)
    })


@app.route("/api/insights/", methods=["GET"])
def get_insights():
    """Static insights placeholder — to be replaced by Agentic AI."""
    return jsonify({
        "insights": [
            {"user": "backup", "recommendation": "Investigate repeated login failures."},
            {"user": "admin", "recommendation": "Review high-risk IP sources."}
        ]
    })

@app.route("/api/health/", methods=["GET"])
def health_check():
    """Check DB connection and record count."""
    df = fetch_df("SELECT COUNT(*) as count FROM enriched_logs;")
    if df.empty:
        return jsonify({"status": "error", "message": "No data found"}), 404
    return jsonify({"status": "ok", "records_loaded": int(df.iloc[0, 0])})

# ----------------------------
# MAIN ENTRY POINT
# ----------------------------
if __name__ == "__main__":
    print(f"📁 Templates: {TEMPLATES_DIR}")
    print(f"📁 Static: {STATIC_DIR}")
    print(f"🧠 Connecting to database: {DB_CONFIG['dbname']} as {DB_CONFIG['user']}")
    app.run(debug=True, port=5000)
