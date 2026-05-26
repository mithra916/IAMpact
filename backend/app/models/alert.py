from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime

from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    timestamp = Column(DateTime, default=datetime.utcnow)

    src_ip = Column(String)
    user = Column(String)
    event_type = Column(String)

    severity = Column(String)
    risk_score = Column(Integer)

    ai_reasoning = Column(Text, nullable=True)

    status = Column(String, default="OPEN")