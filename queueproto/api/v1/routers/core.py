import math
from typing import List, Annotated

from fastapi import APIRouter, Path, Body
from django.db.models import QuerySet
from django.forms.models import model_to_dict

from core.models import Order
from core.tasks import handle_orders

from api.v1.schemas import order as order_schema
from api.v1.schemas import core as core_schema

router = APIRouter()


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

    # ugly... unpacking does not want to collaborate today
    items = [
        order_schema.Order(
            id=order.id,
            created_at=order.created_at,
            updated_at=order.updated_at,
            total_price=order.total_price,
            total_quantity=order.total_quantity,
            state=order.state,
            currency_iso_code=order.currency_iso_code,
            order_items=[
                order_schema.OrderItem(
                    id=order_item.id,
                    created_at=order_item.created_at,
                    updated_at=order_item.updated_at,
                    product_sku=order_item.product_sku,
                    product_title=order_item.product_title,
                    product_media_url=order_item.product_media_url,
                    price=order_item.price,
                    quantity=order_item.quantity,
                ) for order_item in order.order_items.all()
            ],
            customer=order_schema.Customer(
                id=order.customer.id,
                created_at=order.customer.created_at,
                updated_at=order.customer.updated_at,
                first_name=order.customer.first_name,
                last_name=order.customer.last_name,
                address1=order.customer.address1,
                address2=order.customer.address2,
                zip_code=order.customer.zip_code,
                country=order.customer.country,
            )
        ) for order in orders
    ]

    return core_schema.ResponseWithPagination(
        current_page=page,
        items_count=orders_count,
        pages_count=all_pages_count,
        items=items,
    )


@router.post("/orders", response_model=core_schema.ErrorResponse)
def generate_orders(generate: Annotated[int, Path(ge=1)] = 5):
    failed = Order.generate_and_add_fake_orders(to_generate=generate)

    return core_schema.ErrorResponse(
        errors=[
            core_schema.Error(
                message=error.message,
            ) for error in failed
        ]
    )


@router.post("/orders/handle")
def add_orders_to_handling_queue(ids: Annotated[order_schema.OrderIds, Body]):
    handle_orders.delay(order_ids=ids.order_ids)
