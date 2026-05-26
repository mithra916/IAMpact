def generate_explanation(alert):

    priority = alert.get("priority")
    action = alert.get("action")
    user = alert.get("user")
    ip = alert.get("src_ip")

    recommendations = []

    if priority == "CRITICAL":

        recommendations = [
            "Review IAM activity immediately",
            "Revoke suspicious credentials",
            "Force MFA reset",
            "Block malicious IP"
        ]

    elif priority == "HIGH":

        recommendations = [
            "Investigate user session",
            "Verify if activity is authorized",
            "Monitor additional IAM activity"
        ]

    else:

        recommendations = [
            "Continue monitoring"
        ]

    return {
        "summary": (
            f"{priority} alert detected for "
            f"user {user}. "
            f"Action: {action}. "
            f"Source IP: {ip}."
        ),
        "recommendations": recommendations
    }