import asyncio
import json
from typing import AsyncGenerator, Optional, Dict

from fastapi import Request

from core.events import OrderEventsQueue, OrderProcessingEventQueue

from api.v1.utils.order import convert_db_order_to_schema


async def order_event_generator(
    request: Request, order_event_queue: OrderEventsQueue, process_event_queue: OrderProcessingEventQueue,
) -> AsyncGenerator[str, None]:
    while True:
        if await request.is_disconnected():
            break

        if order_event_queue.has_orders():
            recent_order = order_event_queue.pop_order()
            if (
                recent_order is None
            ):
                return
            schemas_order = await asyncio.to_thread(
                convert_db_order_to_schema, recent_order
            )
            yield f"event: newOrders\ndata: {schemas_order.model_dump_json()}\n\n"
        if process_event_queue.has_items(
            event_queue=OrderProcessingEventQueue.EventQueueKey.PROCESSING_STATUS_EVENT
        ):
            processing_status_data: Optional[Dict[str, str]] = (
                process_event_queue.pop_processing_status(
                    event_queue=OrderProcessingEventQueue.EventQueueKey.PROCESSING_STATUS_EVENT
                )
            )
            if processing_status_data is None:
                return
            yield f"event: updatedOrderProcessingStatus\ndata: {json.dumps(processing_status_data)}\n\n"
        if process_event_queue.has_items(
            event_queue=OrderProcessingEventQueue.EventQueueKey.HANDLING_PROCESS
        ):
            processing_status_data: Optional[Dict[str, str]] = (
                process_event_queue.pop_processing_status(
                    event_queue=OrderProcessingEventQueue.EventQueueKey.HANDLING_PROCESS
                )
            )
            if processing_status_data is None:
                return
            yield f"event: updatedOrderHandlingStatus\ndata: {json.dumps(processing_status_data)}\n\n"
        if process_event_queue.has_items(
            event_queue=OrderProcessingEventQueue.EventQueueKey.FULFILLMENT_STATUS
        ):
            processing_status_data: Optional[Dict[str, str]] = (
                process_event_queue.pop_processing_status(
                    event_queue=OrderProcessingEventQueue.EventQueueKey.FULFILLMENT_STATUS
                )
            )
            if processing_status_data is None:
                return
            yield f"event: updatedOrderFulfillmentStatus\ndata: {json.dumps(processing_status_data)}\n\n"

        await asyncio.sleep(0.5)
