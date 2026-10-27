from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Invoice, InvoiceStatus

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.post("/paypal")
def paypal_webhook(payload: dict, db: Session = Depends(get_db)) -> dict:
    # Minimal: look up invoice by paypal_invoice_id in resource and mark paid
    resource = payload.get("resource", {}) if isinstance(payload, dict) else {}
    paypal_id = resource.get("id") if isinstance(resource, dict) else None
    paypal_id = paypal_id or payload.get("invoice_id")
    invoice = None
    if paypal_id:
        invoice = db.query(Invoice).filter(Invoice.paypal_invoice_id == paypal_id).first()
        if invoice is None:
            try:
                invoice = db.query(Invoice).filter(Invoice.id == int(paypal_id)).first()
            except (ValueError, TypeError):
                invoice = None
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    event_type = payload.get("event_type", "")
    if "PAID" in event_type.upper() or "COMPLETED" in event_type.upper():
        invoice.status = InvoiceStatus.paid
        db.commit()
    return {"status": "ok"}