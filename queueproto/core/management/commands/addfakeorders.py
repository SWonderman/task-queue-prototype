from django.core.management.base import BaseCommand, CommandError

from core.models import Order


class Command(BaseCommand):
    help = "Generates and adds fake orders"

    def add_arguments(self, parser):
        parser.add_argument("to_generate", type=int)

    def handle(self, *args, **options):
        to_generate: int = options["to_generate"]
        if to_generate <= 0:
            self.stdout.write(
                self.style.ERROR(
                    f"To generate has to be a positive integer number. Got: {to_generate}."
                )
            )
            return

        failed = Order.generate_and_add_fake_orders(to_generate=to_generate)

        if failed:
            self.stdout.write(
                self.style.WARNING(
                    f"It was not possible to generate and add all orders. Errors: {len(failed)}."
                )
            )
            [self.stdout.write(self.style.ERROR(error.message)) for error in failed]
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"{to_generate} orders were generated and added successfully."
                )
            )
