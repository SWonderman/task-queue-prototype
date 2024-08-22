from datetime import datetime
from typing import Optional, List, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum

T = TypeVar("T")


@dataclass
class Error:
    message: str


@dataclass
class Result(Generic[T]):
    errors: List[Error]
    result: T


class OrderState(str, Enum):
    SHIPPING = "SHIPPING"
    SHIPPED = "SHIPPED"
    CANCELED = "CANCELED"


@dataclass
class Customer:
    first_name: str
    last_name: str
    address1: str
    address2: Optional[str]
    zip_code: str
    country: str


@dataclass
class OrderItem:
    product_sku: str
    product_title: str
    product_media_url: Optional[str]
    price: float
    quantity: int


@dataclass
class OrderShipment:
    shipment_id: str
    carrier_name: str
    carrier_code: str


@dataclass
class Order:
    total_price: float
    total_quantity: int
    state: OrderState
    currency_iso_code: str
    placed_at: datetime
    order_items: List[OrderItem]
    customer: Customer
