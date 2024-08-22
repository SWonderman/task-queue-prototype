import math
import asyncio
import json
from typing import List, Annotated, AsyncGenerator, Set, Optional, Dict

from fastapi import APIRouter, Path, Body, Request, Query
from fastapi.responses import StreamingResponse
from django.db.models import QuerySet
from django.forms.models import model_to_dict

from core.models import Order
from core.events import OrderEventsQueue, OrderProcessingStatusEventQueue
from core.tasks import handle_orders
from core.definitions import Result

from api.v1.schemas import order as order_schema, core as core_schema
from api.v1.utils import order as order_api_utils


router = APIRouter()

active_connections: Set[Request] = set()


@router.get("/orders", response_model=core_schema.ResponseWithPagination[order_schema.Order])
def get_orders(
   page: Annotated[int, Path(ge=1)] = 1,
   display: Annotated[int, Path(ge=1, le=50)] = 15,
):
    orders_count: int = Order.objects.count()

    all_pages_count = math.ceil(orders_count/display)
    if page > all_pages_count:
        page = all_pages_count

    # NOTE: adjust for 0-based indexing
    page -= 1

    lower_boundary = page * display
    upper_boundary = lower_boundary + display

    orders: QuerySet[Order] = Order.objects.all()[lower_boundary:upper_boundary]

    items = [
        order_api_utils.convert_db_order_to_schema(order=order) for order in orders
    ]

    return core_schema.ResponseWithPagination(
        current_page=page,
        items_count=orders_count,
        pages_count=all_pages_count,
        items=items,
    )


async def order_event_generator(request: Request, event_queue: OrderEventsQueue) -> AsyncGenerator[str, None]:
    while True:
        if await request.is_disconnected():
            break

        if event_queue.has_orders():
            recent_order = event_queue.pop_order()
            if recent_order is None: # NOTE: this should not happen after the initial has_orders check
                return
            schemas_order = await asyncio.to_thread(order_api_utils.convert_db_order_to_schema, recent_order)
            yield f"event: newOrders\ndata: {schemas_order.model_dump_json()}\n\n"
        await asyncio.sleep(0.5)


async def order_processing_status_event_generator(request: Request, event_queue: OrderProcessingStatusEventQueue) -> AsyncGenerator[str, None]:
    while True:
        if await request.is_disconnected():
            break

        if event_queue.has_items():
            processing_status_data: Optional[Dict[str, str]] = event_queue.pop_processing_status()
            if processing_status_data is None:
                return
            yield f"event: updatedOrderProcessingStatus\ndata: {json.dumps(processing_status_data)}\n\n"
        await asyncio.sleep(0.5)


@router.get("/orders/stream")
async def stream_orders(request: Request):
    active_connections.add(request)
    return StreamingResponse(order_event_generator(request=request, event_queue=OrderEventsQueue()), media_type="text/event-stream")


@router.get("/orders/processing/status/stream")
async def stream_orders_processing_status(request: Request):
    active_connections.add(request)
    return StreamingResponse(order_processing_status_event_generator(request=request, event_queue=OrderProcessingStatusEventQueue()), media_type="text/event-stream")


@router.post("/orders", response_model=core_schema.ErrorResponse)
def generate_orders(generate: Annotated[int, Query(ge=1)] = 5):
    result: Result[List[Order]] = Order.generate_and_add_fake_orders(to_generate=generate)

    if result.result and len(result.result) > 0:
        event_controller = OrderEventsQueue()
        event_controller.enque_orders(result.result)

    return core_schema.ErrorResponse(
        errors=[
            core_schema.Error(
                message=error.message,
            ) for error in result.errors
        ]
    )


@router.post("/orders/handle")
def add_orders_to_handling_queue(ids: Annotated[order_schema.OrderIds, Body]):
    handle_orders.delay(
        order_ids=ids.order_ids,
    )


@router.on_event("shutdown")
async def shutdown():
    for conn in active_connections:
        await conn.close()
    active_connections.clear()
