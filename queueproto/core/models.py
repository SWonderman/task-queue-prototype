import uuid
import datetime
from typing import List, Optional, Dict, Iterable

from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.timezone import now, make_aware
from django.utils.translation import gettext_lazy as _

from core.marketplace import generate_order, generate_order_shipment
from core.definitions import (
    Order as OrderDefinition,
    Error,
    Result,
    ApiResponse,
)
from core.api import simulate_request


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Customer(BaseModel):
    first_name = models.TextField(max_length=125)
    last_name = models.TextField(max_length=125)
    address1 = models.TextField(max_length=150)
    address2 = models.TextField(max_length=150, null=True, blank=True)
    zip_code = models.TextField(max_length=50)
    country = models.TextField(max_length=125)

    order = models.OneToOneField(
        "Order", related_name="customer", on_delete=models.CASCADE
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class OrderItem(BaseModel):
    product_sku = models.CharField(max_length=25)
    product_title = models.CharField(max_length=125)
    product_media_url = models.URLField(blank=True, null=True)
    price = models.DecimalField(decimal_places=4, max_digits=19)
    quantity = models.PositiveSmallIntegerField()

    order = models.ForeignKey(
        "Order", related_name="order_items", on_delete=models.CASCADE
    )


class OrderShipment(BaseModel):
    shipment_id = models.TextField(max_length=50, unique=True)
    carrier_name = models.TextField(max_length=125)
    carrier_code = models.TextField(max_length=50)

    order = models.OneToOneField(
        "Order",
        related_name="shipment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    @classmethod
    def create_shipment_for_order(
        cls, order: "Order", event_queue
    ) -> Optional["OrderShipment"]:
        started_at = now()

        api_response: ApiResponse[OrderShipment] = simulate_request(
            data_callback=generate_order_shipment,
            allow_failure=True,
            failure_percentage=5,
        )

        error = None
        shipment = None
        if api_response.status_code != 200 and isinstance(api_response.response, Error):
            error = api_response.response
        else:
            shipment_data: OrderShipment = api_response.response
            shipment = cls.objects.create(
                shipment_id=shipment_data.shipment_id,
                carrier_name=shipment_data.carrier_name,
                carrier_code=shipment_data.carrier_code,
                order=order,
            )

        OrderHandlingProcess.update_processing(
            order=order,
            state=OrderHandlingProcess.State.GENERATING_SHIPMENT,
            started_at=started_at,
            event_queue=event_queue,
            event_name="updatedOrderHandlingStatus",
            error=error,
        )

        return shipment


class OrderHandlingProcess(BaseModel):
    class Status(models.TextChoices):
        SUCCEEDED = "SUCCEEDED", _("SUCCEEDED")
        FAILED = "FAILED", _("FAILED")

    class State(models.TextChoices):
        WAITING = "WAITING", _("WAITING")
        GENERATING_SHIPMENT = "GENERATING SHIPMENT", _("GENERATING SHIPMENT")
        SENDING_TRACKING = "SENDING TRACKING", _("SENDING TRACKING")
        MARKING_AS_SHIPPED = "MARKING AS SHIPPED", _("MARKING AS SHIPPED")
        HANDLED = "HANDLED", _("HANDLED")

    status = models.CharField(max_length=25, choices=Status.choices)
    state = models.CharField(max_length=25, choices=State.choices)
    message = models.CharField(max_length=255, null=True, blank=True)
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()

    order = models.ForeignKey(
        "Order",
        related_name="handling_processes",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    @classmethod
    def update_processing(
        cls,
        order: "Order",
        state: "OrderHandlingProcess.State",
        started_at: datetime.datetime,
        event_queue,
        event_name: str,
        error: Optional[Error] = None,
    ):
        order_handling_process_status = OrderHandlingProcess.Status.SUCCEEDED
        process_status = "SUCCESS"
        process_message = None

        if error:
            order_handling_process_status = OrderHandlingProcess.Status.FAILED
            process_status = "FAILED"
            process_message = error.message

        cls.objects.create(
            status=order_handling_process_status,
            state=state,
            message=process_message,
            started_at=started_at,
            finished_at=now(),
            order=order,
        )

        event_queue.enque_processing_status_event(
            data={
                "order_id": str(order.id),
                "state": state.value,
                "status": process_status,
                "event": event_name,
            },
        )


class Order(BaseModel):
    class State(models.TextChoices):
        SHIPPING = "SHIPPING", _("SHIPPING")
        SHIPPED = "SHIPPED", _("SHIPPED")
        CANCELED = "CANCELED", _("CANCELED")

    total_price = models.DecimalField(decimal_places=4, max_digits=19)
    total_quantity = models.PositiveSmallIntegerField()
    state = models.CharField(max_length=25, choices=State.choices)
    currency_iso_code = models.TextField(max_length=3)
    placed_at = models.DateTimeField()

    @classmethod
    def generate_and_add_fake_orders(cls, to_generate: int) -> Result[List["Order"]]:
        # do not play with me...
        if to_generate <= 0:
            to_generate = 1

        fake_orders: List[OrderDefinition] = [
            generate_order() for _ in range(to_generate)
        ]

        orders: List[Order] = []
        created_orders: List[Order] = []
        order_items: List[OrderItem] = []
        customers: List[Customer] = []
        order_handling_processes: List[OrderHandlingProcess] = []
        failed: List[Error] = []
        with transaction.atomic():
            for fake_order in fake_orders:
                try:
                    order = Order(
                        total_price=fake_order.total_price,
                        total_quantity=fake_order.total_quantity,
                        state=cls.State[fake_order.state],
                        currency_iso_code=fake_order.currency_iso_code,
                        placed_at=make_aware(fake_order.placed_at),
                    )
                    orders.append(order)

                    order_items.extend(
                        [
                            OrderItem(
                                product_sku=order_item.product_sku,
                                product_title=order_item.product_title,
                                product_media_url=order_item.product_media_url,
                                price=order_item.price,
                                quantity=order_item.quantity,
                                order=order,
                            )
                            for order_item in fake_order.order_items
                        ]
                    )

                    customers.append(
                        Customer(
                            first_name=fake_order.customer.first_name,
                            last_name=fake_order.customer.last_name,
                            address1=fake_order.customer.address1,
                            address2=fake_order.customer.address2,
                            zip_code=fake_order.customer.zip_code,
                            country=fake_order.customer.country,
                            order=order,
                        )
                    )

                    order_handling_processes.append(
                        OrderHandlingProcess(
                            status=OrderHandlingProcess.Status.SUCCEEDED,
                            state=OrderHandlingProcess.State.WAITING,
                            started_at=now(),
                            finished_at=now(),
                            order=order,
                        )
                    )

                except Exception as e:
                    failed.append(
                        Error(message=f"Could not create fake order. Error: {e}")
                    )
                    continue

        if orders:
            created_orders = cls.objects.bulk_create(orders)
            OrderItem.objects.bulk_create(order_items)
            Customer.objects.bulk_create(customers)
            OrderHandlingProcess.objects.bulk_create(order_handling_processes)

        return Result(
            errors=failed,
            result=created_orders,
        )

    @classmethod
    def send_back_tracking_number(cls, order: "Order", event_queue) -> bool:
        started_at = now()

        api_response: ApiResponse[None] = simulate_request(
            data_callback=generate_order_shipment, allow_failure=True
        )

        error = None
        if not order.shipment:
            error = Error(message=f"Order with ID '{order.id}' does not have shipment.")
        elif api_response.status_code != 200 and isinstance(
            api_response.response, Error
        ):
            error = api_response.response

        OrderHandlingProcess.update_processing(
            order=order,
            state=OrderHandlingProcess.State.SENDING_TRACKING,
            started_at=started_at,
            event_queue=event_queue,
            event_name="updatedOrderHandlingStatus",
            error=error,
        )

        return error == None

    @classmethod
    def mark_order_as_shipped(cls, order: "Order", event_queue) -> bool:
        started_at = now()

        api_response: ApiResponse[None] = simulate_request(
            data_callback=None, allow_failure=True
        )

        error = None
        if api_response.status_code != 200 and isinstance(api_response.response, Error):
            error = api_response.response

        OrderHandlingProcess.update_processing(
            order=order,
            state=OrderHandlingProcess.State.MARKING_AS_SHIPPED,
            started_at=started_at,
            event_queue=event_queue,
            event_name="updatedOrderHandlingStatus",
            error=error,
        )

        return error == None

    @classmethod
    def get_latest_handling_process_for_each_order(
        cls, orders: Iterable["Order"]
    ) -> Dict["Order", Optional[OrderHandlingProcess]]:
        handling_processes: QuerySet[OrderHandlingProcess] = (
            OrderHandlingProcess.objects.filter(order__in=orders)
        )
        order_latest_handling_processes = dict()
        for order in orders:
            order_latest_handling_processes[order] = (
                handling_processes.filter(order=order).order_by("created_at").last()
            )

        return order_latest_handling_processes
