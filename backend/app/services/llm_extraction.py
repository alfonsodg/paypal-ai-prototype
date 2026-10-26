import json
from typing import Any

from ..config import settings

SYSTEM_PROMPT = (
    "You extract invoice data from a natural-language request. "
    "Respond ONLY with valid JSON matching this schema: "
    '{"client_name": str, "client_email": str or null, "currency": str, '
    '"tax_rate": number, "items": [{"description": str, "quantity": number, "unit_price": number}]}. '
    "If email is missing, use null. Default currency USD, tax_rate 0."
)


def _client():
    from openai import OpenAI

    return OpenAI(api_key=settings.openai_api_key)


def extract_invoice(text: str) -> dict[str, Any]:
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