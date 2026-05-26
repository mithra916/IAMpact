from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.pipeline_service import process_event

router = APIRouter()


class PasteLogRequest(BaseModel):
    log: str


@router.post("/paste-log")
async def paste_log(payload: PasteLogRequest, db: Session = Depends(get_db)):

    result = await process_event(payload.log, db)

    return result