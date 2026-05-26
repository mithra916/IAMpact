import re
import ipaddress


def extract_ip(value):
    if not value:
        return "unknown"

    value = str(value)

    match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", value)

    if not match:
        return "unknown"

    ip = match.group(0)

    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        return "unknown"


def detect_log_type(event):
    if not isinstance(event, dict):
        return "unknown"

    if "eventSource" in event and "eventName" in event:
        if event.get("eventSource") == "iam.amazonaws.com":
            return "aws_iam"
        return "aws_cloudtrail"

    if "userIdentity" in event and "eventName" in event:
        return "aws_cloudtrail"

    return "unknown"


def parse_cloudtrail_event(event):
    user_identity = event.get("userIdentity", {})

    return {
        "timestamp": event.get("eventTime", "unknown"),
        "user": user_identity.get(
            "userName",
            user_identity.get("arn", "unknown")
        ),
        "action": event.get("eventName", "unknown"),
        "src_ip": extract_ip(event.get("sourceIPAddress", "unknown")),
        "region": event.get("awsRegion", "unknown"),
        "result": "FAILED" if event.get("errorCode") else "SUCCESS",
        "error_code": event.get("errorCode"),
        "log_type": detect_log_type(event),
        "raw_event": event
    }