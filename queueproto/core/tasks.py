from typing import List

from django.utils.timezone import now
from django.db.models import QuerySet
from celery import shared_task
from celery.utils.log import get_task_logger

from core.models import Order, OrderShipment, OrderHandlingProcess
from core.events import OrderProcessingStatusEventQueue, OrderProcessingStatusEventQueue

logger = get_task_logger(__name__)

@shared_task(queue="single_worker_queue")
def handle_orders(order_ids: List[str]) -> None:
    if len(order_ids) == 0:
        logger.error(msg="No order IDs were passed to handle orders function.")
        return

    orders: QuerySet[Order] = Order.objects.filter(id__in=order_ids)
    if len(orders) == 0:
        logger.error(msg="No orders were found for the provided IDs")
        return

    event_queue = OrderProcessingStatusEventQueue()
    for order in orders:
        event_queue.enque_processing_status_event(order_id=str(order.id), status="QUEUED")

    for order in orders:
        handle_order.delay(order.id)


@shared_task(queue="single_worker_queue")
def handle_order(order_id: str) -> None:
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        logger.error(msg=f"Error while handling order: order with ID `{order_id}` does not exist.")
        return

    event_queue = OrderProcessingStatusEventQueue()
    event_queue.enque_processing_status_event(order_id=str(order.id), status="PROCESSING")

    started_at = now()

    created_shipment = OrderShipment.create_shipment_for_order(order)
    Order.send_back_tracking_number(order)
    Order.mark_order_as_shipped(order)

    # TODO: handle error/fail path

    event_queue.enque_processing_status_event(order_id=str(order.id), status="PROCESSED")

    OrderHandlingProcess.objects.create(
        status=OrderHandlingProcess.Status.SUCCEEDED,
        state=OrderHandlingProcess.State.HANDLED,
        started_at=started_at,
        finished_at=now(),
        order=order,
    )
