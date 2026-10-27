import httpx

from ..config import settings


def notify(event: str, payload: dict) -> None:
    if settings.outgoing_webhook_url:
        try:
            httpx.post(settings.outgoing_webhook_url, json={"event": event, "data": payload}, timeout=10)
        except Exception:
            pass
    if settings.slack_webhook_url:
        try:
            httpx.post(settings.slack_webhook_url, json={"text": f"[{event}] {payload}"}, timeout=10)
        except Exception:
            pass