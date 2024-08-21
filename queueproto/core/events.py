from typing import Deque, List, Optional
from collections import deque

from django.db.models import QuerySet

from core.models import Order


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class OrderEventsQueue(metaclass=Singleton):
    def __init__(self):
       self.recently_added_orders: Deque[Order] = deque()

    def enque_orders(self, orders: List[Order]) -> None:
        for order in orders:
            self.recently_added_orders.appendleft(order)

    def pop_order(self) -> Optional[Order]:
        return self.recently_added_orders.pop()

    def has_orders(self) -> bool:
        return len(self.recently_added_orders) > 0
