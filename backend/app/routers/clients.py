from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Client, Invoice, InvoiceStatus

router = APIRouter(prefix="/api/v1", tags=["clients"])


@router.get("/clients")
def list_clients(db: Session = Depends(get_db)) -> list[dict]:
    clients = db.query(Client).all()
    result = []
    for c in clients:
        invoices = db.query(Invoice).filter(Invoice.client_id == c.id).all()
        result.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "tags": c.tags,
            "notes": c.notes,
            "invoice_count": len(invoices),
            "total_billed": round(sum(i.total for i in invoices), 2),
            "total_paid": round(sum(i.total for i in invoices if i.status == InvoiceStatus.paid), 2),
        })
    return result