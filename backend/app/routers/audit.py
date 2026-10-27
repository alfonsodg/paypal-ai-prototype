from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import AuditLog

router = APIRouter(prefix="/api/v1", tags=["audit"])


@router.get("/audit")
def list_audit(limit: int = 50, db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [{"id": r.id, "entity": r.entity, "entity_id": r.entity_id, "action": r.action, "details": r.details, "created_at": r.created_at} for r in rows]