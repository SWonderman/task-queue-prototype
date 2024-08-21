from django.shortcuts import render
from django.core.paginator import Paginator, Page
from django.db.models import QuerySet

from core.models import Order, OrderHandlingProcess

def index(request):
    orders: QuerySet[Order] = Order.objects.all().order_by("-placed_at")
    paginator = Paginator(orders, 15)

    page_number = request.GET.get("page")
    page_orders: Page = paginator.get_page(page_number)

    if page_number is None:
        page_number = 1

    order_ids_to_their_handling_processes = Order.get_associated_handling_processes(orders=orders)

    context = {
        "orders": page_orders,
        "handling_processes": order_ids_to_their_handling_processes,
        "orders_count": orders.count(),
        "current_page": page_number,
        "pages_count": paginator.num_pages,
    }

    return render(request=request, template_name="core/index.html", context=context)
