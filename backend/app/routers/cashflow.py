from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Invoice, InvoiceStatus
from ..services.risk import projected_cashflow

router = APIRouter(prefix="/api/v1", tags=["cashflow"])


@router.get("/cashflow/forecast")
def forecast(horizon: int = 30, db: Session = Depends(get_db)) -> dict:
    return projected_cashflow(db, horizon)


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)) -> dict:
    invoices = db.query(Invoice).all()
    billed = sum(i.total for i in invoices)
    paid = sum(i.total for i in invoices if i.status == InvoiceStatus.paid)
    pending = sum(i.total for i in invoices if i.status == InvoiceStatus.pending)
    return {
        "total_billed": round(billed, 2),
        "total_paid": round(paid, 2),
        "total_pending": round(pending, 2),
        "count": len(invoices),
    }