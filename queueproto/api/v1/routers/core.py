import math
from typing import List, Annotated, Set

from fastapi import APIRouter, HTTPException, Path, Body, Request, Query
from fastapi.responses import StreamingResponse
from django.db.models import QuerySet

from core.models import Order, OrderHandlingProcess
from core.events import OrderEventsQueue, OrderProcessingEventQueue
from core.tasks import handle_orders
from core.definitions import Result

from api.v1.schemas import order as order_schema, core as core_schema
from api.v1.utils import order as order_api_utils
from api.v1.generators.order import order_event_generator


router = APIRouter()

active_connections: Set[Request] = set()


@router.get(
    "/orders", response_model=core_schema.ResponseWithPagination[order_schema.Order]
)
def get_orders(
    page: Annotated[int, Path(ge=1)] = 1,
    display: Annotated[int, Path(ge=1, le=50)] = 15,
):
    orders_count: int = Order.objects.count()

    all_pages_count = math.ceil(orders_count / display)
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


@router.get("/orders/stream")
async def stream_orders(request: Request):
    active_connections.add(request)
    return StreamingResponse(
        order_event_generator(
            request=request,
            order_event_queue=OrderEventsQueue(),
            process_event_queue=OrderProcessingEventQueue(),
        ),
        media_type="text/event-stream",
    )


@router.post("/orders", response_model=core_schema.ErrorResponse)
def generate_orders(generate: Annotated[int, Query(ge=1)] = 5):
    result: Result[List[Order]] = Order.generate_and_add_fake_orders(
        to_generate=generate
    )

    if result.result and len(result.result) > 0:
        event_controller = OrderEventsQueue()
        event_controller.enque_orders(result.result)

    return core_schema.ErrorResponse(
        errors=[
            core_schema.Error(
                message=error.message,
            )
            for error in result.errors
        ]
    )


@router.post("/orders/handle")
def add_orders_to_handling_queue(ids: Annotated[order_schema.OrderIds, Body]):
    handle_orders.delay(
        order_ids=ids.order_ids,
    )


@router.get(
    "/orders/{id}/fulfillment/history",
    response_model=List[order_schema.OrderHandlingProcess],
)
def get_order_fulfillment_history(id: Annotated[str, Path(title="Order ID")]):
    try:
        order = Order.objects.get(id=id)
        handling_processes: QuerySet[OrderHandlingProcess] = (
            order.handling_processes.all()
        )
    except Order.OrderDoesNotExist:
        raise HTTPException(status_code=404, detail="Order was not found")

    return [
        order_schema.OrderHandlingProcess(
            id=str(process.id),
            created_at=str(process.created_at),
            updated_at=str(process.updated_at),
            status=str(process.status),
            state=str(process.state),
            message=process.message,
            started_at=str(process.started_at),
            finished_at=str(process.finished_at),
        )
        for process in handling_processes
    ]


@router.on_event("shutdown")
async def shutdown():
    for conn in active_connections:
        await conn.close()
    active_connections.clear()
