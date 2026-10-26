import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Client, Invoice, InvoiceStatus, LineItem
from ..schemas import InvoiceCreate, InvoiceOut
from ..services.email import send_invoice_email
from ..services.pdf import generate_invoice_pdf
from ..services.paypal import create_paypal_invoice

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
    return invoice


@router.get("", response_model=list[InvoiceOut])
def list_invoices(db: Session = Depends(get_db)) -> list[Invoice]:
    return db.query(Invoice).order_by(Invoice.created_at.desc()).all()


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
    send_invoice_email(
        invoice.client.email,
        f"Reminder: Invoice {invoice.number}",
        f"Please pay invoice {invoice.number}. Total: {invoice.total}. {invoice.payment_link or ''}",
        pdf,
    )
    return {"status": "sent"}