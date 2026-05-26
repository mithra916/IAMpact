import re

def validate_log_entry(entry: dict) -> tuple[bool, str]:
    """Validate a log record before inserting into DB."""
    try:
        # Required fields
        required = ["user_id", "action_id", "ip_id", "result", "alert_score", "prelim_priority"]
        for key in required:
            if key not in entry or entry[key] is None:
                return False, f"Missing required field: {key}"

        # Score between 0–10
        if not (0 <= float(entry["alert_score"]) <= 10):
            return False, "Alert score must be between 0 and 10"

        # Priority check
        if entry["prelim_priority"].upper() not in ["LOW", "MEDIUM", "HIGH"]:
            return False, "Invalid prelim_priority value"

        # IP validation (simple regex)
        ip = entry.get("ip", "")
        if ip and not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip):
            return False, f"Invalid IP format: {ip}"

        return True, "Valid"
    except Exception as e:
        return False, str(e)
