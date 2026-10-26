from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..models import Invoice, InvoiceStatus


def client_risk_score(db: Session, client_id: int) -> float:
    invoices = db.query(Invoice).filter(Invoice.client_id == client_id).all()
    if not invoices:
        return 0.5
    paid = [i for i in invoices if i.status == InvoiceStatus.paid]
    overdue = [i for i in invoices if i.status == InvoiceStatus.overdue]
    ratio_paid = len(paid) / len(invoices)
    ratio_overdue = len(overdue) / len(invoices)
    return round(min(1.0, max(0.0, 0.5 + 0.5 * ratio_overdue - 0.3 * ratio_paid)), 3)


def projected_cashflow(db: Session, horizon_days: int = 30) -> dict:
    cutoff = datetime.utcnow() + timedelta(days=horizon_days)
    pending = (
        db.query(Invoice)
        .filter(Invoice.status == InvoiceStatus.pending)
        .filter((Invoice.due_date.is_(None)) | (Invoice.due_date <= cutoff))
        .all()
    )
    expected = sum(i.total for i in pending)
    risk_adjusted = 0.0
    for inv in pending:
        score = client_risk_score(db, inv.client_id)
        risk_adjusted += inv.total * (1 - score)
    return {
        "horizon_days": horizon_days,
        "expected_amount": round(expected, 2),
        "risk_adjusted_amount": round(risk_adjusted, 2),
        "pending_count": len(pending),
    }