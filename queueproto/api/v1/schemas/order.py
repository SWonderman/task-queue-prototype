import datetime
import uuid
from typing import Optional, List
from pydantic import BaseModel, field_validator

from core.definitions import OrderState


class BaseSchema(BaseModel):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime


class Customer(BaseSchema):
    first_name: str
    last_name: str
    address1: str
    address2: Optional[str]
    zip_code: str
    country: str


class OrderItem(BaseSchema):
    product_sku: str
    product_title: str
    product_media_url: Optional[str]
    price: float
    quantity: int


class Order(BaseSchema):
    total_price: float
    total_quantity: int
    state: OrderState
    currency_iso_code: str
    placed_at: datetime.datetime
    order_items: List[OrderItem]
    customer: Customer


class OrderIds(BaseModel):
    order_ids: List[str]
