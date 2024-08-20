from django.shortcuts import render
from django.db.models import QuerySet

from core.models import Order

def index(request):
    orders: QuerySet[Order] = Order.objects.all()

    context = {
        "orders": orders,
    }

    return render(request=request, template_name="core/index.html", context=context)
