from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class LineItemIn(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0


class LineItemOut(LineItemIn):
    id: int
    amount: float


class InvoiceCreate(BaseModel):
    client_name: str
    client_email: EmailStr
    currency: str = "USD"
    tax_rate: float = 0.0
    due_date: Optional[datetime] = None
    items: List[LineItemIn] = Field(default_factory=list)


class InvoiceOut(BaseModel):
    id: int
    number: str
    client_id: int
    currency: str
    subtotal: float
    tax: float
    total: float
    status: str
    due_date: Optional[datetime] = None
    payment_link: Optional[str] = None
    created_at: datetime
    items: List[LineItemOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}