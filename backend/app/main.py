from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import Base, engine
from .jobs.scheduler import start_scheduler, stop_scheduler
from .routers.analytics import router as analytics_router
from .routers.clients import router as clients_router
from .routers.audit import router as audit_router
from .routers.cashflow import router as cashflow_router
from .routers.extraction import router as extraction_router
from .routers.invoices import router as invoices_router
from .routers.queries import router as queries_router
from .routers.recurring import router as recurring_router
from .routers.webhooks import router as webhooks_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PayPal AI Prototype", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(invoices_router)
app.include_router(extraction_router)
app.include_router(webhooks_router)
app.include_router(cashflow_router)
app.include_router(analytics_router)
app.include_router(audit_router)
app.include_router(clients_router)
app.include_router(queries_router)
app.include_router(recurring_router)


@app.on_event("startup")
def on_startup() -> None:
    if settings.enable_scheduler:
        start_scheduler()


@app.on_event("shutdown")
def on_shutdown() -> None:
    stop_scheduler()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}