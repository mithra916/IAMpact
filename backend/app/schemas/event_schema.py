from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NormalizedEvent(BaseModel):
    timestamp: datetime
    src_ip: Optional[str]
    user: Optional[str]
    action: Optional[str]
    result: Optional[str]
    event_type: str
    raw_log: str