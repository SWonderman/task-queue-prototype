import uuid

from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


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

    order = models.ForeignKey("Order", related_name="product", on_delete=models.CASCADE)


class Order(BaseModel):
    class State(models.TextChoices):
        SHIPPING = "SHIPPING", _("SHIPPING")
        SHIPPED = "SHIPPED", _("SHIPPED")
        CANCELED = "CANCELED", _("CANCELED")

    total_price = models.DecimalField(decimal_places=4, max_digits=19)
    total_quantity = models.PositiveSmallIntegerField()
    state = models.CharField(max_length=25, choices=State.choices)
    currency_iso_code = models.TextField(max_length=3)
