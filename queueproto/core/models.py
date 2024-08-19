from typing import List
import uuid

from django.db import models, transaction
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from core.marketplace import generate_order
from core.definitions import Order as OrderDefinition, Error


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

    order = models.OneToOneField("Order", related_name="customer", on_delete=models.CASCADE)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class OrderItem(BaseModel):
    product_sku = models.TextField(max_length=25)
    product_title = models.TextField(max_length=125)
    product_media_url = models.URLField(blank=True, null=True)
    price = models.DecimalField(decimal_places=4, max_digits=19)
    quantity = models.PositiveSmallIntegerField()

    order = models.ForeignKey("Order", related_name="order_items", on_delete=models.CASCADE)


class Order(BaseModel):
    class State(models.TextChoices):
        SHIPPING = "SHIPPING", _("SHIPPING")
        SHIPPED = "SHIPPED", _("SHIPPED")
        CANCELED = "CANCELED", _("CANCELED")

    total_price = models.DecimalField(decimal_places=4, max_digits=19)
    total_quantity = models.PositiveSmallIntegerField()
    state = models.CharField(max_length=25, choices=State.choices)
    currency_iso_code = models.TextField(max_length=3)

    @classmethod
    def generate_and_add_fake_orders(cls, to_generate: int) -> List[Error]:
        # do not play with me...
        if to_generate <= 0:
            to_generate = 1

        fake_orders: List[OrderDefinition] = [generate_order() for _ in range(to_generate)]

        orders: List[Order] = []
        order_items: List[OrderItem] = []
        customers: List[Customer] = []
        failed: List[Error] = []
        with transaction.atomic():
            for fake_order in fake_orders:
                try:
                    order = Order(
                        total_price=fake_order.total_price,
                        total_quantity=fake_order.total_quantity,
                        state=cls.State[fake_order.state],
                        currency_iso_code=fake_order.currency_iso_code,
                    )
                    orders.append(order)

                    order_items.extend([
                        OrderItem(
                            product_sku=order_item.product_sku,
                            product_title=order_item.product_title,
                            product_media_url=order_item.product_media_url,
                            price=order_item.price,
                            quantity=order_item.quantity,
                            order=order,
                        )
                    for order_item in fake_order.order_items
                    ])

                    customer = customers.append(Customer(
                        first_name=fake_order.customer.first_name,
                        last_name=fake_order.customer.last_name,
                        address1=fake_order.customer.address1,
                        address2=fake_order.customer.address2,
                        zip_code=fake_order.customer.zip_code,
                        country=fake_order.customer.country,
                        order=order,
                    ))
                except Exception as e:
                    failed.append(Error(message=f"Could not create fake order. Error: {e}"))
                    continue

        if orders:
            cls.objects.bulk_create(orders)
            OrderItem.objects.bulk_create(order_items)
            Customer.objects.bulk_create(customers)

        return failed
