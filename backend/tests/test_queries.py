import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("PAYPAL_CLIENT_ID", "test")
os.environ.setdefault("PAYPAL_CLIENT_SECRET", "test")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
os.environ.setdefault("BACKEND_URL", "http://localhost:8000")
os.environ.setdefault("MOCK_LLM", "true")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_query_endpoint():
    r = client.post("/api/v1/query", json={"text": "all invoices"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_export_csv():
    r = client.get("/api/v1/invoices/export/csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")