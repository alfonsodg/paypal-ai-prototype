from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..services.analytics import analytics_summary

router = APIRouter(prefix="/api/v1", tags=["analytics"])


@router.get("/analytics")
def analytics(db: Session = Depends(get_db)) -> dict:
    return analytics_summary(db)