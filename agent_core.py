"""
agent_core.py — Agentic AI core for IAMpact

Features:
- Watches data/scored_logs.csv (or data/final_alerts.csv) for changes.
- For new/high-priority alerts, generates an explanation + suggested action.
- Uses OpenAI if OPENAI_API_KEY is set; otherwise uses a fallback rule-based explanation.
- Writes/updates data/final_alerts.csv with agent columns:
    - reasoning_text (str)
    - agent_action (str)
    - agent_confidence (float 0..1)
    - agent_timestamp (iso)
Usage:
    pip install watchdog openai pandas python-dotenv
    # set OPENAI_API_KEY in environment or .env if you want LLM explanations
    python src/agent_core.py
Notes:
- This agent only suggests actions. It does NOT call cloud APIs to remediate.
- Tune thresholds and prompts for your environment.
"""

import os
import time
import threading
from datetime import datetime
import pandas as pd
import numpy as np

# Optional libs
try:
    import openai
except Exception:
    openai = None

# Watchdog for file system events
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except Exception:
    Observer = None
    FileSystemEventHandler = object

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SCORED_PATH = os.path.normpath(os.path.join(DATA_DIR, "scored_logs.csv"))
FINAL_PATH = os.path.normpath(os.path.join(DATA_DIR, "final_alerts.csv"))
POLL_INTERVAL = 6  # seconds for periodic re-check if watchdog not available
AGENT_MIN_ALERT_SCORE = 0.5  # only explain alerts with alert_score >= this
AGENT_TTL_SECONDS = 60 * 60 * 24  # one day window to avoid reprocessing old alerts
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Utility: safe read (if file is large, sample)
def safe_read_csv(path, sample_limit=200000):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        if len(df) > sample_limit:
            return df.sample(sample_limit, random_state=42).reset_index(drop=True)
        return df
    except Exception as e:
        print("Error reading CSV:", e)
        return pd.DataFrame()

# Compose LLM prompt (keeps it short)
LLM_PROMPT_TEMPLATE = """You are an experienced cloud security analyst. Given this IAM event, explain in 2-4 bullet points WHY it looks suspicious and suggest a single concise recommended next step for an analyst (no automatic remediation).
Return JSON with keys: reasoning (string), suggestion (string), confidence (0..1 numeric).

Event fields:
{event}

Be concise and factual.
"""

# Fallback rule-based reasoning (deterministic)
def rule_based_reasoning(row):
    reasons = []
    score = float(row.get("alert_score", 0) or 0)
    ti = float(row.get("ti_score", 0) or 0)
    action = str(row.get("action", "")).lower()

    if score >= 0.8:
        reasons.append("High anomaly score from ML model")
    elif score >= 0.5:
        reasons.append("Moderate anomaly score from ML model")
    if ti >= 7:
        reasons.append("Threat Intelligence indicates high risk for source IP")
    if "role" in action or "attach" in action or "policy" in action:
        reasons.append("IAM role or policy change observed (privilege escalation risk)")
    if "consolelogin" in action.lower() or "login" in action.lower():
        if int(float(row.get("ml_hourly_count", 0) or 0)) > 10:
            reasons.append("Multiple login events (possible brute force or automation)")
    if not reasons:
        reasons.append("Unusual combination of features flagged by model")

    suggestion = "Investigate user activity and check recent IAM changes. Consider MFA check and token revocation if suspicious."
    confidence = min(0.95, 0.2 + score * 0.7 + min(ti / 10.0, 0.2))
    reasoning_text = " • ".join(reasons)
    return {"reasoning": reasoning_text, "suggestion": suggestion, "confidence": round(confidence, 2)}

# LLM call wrapper (OpenAI)
def llm_reasoning(row):
    if not openai:
        return None
    event_summary = {
        "timestamp": row.get("timestamp"),
        "user": row.get("user"),
        "action": row.get("action"),
        "src_ip": row.get("src_ip"),
        "alert_score": float(row.get("alert_score", 0) or 0),
        "ti_score": float(row.get("ti_score", 0) or 0),
        "prelim_priority": row.get("prelim_priority", "")
    }
    prompt = LLM_PROMPT_TEMPLATE.format(event=event_summary)
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # if not available in your account, change to supported model
            messages=[{"role": "system", "content": "You are a cloud security analyst."},
                      {"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0.2,
        )
        text = resp["choices"][0]["message"]["content"].strip()
        # Expect user JSON — but we'll be forgiving: try to parse lines
        # Simple parsing: find 'reasoning:' and 'suggestion:' if present
        reasoning = None
        suggestion = None
        confidence = None
        # naive parse
        if "reasoning" in text.lower() and "suggestion" in text.lower():
            # try to extract by lines
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            for l in lines:
                low = l.lower()
                if low.startswith("reasoning"):
                    reasoning = l.split(":", 1)[1].strip()
                elif low.startswith("suggestion"):
                    suggestion = l.split(":", 1)[1].strip()
                elif low.startswith("confidence"):
                    try:
                        confidence = float(l.split(":", 1)[1].strip())
                    except:
                        confidence = None
        # fallback: whole text as reasoning
        if not reasoning:
            reasoning = text
        if not suggestion:
            suggestion = "Investigate in console and verify user's recent actions."
        if confidence is None:
            confidence = min(0.99, 0.5 + float(event_summary["alert_score"]) * 0.4 + float(event_summary["ti_score"]) / 25.0)
        return {"reasoning": reasoning, "suggestion": suggestion, "confidence": round(float(confidence), 2)}
    except Exception as e:
        print("LLM call failed:", e)
        return None

# Process function: read current final file (if exists), merge new alerts, generate reasoning for high alerts
def process_alerts_once():
    # Prefer final_alerts if present; otherwise read scored_logs
    path_in = FINAL_PATH if os.path.exists(FINAL_PATH) else SCORED_PATH
    df_in = safe_read_csv(path_in)
    if df_in.empty:
        print("No input file to process:", path_in)
        return

    # ensure id column for row-level merging
    if "event_id" not in df_in.columns:
        df_in = df_in.reset_index().rename(columns={"index": "event_id"})

    # load existing final (to preserve existing reasoning)
    existing = safe_read_csv(FINAL_PATH) if os.path.exists(FINAL_PATH) else pd.DataFrame()
    existing_ids = set(existing.get("event_id", existing.index.tolist())) if not existing.empty else set()

    # Find candidate alerts to process
    now_ts = datetime.utcnow().isoformat() + "Z"
    to_process = []
    for _, row in df_in.iterrows():
        eid = row.get("event_id")
        try:
            alert_score = float(row.get("alert_score", 0) or 0)
        except:
            alert_score = 0.0
        # process if alert_score high and not already processed recently
        if alert_score >= AGENT_MIN_ALERT_SCORE and (eid not in existing_ids):
            to_process.append(row)

    if not to_process:
        print("No new high-priority alerts to process (count=0).")
    else:
        print(f"Processing {len(to_process)} alert(s) with agentic reasoning...")
    results = []
    for row in to_process:
        r = row.to_dict()
        # First try LLM
        llm_out = llm_reasoning(r) if openai and OPENAI_API_KEY else None
        if llm_out:
            reasoning = llm_out["reasoning"]
            suggestion = llm_out["suggestion"]
            confidence = llm_out["confidence"]
        else:
            fb = rule_based_reasoning(r)
            reasoning = fb["reasoning"]
            suggestion = fb["suggestion"]
            confidence = fb["confidence"]
        r["reasoning_text"] = reasoning
        r["agent_action"] = suggestion
        r["agent_confidence"] = confidence
        r["agent_timestamp"] = now_ts
        results.append(r)
        print(f" -> processed event_id={r.get('event_id')} score={r.get('alert_score')} confidence={confidence}")

    # Append results to existing final dataframe (merge on event_id)
    if not results:
        return
    df_results = pd.DataFrame(results)
    if existing.empty:
        out = df_results
    else:
        # combine: keep existing rows + new ones (avoid duplicates)
        existing_ids = set(existing.get("event_id", []))
        new_only = df_results[~df_results["event_id"].isin(existing_ids)]
        out = pd.concat([existing, new_only], ignore_index=True, sort=False)

    # If there were rows in input that weren't in final, ensure they are included
    # Merge full input with agent columns where present
    merged = df_in.merge(out[["event_id", "reasoning_text", "agent_action", "agent_confidence", "agent_timestamp"]],
                         on="event_id", how="left")
    # If reasoning exists in out use it; else keep any existing
    merged.to_csv(FINAL_PATH, index=False)
    print(f"✅ Wrote updated final alerts to {FINAL_PATH} (total rows {len(merged)})")

# Watchdog event handler
class DataChangeHandler(FileSystemEventHandler):
    def __init__(self, paths_to_watch):
        super().__init__()
        self.paths_to_watch = set(os.path.abspath(p) for p in paths_to_watch)

    def on_modified(self, event):
        path = os.path.abspath(event.src_path)
        if any(path.endswith(p) or path == p for p in self.paths_to_watch):
            print(f"Detected change in {path} -> processing alerts")
            try:
                process_alerts_once()
            except Exception as e:
                print("Error processing alerts:", e)

    def on_created(self, event):
        self.on_modified(event)

def run_watcher():
    # ensure data dir exists
    os.makedirs(DATA_DIR, exist_ok=True)
    monitored = [os.path.normpath(SCORED_PATH), os.path.normpath(FINAL_PATH)]
    if Observer is None:
        print("watchdog not available; falling back to polling every", POLL_INTERVAL, "seconds.")
        while True:
            try:
                process_alerts_once()
            except Exception as e:
                print("Process error:", e)
            time.sleep(POLL_INTERVAL)
    else:
        event_handler = DataChangeHandler(monitored)
        observer = Observer()
        observer.schedule(event_handler, path=os.path.abspath(DATA_DIR), recursive=False)
        observer.start()
        print("Agent watcher started. Monitoring:", monitored)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == "__main__":
    print("Starting Agentic core (agent_core.py). CTRL+C to stop.")
    # run initial process once
    try:
        process_alerts_once()
    except Exception as e:
        print("Initial processing error:", e)
    # start watcher loop
    run_watcher()
