from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import QuerySet

from core.models import Order

def index(request):
    orders: QuerySet[Order] = Order.objects.all()
    paginator = Paginator(orders, 15)

    page_number = request.GET.get("page")
    page_orders = paginator.get_page(page_number)

    context = {
        "orders": page_orders,
    }

    return render(request=request, template_name="core/index.html", context=context)
