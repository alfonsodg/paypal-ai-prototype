import os
import uuid

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("PAYPAL_CLIENT_ID", "test")
os.environ.setdefault("PAYPAL_CLIENT_SECRET", "test")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
os.environ.setdefault("BACKEND_URL", "http://localhost:8000")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import Client, Invoice, InvoiceStatus

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


def test_webhook_marks_paid():
    db = TestingSession()
    c = Client(name="C", email="c@example.com")
    db.add(c)
    db.flush()
    paypal_id = f"PAY-{uuid.uuid4().hex[:6]}"
    inv = Invoice(client_id=c.id, number=f"INV-{uuid.uuid4().hex[:6]}", currency="USD",
                  subtotal=10, tax=0, total=10, status=InvoiceStatus.pending, paypal_invoice_id=paypal_id)
    db.add(inv)
    db.commit()
    db.refresh(inv)
    iid = inv.id
    db.close()

    r = client.post("/api/v1/webhooks/paypal", json={"event_type": "PAYMENT.CAPTURE.COMPLETED", "resource": {"id": paypal_id}})
    assert r.status_code == 200

    db = TestingSession()
    updated = db.query(Invoice).filter(Invoice.id == iid).first()
    assert updated.status == InvoiceStatus.paid
    db.close()