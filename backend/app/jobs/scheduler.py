from typing import Any

from ..db import SessionLocal
from ..models import Invoice, InvoiceStatus
from ..services.email import send_invoice_email
from ..services.pdf import generate_invoice_pdf

_scheduler: Any = None


def _send_reminders() -> None:
    db = SessionLocal()
    try:
        invoices = db.query(Invoice).filter(Invoice.status == InvoiceStatus.pending).all()
        for inv in invoices:
            pdf = generate_invoice_pdf(
                {
                    "number": inv.number,
                    "client": {"name": inv.client.name, "email": inv.client.email},
                    "items": [],
                    "subtotal": inv.subtotal,
                    "tax": inv.tax,
                    "total": inv.total,
                    "payment_link": inv.payment_link,
                }
            )
            send_invoice_email(
                inv.client.email,
                f"Reminder: Invoice {inv.number}",
                f"Please pay invoice {inv.number}. Total: {inv.total}.",
                pdf,
            )
    finally:
        db.close()


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
    except ImportError:
        return
    _scheduler = BackgroundScheduler()
    _scheduler.add_job(_send_reminders, "interval", days=1)
    _scheduler.start()


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown()
        _scheduler = None