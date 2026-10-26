import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("PAYPAL_CLIENT_ID", "test")
os.environ.setdefault("PAYPAL_CLIENT_SECRET", "test")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
os.environ.setdefault("BACKEND_URL", "http://localhost:8000")

from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
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


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_and_list_invoice():
    payload = {
        "client_name": "Juan",
        "client_email": "juan@example.com",
        "tax_rate": 0.18,
        "items": [{"description": "Consultoria", "quantity": 5, "unit_price": 50.0}],
    }
    r = client.post("/api/v1/invoices", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "pending"
    assert data["subtotal"] == 250.0
    assert data["tax"] == 45.0
    assert data["total"] == 295.0
    assert len(data["items"]) == 1

    r2 = client.get("/api/v1/invoices")
    assert r2.status_code == 200
    assert len(r2.json()) >= 1


def test_get_invoice_not_found():
    r = client.get("/api/v1/invoices/99999")
    assert r.status_code == 404