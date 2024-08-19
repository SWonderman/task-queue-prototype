from typing import List
import string
import random

from faker import Faker

from core.definitions import OrderState, Order, OrderItem, Customer

fake = Faker()

PRODUCT_ADJECTIVES = [
    "Innovative",
    "Durable",
    "Elegant",
    "Versatile",
    "Compact",
    "Sleek",
    "Robust",
    "Efficient",
    "Premium",
    "User-friendly",
    "Lightweight",
    "Stylish",
    "Affordable",
    "Reliable",
    "Cutting-edge",
]

PRODUCT_MATERIALS = [
    "Stainless steel",
    "Carbon fiber",
    "Aluminum",
    "Bamboo",
    "Leather",
    "Ceramic",
    "Glass",
    "Titanium",
    "Plastic",
    "Wood",
    "Silicone",
    "Copper",
    "Polycarbonate",
    "Wool",
    "Rubber",
]

PRODUCT_NAMES = [
    "Backpack",
    "Wallet",
    "Laptop Stand",
    "Travel Mug",
    "Headphones",
    "Notebook",
    "Desk Organizer",
    "Watch",
    "Phone Charger",
    "Desk Lamp",
    "Yoga Mat",
    "Sunglasses",
    "Water Bottle",
    "Keychain",
    "Suitcase",
]


def generate_customer() -> Customer:
    return Customer(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        address1=fake.street_address(),
        address2=fake.secondary_address(),
        zip_code=fake.zipcode(),
        country=fake.country(),
    )


def generate_order_item() -> OrderItem:
    characters_set = string.ascii_letters + string.digits

    product_title = f"{PRODUCT_ADJECTIVES[random.randint(0, len(PRODUCT_ADJECTIVES) -1)]} {PRODUCT_MATERIALS[random.randint(0, len(PRODUCT_MATERIALS) -1)]} {PRODUCT_NAMES[random.randint(0, len(PRODUCT_NAMES)-1)]}"

    return OrderItem(
        product_sku="".join(random.choice(characters_set) for i in range(6)),
        product_title=product_title,
        product_media_url=None,
        price=round(random.uniform(3.5, 10.0), 1),
        quantity=random.randint(1, 3),
    )

def generate_order() -> Order:
    customer: Customer = generate_customer()
    order_items: List[OrderItem] = [generate_order_item() for _ in range(random.randint(1, 5))]

    states = [state for state in OrderState]
    currency_iso_codes = ["SEK", "PLN", "DKK", "EUR", "NOK"]

    return Order(
        total_price=sum([order_item.price for order_item in order_items]),
        total_quantity=sum([order_item.quantity for order_item in order_items]),
        state=states[random.randint(0, len(states) - 1)],
        currency_iso_code=currency_iso_codes[random.randint(0, len(currency_iso_codes) - 1)],
        order_items=order_items,
        customer=customer,
    )
