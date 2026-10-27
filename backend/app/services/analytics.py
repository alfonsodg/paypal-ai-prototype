from collections import defaultdict

from sqlalchemy.orm import Session

from ..models import Invoice, InvoiceStatus


def revenue_by_month(db: Session) -> list[dict]:
    buckets: dict[str, dict] = defaultdict(lambda: {"billed": 0.0, "paid": 0.0})
    for inv in db.query(Invoice).all():
        key = inv.created_at.strftime("%Y-%m") if inv.created_at else "unknown"
        buckets[key]["billed"] += inv.total
        if inv.status == InvoiceStatus.paid:
            buckets[key]["paid"] += inv.total
    return [{"month": k, "billed": round(v["billed"], 2), "paid": round(v["paid"], 2)} for k, v in sorted(buckets.items())]


def top_clients(db: Session, limit: int = 5) -> list[dict]:
    agg: dict[int, dict] = defaultdict(lambda: {"total": 0.0, "count": 0})
    for inv in db.query(Invoice).all():
        agg[inv.client_id]["total"] += inv.total
        agg[inv.client_id]["count"] += 1
    from ..models import Client

    result = []
    for cid, v in agg.items():
        client = db.query(Client).filter(Client.id == cid).first()
        result.append({"name": client.name if client else f"#{cid}", "total": round(v["total"], 2), "count": v["count"]})
    result.sort(key=lambda x: x["total"], reverse=True)
    return result[:limit]


def avg_days_to_pay(db: Session) -> float:
    days = []
    for inv in db.query(Invoice).filter(Invoice.status == InvoiceStatus.paid).all():
        if inv.created_at and inv.due_date:
            delta = (inv.due_date - inv.created_at).days
            days.append(max(0, delta))
    if not days:
        return 0.0
    return round(sum(days) / len(days), 1)


def analytics_summary(db: Session) -> dict:
    return {
        "revenue_by_month": revenue_by_month(db),
        "top_clients": top_clients(db),
        "avg_days_to_pay": avg_days_to_pay(db),
    }