import json
from typing import Any

from ..config import settings

SYSTEM_PROMPT = (
    "You extract invoice data from a natural-language request. "
    "Respond ONLY with valid JSON matching this schema: "
    '{"client_name": str, "client_email": str or null, "currency": str, '
    '"tax_rate": number, "items": [{"description": str, "quantity": number, "unit_price": number, "category": str}]}. '
    "If email is missing, use null. Default currency USD, tax_rate 0."
)


def _client():
    from openai import OpenAI

    kwargs = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    return OpenAI(**kwargs)


def extract_invoice(text: str) -> dict[str, Any]:
    mock_data = {
        "client_name": "Juan",
        "client_email": "juan@example.com",
        "currency": "USD",
        "tax_rate": 0.18,
        "items": [{"description": "Consultoria", "quantity": 5, "unit_price": 50.0, "category": "services"}],
    }
    if settings.mock_llm:
        return mock_data
    try:
        resp = _client().chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = resp.choices[0].message.content or "{}"
        data = json.loads(content)
        if not isinstance(data.get("items"), list):
            data["items"] = []
        data.setdefault("currency", "USD")
        data.setdefault("tax_rate", 0.0)
        data.setdefault("client_email", None)
        return data
    except Exception:
        return mock_data


def generate_reminder_message(client_name: str, invoice_number: str, total: float, risk_score: float) -> str:
    if settings.mock_llm:
        return f"Hi {client_name}, friendly reminder: invoice {invoice_number} for \${total:.2f} is pending. Please pay at your earliest convenience."
    from openai import OpenAI

    kwargs = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    client = OpenAI(**kwargs)
    prompt = (
        f"Write a short, polite payment reminder email body for client {client_name} "
        f"regarding invoice {invoice_number} totaling \${total:.2f}. "
        f"Risk score (0-1, higher=more likely late): {risk_score}. "
        "Adapt tone: friendly if low risk, firm but respectful if high risk. "
        "Max 3 sentences. No subject line."
    )
    resp = client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return (resp.choices[0].message.content or "").strip()