import json
from typing import Deque, Optional, Iterable, Dict, Any
from collections import deque

from django_redis import get_redis_connection

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

    def enque_orders(self, orders: Iterable[Order]) -> None:
        for order in orders:
            self.recently_added_orders.appendleft(order)

    def pop_order(self) -> Optional[Order]:
        return self.recently_added_orders.pop()

    def has_orders(self) -> bool:
        return len(self.recently_added_orders) > 0


# A wrapper class around a 'raw' redis connection that utlizes
# redis list as a queue
class OrderProcessingEventQueue(metaclass=Singleton):
    def __init__(self):
        self._event_queue_key = "order_processing_status_event_queue"
        self._connection = get_redis_connection("default")

    def enque_processing_status_event(
        self, data: Dict[str, Any]
    ) -> None:
        self._connection.lpush(self._event_queue_key, json.dumps(data))

    def pop_processing_status(
        self
    ) -> Optional[Dict[str, str]]:
        event = self._connection.rpop(self._event_queue_key)

        if not event:
            return None

        return json.loads(event)

    def has_items(self) -> bool:
        return len(self._connection.lrange(self._event_queue_key, 0, -1)) > 0
