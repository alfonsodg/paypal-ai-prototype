from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Client, Invoice, InvoiceStatus, LineItem, RecurringInvoice

router = APIRouter(prefix="/api/v1", tags=["recurring"])


class RecurringIn(BaseModel):
    client_id: int
    description: str
    amount: float
    currency: str = "USD"
    frequency: str = "monthly"


@router.post("/recurring")
def create_recurring(payload: RecurringIn, db: Session = Depends(get_db)) -> dict:
    client = db.query(Client).filter(Client.id == payload.client_id).first()
    if not client:
        return {"error": "client not found"}
    next_run = datetime.utcnow() + (timedelta(days=7) if payload.frequency == "weekly" else timedelta(days=30))
    ri = RecurringInvoice(
        client_id=payload.client_id,
        description=payload.description,
        amount=payload.amount,
        currency=payload.currency,
        frequency=payload.frequency,
        next_run=next_run,
    )
    db.add(ri)
    db.commit()
    db.refresh(ri)
    return {"id": ri.id, "next_run": ri.next_run, "frequency": ri.frequency}


@router.get("/recurring")
def list_recurring(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(RecurringInvoice).all()
    return [{"id": r.id, "client_id": r.client_id, "description": r.description, "amount": r.amount, "currency": r.currency, "frequency": r.frequency, "next_run": r.next_run, "active": r.active} for r in rows]


@router.post("/recurring/run")
def run_recurring(db: Session = Depends(get_db)) -> dict:
    now = datetime.utcnow()
    due = db.query(RecurringInvoice).filter(RecurringInvoice.active.is_(True), RecurringInvoice.next_run <= now).all()
    created = 0
    for ri in due:
        client = db.query(Client).filter(Client.id == ri.client_id).first()
        if not client:
            continue
        inv = Invoice(client_id=client.id, number=f"REC-{ri.id}-{int(now.timestamp())}", currency=ri.currency, subtotal=ri.amount, tax=0.0, total=ri.amount, status=InvoiceStatus.pending)
        inv.items.append(LineItem(description=ri.description, quantity=1, unit_price=ri.amount, amount=ri.amount))
        db.add(inv)
        if ri.frequency == "weekly":
            ri.next_run = now + timedelta(days=7)
        else:
            ri.next_run = now + timedelta(days=30)
        created += 1
    db.commit()
    return {"created": created}