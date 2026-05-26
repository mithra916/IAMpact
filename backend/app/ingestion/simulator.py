import time

def stream_logs(logs, delay=1):
    for log in logs:
        yield log
        time.sleep(delay)