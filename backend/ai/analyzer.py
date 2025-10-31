import pandas as pd

def analyze_logs(df: pd.DataFrame):
    """Basic analysis for anomalies and alert patterns."""
    insights = []
    
    if df.empty:
        return [{"message": "No log data available"}]
    
    # Example 1: users with most high-priority alerts
    top_users = (
        df[df["prelim_priority"].str.upper() == "HIGH"]
        .groupby("user")["alert_score"]
        .count()
        .sort_values(ascending=False)
        .head(5)
    )
    for user, count in top_users.items():
        insights.append({
            "user": user,
            "finding": f"{count} high-priority alerts detected for {user}"
        })

    # Example 2: top risky IPs
    top_ips = (
        df.groupby("src_ip")["alert_score"]
        .mean()
        .sort_values(ascending=False)
        .head(5)
    )
    for ip, score in top_ips.items():
        insights.append({
            "ip": ip,
            "finding": f"IP {ip} shows avg alert score {score:.2f}"
        })

    return insights
