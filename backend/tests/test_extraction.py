import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("PAYPAL_CLIENT_ID", "test")
os.environ.setdefault("PAYPAL_CLIENT_SECRET", "test")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
os.environ.setdefault("BACKEND_URL", "http://localhost:8000")

from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_extract_endpoint():
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = (
        '{"client_name":"Juan","client_email":"juan@example.com","currency":"USD",'
        '"tax_rate":0.18,"items":[{"description":"Consultoria","quantity":5,"unit_price":50.0}]}'
    )
    with patch("app.services.llm_extraction._client") as m:
        m.return_value.chat.completions.create.return_value = mock_resp
        r = client.post("/api/v1/extract", json={"text": "Factura a Juan por 5 horas a 50"})
    assert r.status_code == 200
    data = r.json()
    assert data["client_name"] == "Juan"
    assert len(data["items"]) == 1