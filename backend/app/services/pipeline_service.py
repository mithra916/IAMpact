from app.parsing.normalizer import normalize_log
from app.detection.risk_engine import calculate_risk
from app.services.alert_service import create_alert
from app.core.websocket_manager import manager


async def process_event(raw_log: str, db):

    # 1. Normalize
    normalized = normalize_log(raw_log)

    # 2. Risk scoring
    risk = calculate_risk(normalized)
    normalized.update(risk)

    # 3. Store in DB
    alert = create_alert(db, normalized)

    # 4. REALTIME PUSH (WebSocket)
    await manager.broadcast({
        "id": alert.id,
        "src_ip": alert.src_ip,
        "event_type": alert.event_type,
        "severity": alert.severity,
        "risk_score": alert.risk_score
    })

    # 5. Return response
    return {
        "alert_id": alert.id,
        "severity": alert.severity,
        "risk_score": alert.risk_score
    }