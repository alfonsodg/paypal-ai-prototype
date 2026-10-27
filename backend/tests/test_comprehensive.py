import os
import uuid

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("PAYPAL_CLIENT_ID", "test")
os.environ.setdefault("PAYPAL_CLIENT_SECRET", "test")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
os.environ.setdefault("BACKEND_URL", "http://localhost:8000")
os.environ.setdefault("MOCK_LLM", "true")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def _create_invoice(client_name="Juan", email=None, tax_rate=0.18, items=None, currency="USD"):
    email = email or f"{client_name.lower()}-{uuid.uuid4().hex[:4]}@example.com"
    items = items or [{"description": "Consultoria", "quantity": 5, "unit_price": 50.0}]
    r = client.post("/api/v1/invoices", json={
        "client_name": client_name, "client_email": email, "currency": currency,
        "tax_rate": tax_rate, "items": items,
    })
    assert r.status_code == 201, r.text
    return r.json()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_invoice_create_semantics():
    inv = _create_invoice(tax_rate=0.18, items=[{"description": "A", "quantity": 2, "unit_price": 10.0}])
    assert inv["subtotal"] == 20.0
    assert inv["tax"] == 3.6
    assert inv["total"] == 23.6
    assert inv["status"] == "pending"
    assert inv["late_fee"] == 0.0
    assert len(inv["items"]) == 1
    assert inv["items"][0]["amount"] == 20.0


def test_invoice_list_and_get():
    inv = _create_invoice()
    r = client.get("/api/v1/invoices")
    assert r.status_code == 200
    assert any(i["id"] == inv["id"] for i in r.json())
    r2 = client.get(f"/api/v1/invoices/{inv['id']}")
    assert r2.status_code == 200
    assert r2.json()["id"] == inv["id"]
    r3 = client.get("/api/v1/invoices/99999")
    assert r3.status_code == 404


def test_invoice_filters():
    _create_invoice(client_name="FilterTest", tax_rate=0.0)
    r = client.get("/api/v1/invoices?status=pending")
    assert r.status_code == 200
    assert all(i["status"] == "pending" for i in r.json())
    r2 = client.get("/api/v1/invoices?min_amount=1")
    assert r2.status_code == 200
    r3 = client.get("/api/v1/invoices?search=INV")
    assert r3.status_code == 200


def test_pdf_endpoint():
    inv = _create_invoice()
    r = client.get(f"/api/v1/invoices/{inv['id']}/pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"


def test_extract_endpoint():
    r = client.post("/api/v1/extract", json={"text": "Factura a Juan por 5 horas a 50"})
    assert r.status_code == 200
    data = r.json()
    assert data["client_name"] == "Juan"
    assert len(data["items"]) >= 1
    assert "category" in data["items"][0]


def test_query_endpoint():
    _create_invoice(client_name="QueryTest")
    r = client.post("/api/v1/query", json={"text": "all invoices"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_export_csv():
    r = client.get("/api/v1/invoices/export/csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")
    assert "number,client,status" in r.text


def test_metrics():
    _create_invoice()
    r = client.get("/api/v1/metrics")
    assert r.status_code == 200
    d = r.json()
    assert "total_billed" in d and "total_paid" in d and "total_pending" in d and "count" in d
    assert d["count"] >= 1


def test_cashflow_forecast():
    r = client.get("/api/v1/cashflow/forecast?horizon=30")
    assert r.status_code == 200
    d = r.json()
    assert d["horizon_days"] == 30
    assert "expected_amount" in d
    assert "risk_adjusted_amount" in d


def test_analytics():
    r = client.get("/api/v1/analytics")
    assert r.status_code == 200
    d = r.json()
    assert "revenue_by_month" in d
    assert "top_clients" in d
    assert "avg_days_to_pay" in d


def test_clients():
    _create_invoice(client_name="ClientTest")
    r = client.get("/api/v1/clients")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1
    c = r.json()[0]
    assert "invoice_count" in c and "total_billed" in c and "total_paid" in c


def test_audit():
    _create_invoice()
    r = client.get("/api/v1/audit")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    # at least one audit entry from invoice creation
    assert len(r.json()) >= 1


def test_recurring_create_and_run():
    _create_invoice(client_name="RecurClient")
    # get client id
    clients = client.get("/api/v1/clients").json()
    cid = clients[0]["id"]
    r = client.post("/api/v1/recurring", json={"client_id": cid, "description": "Monthly", "amount": 100.0, "frequency": "monthly"})
    assert r.status_code == 200
    assert "id" in r.json() and "next_run" in r.json()
    # run (won't create because next_run is in future, but endpoint works)
    r2 = client.post("/api/v1/recurring/run")
    assert r2.status_code == 200
    assert "created" in r2.json()


def test_partial_payment():
    inv = _create_invoice(tax_rate=0.0, items=[{"description": "X", "quantity": 1, "unit_price": 100.0}])
    assert inv["total"] == 100.0
    r = client.post(f"/api/v1/invoices/{inv['id']}/payments", json={"amount": 40.0})
    assert r.status_code == 200
    assert r.json()["status"] == "pending"
    assert r.json()["paid_total"] == 40.0
    r2 = client.post(f"/api/v1/invoices/{inv['id']}/payments", json={"amount": 60.0})
    assert r2.status_code == 200
    assert r2.json()["status"] == "paid"


def test_credit_note():
    inv = _create_invoice()
    r = client.post(f"/api/v1/invoices/{inv['id']}/credit-note", json={"amount": 10.0, "reason": "refund"})
    assert r.status_code == 200
    assert r.json()["amount"] == 10.0
    assert r.json()["reason"] == "refund"


def test_webhook_marks_paid():
    # create invoice via API then set paypal_invoice_id by direct DB
    inv = _create_invoice()
    r = client.post("/api/v1/webhooks/paypal", json={"event_type": "PAYMENT.CAPTURE.COMPLETED", "invoice_id": inv["id"]})
    assert r.status_code == 200
    r2 = client.get(f"/api/v1/invoices/{inv['id']}")
    assert r2.json()["status"] == "paid"


def test_openapi():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    d = r.json()
    assert len(d["paths"]) >= 15
