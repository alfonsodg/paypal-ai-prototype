import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class InvoiceStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    invoices: Mapped[list["Invoice"]] = relationship(back_populates="client")


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    number: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    tax: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus), default=InvoiceStatus.pending
    )
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    paypal_invoice_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    payment_link: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    @property
    def late_fee(self) -> float:
        from ..config import settings

        if self.status != InvoiceStatus.overdue or not self.due_date:
            return 0.0
        days_overdue = (datetime.utcnow() - self.due_date).days
        if days_overdue <= 0:
            return 0.0
        months = max(1, days_overdue // 30)
        return round(self.total * settings.late_fee_rate * months, 2)

    client: Mapped[Client] = relationship(back_populates="invoices")
    items: Mapped[list["LineItem"]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(back_populates="invoice")


class LineItem(Base):
    __tablename__ = "line_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)
    amount: Mapped[float] = mapped_column(Float, default=0.0)

    invoice: Mapped[Invoice] = relationship(back_populates="items")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    paypal_payment_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    invoice: Mapped[Invoice] = relationship(back_populates="payments")


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), default="email")
    status: Mapped[str] = mapped_column(String(32), default="scheduled")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class CashFlowForecast(Base):
    __tablename__ = "cashflow_forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    horizon_days: Mapped[int] = mapped_column(Integer, nullable=False)
    expected_amount: Mapped[float] = mapped_column(Float, default=0.0)
    risk_adjusted_amount: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())