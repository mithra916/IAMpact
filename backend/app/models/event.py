from sqlalchemy import Column, Integer, Text, JSON, DateTime, Boolean
from datetime import datetime

from app.core.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)

    raw_log = Column(Text)

    normalized = Column(JSON)

    processed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)