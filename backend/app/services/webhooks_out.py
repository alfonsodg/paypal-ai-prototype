import httpx

from ..config import settings


def notify(event: str, payload: dict) -> None:
    if not settings.outgoing_webhook_url:
        return
    try:
        httpx.post(settings.outgoing_webhook_url, json={"event": event, "data": payload}, timeout=10)
    except Exception:
        pass