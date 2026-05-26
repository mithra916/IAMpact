def generate_recommendations(insights):
    """Turns findings into natural recommendations."""
    recs = []
    for item in insights:
        if "user" in item:
            recs.append({
                "type": "user",
                "target": item["user"],
                "recommendation": f"Review login activity for {item['user']}"
            })
        elif "ip" in item:
            recs.append({
                "type": "ip",
                "target": item["ip"],
                "recommendation": f"Investigate IP {item['ip']} for repeated alerts"
            })
    return recs
