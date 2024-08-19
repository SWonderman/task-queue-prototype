from typing import Optional, List
from dataclasses import dataclass
from enum import Enum


@dataclass
class Error:
    message: str


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
class Order:
   total_price: float
   total_quantity: int
   state: OrderState
   currency_iso_code: str
   order_items: List[OrderItem]
   customer: Customer
