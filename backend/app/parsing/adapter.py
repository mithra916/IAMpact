'''from datetime import datetime

def parse_time(value):
    if isinstance(value, datetime):
        return value

    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except:
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except:
            raise ValueError(f"Unsupported date format: {value}")


def adapt_event(row):
    return {
        "event_time": parse_time(row["eventtime"]),
        "event_name": row["eventname"],
        "user_identity": row["useridentityusername"],
        "source_ip": row["sourceipaddress"],
        "aws_region": row["awsregion"],
        "event_source": row["eventsource"],

        "is_failure": row["is_failure"],
        "is_login": row["is_login"],
        "is_iam": row["is_iam"],
        "is_ec2": row["is_ec2"],
        "is_s3": row["is_s3"]
    }'''


from datetime import datetime
import pandas as pd


def parse_time(value):
    if isinstance(value, datetime):
        return value

    try:
        return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
    except:
        try:
            return datetime.strptime(str(value), "%Y-%m-%d")
        except:
            return datetime.now()


def clean_value(value, default="Unknown"):
    if pd.isna(value):
        return default

    value = str(value).strip()

    if value.lower() in ["nan", "none", "", "null"]:
        return default

    return value


def adapt_event(row):
    user = clean_value(row["useridentityusername"])

    return {
        "event_time": parse_time(row["eventtime"]),
        "event_name": clean_value(row["eventname"]).lower(),

        "user": user,
        "user_identity": user,   # ✅ compatibility fix

        "source_ip": clean_value(row["sourceipaddress"]),
        "aws_region": clean_value(row["awsregion"]),
        "event_source": clean_value(row["eventsource"]),

        "is_failure": row.get("is_failure", 0),
        "is_login": row.get("is_login", 0),
        "is_iam": row.get("is_iam", 0),
        "is_ec2": row.get("is_ec2", 0),
        "is_s3": row.get("is_s3", 0)
    }