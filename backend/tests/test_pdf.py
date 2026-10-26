import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("PAYPAL_CLIENT_ID", "test")
os.environ.setdefault("PAYPAL_CLIENT_SECRET", "test")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
os.environ.setdefault("BACKEND_URL", "http://localhost:8000")

from app.services.pdf import generate_invoice_pdf


def test_generate_invoice_pdf():
    data = {
        "number": "INV-1",
        "client": {"name": "Juan", "email": "juan@example.com"},
        "items": [{"description": "Consultoria", "quantity": 5, "unit_price": 50.0, "amount": 250.0}],
        "subtotal": 250.0,
        "tax": 45.0,
        "total": 295.0,
        "payment_link": "https://paypal.com/pay",
    }
    pdf = generate_invoice_pdf(data)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 100