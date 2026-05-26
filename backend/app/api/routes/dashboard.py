from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.alert import Alert

router = APIRouter()


@router.get("/dashboard-metrics")
def metrics(db: Session = Depends(get_db)):

    total = db.query(Alert).count()
    critical = db.query(Alert).filter(Alert.severity == "CRITICAL").count()
    high = db.query(Alert).filter(Alert.severity == "HIGH").count()

    return {
        "total_alerts": total,
        "critical_alerts": critical,
        "high_alerts": high
    }