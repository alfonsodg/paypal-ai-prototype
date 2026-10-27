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


def test_analytics_endpoint():
    r = client.get("/api/v1/analytics")
    assert r.status_code == 200
    data = r.json()
    assert "revenue_by_month" in data
    assert "top_clients" in data
    assert "avg_days_to_pay" in data