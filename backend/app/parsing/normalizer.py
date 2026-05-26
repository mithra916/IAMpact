from app.parsing.parser import detect_log_type, extract_ip


def normalize_log(raw_log: str):

    log_type = detect_log_type(raw_log)

    normalized = {
        "event_type": "UNKNOWN",
        "src_ip": extract_ip(raw_log),
        "raw": raw_log
    }

    if log_type == "LINUX_AUTH":

        normalized["event_type"] = "FAILED_LOGIN"

        if "root" in raw_log:
            normalized["user"] = "root"

    return normalized