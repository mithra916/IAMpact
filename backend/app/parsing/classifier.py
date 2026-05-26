def classify_event(event):
    if event.get("is_login"):
        return "authentication"
    elif event.get("is_iam"):
        return "authorization"
    elif event.get("is_s3"):
        return "data_access"
    else:
        return "infrastructure"