from typing import Dict

from core.models import Order, OrderHandlingProcess

from api.v1.schemas import order as order_schema


def convert_db_order_to_schema(order: Order) -> order_schema.Order:
    latest_order_handling = (
        OrderHandlingProcess.objects.filter(order=order).order_by("created_at").last()
    )
    latest_order_handling_schema = None
    if latest_order_handling:
        latest_order_handling_schema = order_schema.OrderHandlingProcess(
            id=str(latest_order_handling.id),
            created_at=str(latest_order_handling.created_at),
            updated_at=str(latest_order_handling.updated_at),
            status=str(latest_order_handling.status),
            state=str(latest_order_handling.state),
            started_at=str(latest_order_handling.started_at),
            finished_at=str(latest_order_handling.finished_at),
        )

    return order_schema.Order(
        id=str(order.id),
        created_at=str(order.created_at),
        updated_at=str(order.updated_at),
        total_price=float(order.total_price),
        total_quantity=int(order.total_quantity),
        state=str(order.state),
        currency_iso_code=str(order.currency_iso_code),
        placed_at=str(order.placed_at),
        order_items=[
            order_schema.OrderItem(
                id=str(order_item.id),
                created_at=str(order_item.created_at),
                updated_at=str(order_item.updated_at),
                product_sku=order_item.product_sku,
                product_title=order_item.product_title,
                product_media_url=order_item.product_media_url,
                price=float(order_item.price),
                quantity=int(order_item.quantity),
            )
            for order_item in order.order_items.all()
        ],
        customer=order_schema.Customer(
            id=str(order.customer.id),
            created_at=str(order.customer.created_at),
            updated_at=str(order.customer.updated_at),
            first_name=order.customer.first_name,
            last_name=order.customer.last_name,
            address1=order.customer.address1,
            address2=order.customer.address2,
            zip_code=order.customer.zip_code,
            country=order.customer.country,
        ),
        latest_handling_process=latest_order_handling_schema,
    )
