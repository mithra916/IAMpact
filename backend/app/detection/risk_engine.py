def calculate_risk(event):

    risk_score = 0
    reasons = []

    critical_actions = [
        "CreateAccessKey",
        "DeleteAccessKey",
        "AttachUserPolicy",
        "AttachRolePolicy",
        "PutUserPolicy",
        "CreateUser",
        "DeleteUser",
        "DeleteTrail",
        "StopLogging"
    ]

    high_actions = [
        "ConsoleLogin",
        "AssumeRole",
        "CreateLoginProfile"
    ]

    action = event.get("action", "")
    ip = event.get("src_ip", "")
    result = event.get("result", "")

    if action in critical_actions:
        risk_score += 50
        reasons.append(
            f"Sensitive IAM action detected: {action}"
        )

    if action in high_actions:
        risk_score += 25
        reasons.append(
            f"High-risk IAM activity detected: {action}"
        )

    if result == "FAILED":
        risk_score += 20
        reasons.append(
            "Failed authentication detected"
        )

    if (
        ip != "unknown"
        and not ip.startswith(("10.", "172.", "192.168."))
    ):
        risk_score += 15
        reasons.append(
            f"External source IP detected: {ip}"
        )

    if action in ["DeleteTrail", "StopLogging"]:
        risk_score += 30
        reasons.append(
            "CloudTrail tampering detected"
        )

    risk_score = min(risk_score, 100)

    if risk_score >= 80:
        priority = "CRITICAL"
    elif risk_score >= 60:
        priority = "HIGH"
    elif risk_score >= 35:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    event["risk_score"] = risk_score
    event["priority"] = priority
    event["reasons"] = reasons

    return event