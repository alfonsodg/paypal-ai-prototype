import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("PAYPAL_CLIENT_ID", "test")
os.environ.setdefault("PAYPAL_CLIENT_SECRET", "test")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
os.environ.setdefault("BACKEND_URL", "http://localhost:8000")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metrics_endpoint():
    r = client.get("/api/v1/metrics")
    assert r.status_code == 200
    data = r.json()
    assert "total_billed" in data
    assert "count" in data


def test_cashflow_forecast():
    r = client.get("/api/v1/cashflow/forecast?horizon=30")
    assert r.status_code == 200
    data = r.json()
    assert data["horizon_days"] == 30