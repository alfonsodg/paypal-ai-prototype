import json

from ..config import settings


def parse_natural_query(text: str) -> dict:
    if settings.mock_llm:
        return {"status": None, "client": None, "search": None, "min_amount": None, "max_amount": None}
    default = {"status": None, "client": None, "search": None, "min_amount": None, "max_amount": None}
    try:
        from openai import OpenAI

        kwargs = {"api_key": settings.openai_api_key}
        if settings.openai_base_url:
            kwargs["base_url"] = settings.openai_base_url
        client = OpenAI(**kwargs)
        system = (
            "Parse a natural language query about invoices into JSON filters. "
            "Schema: {\"status\": one of pending/paid/overdue or null, \"client\": string or null, "
            "\"search\": string or null, \"min_amount\": number or null, \"max_amount\": number or null}. "
            "Respond ONLY with valid JSON."
        )
        resp = client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": text}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        return json.loads(resp.choices[0].message.content or "{}")
    except Exception:
        return default