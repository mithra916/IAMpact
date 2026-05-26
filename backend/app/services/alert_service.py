from sqlalchemy.orm import Session
from app.models.alert import Alert
from datetime import datetime


def create_alert(db: Session, event: dict):

    alert = Alert(
        timestamp=datetime.utcnow(),
        src_ip=event.get("src_ip"),
        user=event.get("user"),
        event_type=event.get("event_type"),
        severity=event.get("severity"),
        risk_score=event.get("risk_score"),
        status="OPEN"
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert