from django.contrib import admin

from core.models import Customer, OrderItem, OrderShipment, OrderHandlingProcess, Order

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderShipment)
admin.site.register(OrderHandlingProcess)
admin.site.register(Customer)
