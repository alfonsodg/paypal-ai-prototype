from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Invoice
from ..services.query_parser import parse_natural_query

router = APIRouter(prefix="/api/v1", tags=["queries"])


class QueryRequest(BaseModel):
    text: str


@router.post("/query")
def query_invoices(payload: QueryRequest, db: Session = Depends(get_db)) -> list[dict]:
    filters = parse_natural_query(payload.text)
    q = db.query(Invoice)
    if filters.get("status"):
        q = q.filter(Invoice.status == filters["status"])
    if filters.get("client"):
        from ..models import Client

        q = q.join(Client).filter(Client.name.ilike(f"%{filters['client']}%"))
    if filters.get("search"):
        q = q.filter(Invoice.number.ilike(f"%{filters['search']}%"))
    if filters.get("min_amount") is not None:
        q = q.filter(Invoice.total >= filters["min_amount"])
    if filters.get("max_amount") is not None:
        q = q.filter(Invoice.total <= filters["max_amount"])
    invoices = q.order_by(Invoice.created_at.desc()).all()
    return [{"id": i.id, "number": i.number, "status": i.status.value, "total": i.total, "client": i.client.name} for i in invoices]