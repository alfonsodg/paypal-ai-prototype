import csv
import io
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import AuditLog, Client, CreditNote, Invoice, InvoiceStatus, LineItem, Payment
from ..schemas import InvoiceCreate, InvoiceOut
from ..services.email import send_invoice_email
from ..services.llm_extraction import generate_reminder_message
from ..services.pdf import generate_invoice_pdf
from ..services.paypal import create_paypal_invoice
from ..services.risk import client_risk_score
from ..services.webhooks_out import notify

router = APIRouter(prefix="/api/v1/invoices", tags=["invoices"])


def _get_or_create_client(db: Session, name: str, email: str) -> Client:
    client = db.query(Client).filter(Client.email == email).first()
    if client is None:
        client = Client(name=name, email=email)
        db.add(client)
        db.flush()
    return client


@router.post("", response_model=InvoiceOut, status_code=201)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)) -> Invoice:
    client = _get_or_create_client(db, payload.client_name, payload.client_email)
    subtotal = sum(i.quantity * i.unit_price for i in payload.items)
    tax = round(subtotal * payload.tax_rate, 2)
    total = round(subtotal + tax, 2)
    invoice = Invoice(
        client_id=client.id,
        number=f"INV-{uuid.uuid4().hex[:8].upper()}",
        currency=payload.currency,
        exchange_rate=payload.exchange_rate,
        subtotal=round(subtotal, 2),
        tax=tax,
        total=total,
        status=InvoiceStatus.pending,
        due_date=payload.due_date,
    )
    for item in payload.items:
        invoice.items.append(
            LineItem(
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                amount=round(item.quantity * item.unit_price, 2),
            )
        )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    db.add(AuditLog(entity="invoice", entity_id=invoice.id, action="created", details=f"number={invoice.number} total={invoice.total}"))
    db.commit()
    notify("invoice.created", {"id": invoice.id, "number": invoice.number, "total": invoice.total, "status": invoice.status.value})
    return invoice


@router.get("", response_model=list[InvoiceOut])
def list_invoices(
    status: str | None = None,
    client: str | None = None,
    search: str | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
    db: Session = Depends(get_db),
) -> list[Invoice]:
    q = db.query(Invoice)
    if status:
        q = q.filter(Invoice.status == status)
    if client:
        q = q.join(Invoice.client).filter(Client.name.ilike(f"%{client}%"))
    if search:
        q = q.filter(Invoice.number.ilike(f"%{search}%"))
    if min_amount is not None:
        q = q.filter(Invoice.total >= min_amount)
    if max_amount is not None:
        q = q.filter(Invoice.total <= max_amount)
    return q.order_by(Invoice.created_at.desc()).all()


@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db)) -> StreamingResponse:
    invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["number", "client", "status", "currency", "subtotal", "tax", "total", "created_at"])
    for inv in invoices:
        writer.writerow([inv.number, inv.client.name, inv.status.value, inv.currency, inv.subtotal, inv.tax, inv.total, inv.created_at])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=invoices.csv"})


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)) -> Invoice:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.get("/{invoice_id}/pdf")
def invoice_pdf(invoice_id: int, db: Session = Depends(get_db)) -> Response:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    data = {
        "number": invoice.number,
        "client": {"name": invoice.client.name, "email": invoice.client.email},
        "items": [
            {
                "description": i.description,
                "quantity": i.quantity,
                "unit_price": i.unit_price,
                "amount": i.amount,
            }
            for i in invoice.items
        ],
        "subtotal": invoice.subtotal,
        "tax": invoice.tax,
        "total": invoice.total,
        "payment_link": invoice.payment_link,
    }
    pdf_bytes = generate_invoice_pdf(data)
    return Response(content=pdf_bytes, media_type="application/pdf")


@router.post("/{invoice_id}/send-paypal")
def send_paypal(invoice_id: int, db: Session = Depends(get_db)) -> InvoiceOut:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    paypal_data = {
        "number": invoice.number,
        "currency": invoice.currency,
        "client_name": invoice.client.name,
        "client_email": invoice.client.email,
        "items": [
            {
                "description": i.description,
                "quantity": i.quantity,
                "unit_price": i.unit_price,
            }
            for i in invoice.items
        ],
    }
    result = create_paypal_invoice(paypal_data)
    invoice.paypal_invoice_id = result["paypal_invoice_id"]
    invoice.payment_link = result["payment_link"]
    db.commit()
    db.refresh(invoice)
    return invoice


@router.post("/{invoice_id}/remind")
def remind(invoice_id: int, db: Session = Depends(get_db)) -> dict:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    pdf = generate_invoice_pdf(
        {
            "number": invoice.number,
            "client": {"name": invoice.client.name, "email": invoice.client.email},
            "items": [
                {
                    "description": i.description,
                    "quantity": i.quantity,
                    "unit_price": i.unit_price,
                    "amount": i.amount,
                }
                for i in invoice.items
            ],
            "subtotal": invoice.subtotal,
            "tax": invoice.tax,
            "total": invoice.total,
            "payment_link": invoice.payment_link,
        }
    )
    risk = client_risk_score(db, invoice.client_id)
    message = generate_reminder_message(invoice.client.name, invoice.number, invoice.total, risk)
    send_invoice_email(
        invoice.client.email,
        f"Reminder: Invoice {invoice.number}",
        f"{message}\n\nPay here: {invoice.payment_link or ''}",
        pdf,
    )
    return {"status": "sent", "risk_score": risk}


class PaymentPayload(BaseModel):
    amount: float
    status: str = "completed"


class CreditNotePayload(BaseModel):
    amount: float
    reason: str | None = None


@router.post("/{invoice_id}/payments")
def record_payment(invoice_id: int, payload: PaymentPayload, db: Session = Depends(get_db)) -> dict:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    payment = Payment(invoice_id=invoice.id, amount=payload.amount, status=payload.status)
    db.add(payment)
    paid_total = sum(p.amount for p in invoice.payments) + payload.amount
    if paid_total >= invoice.total:
        invoice.status = InvoiceStatus.paid
    db.commit()
    return {"status": invoice.status.value, "paid_total": round(paid_total, 2), "total": invoice.total}


@router.post("/{invoice_id}/credit-note")
def create_credit_note(invoice_id: int, payload: CreditNotePayload, db: Session = Depends(get_db)) -> dict:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    cn = CreditNote(invoice_id=invoice.id, amount=payload.amount, reason=payload.reason)
    db.add(cn)
    db.commit()
    db.refresh(cn)
    return {"id": cn.id, "amount": cn.amount, "reason": cn.reason}