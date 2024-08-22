from django.core.management.base import BaseCommand, CommandError

from core.models import Order


class Command(BaseCommand):
    help = "Delete all orders from the database"

    def handle(self, *args, **options):
        try:
            orders_count = Order.objects.count()
            Order.objects.all().delete()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error while deleting orders: {e}."))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"{orders_count} orders deleted.")
            )
