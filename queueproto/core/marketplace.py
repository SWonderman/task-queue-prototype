from typing import List, Dict
import string
import random

from faker import Faker

from core.definitions import OrderState, Order, OrderItem, Customer, OrderShipment

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
    countries = [
        "Denmark",
        "Sweden",
        "Germany",
        "Netherlands",
        "Finland",
        "Norway",
        "Poland",
    ]

    return Customer(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        address1=fake.street_address(),
        address2=fake.secondary_address(),
        zip_code=fake.zipcode(),
        country=countries[random.randint(0, len(countries) - 1)],
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


def generate_order_shipment() -> OrderShipment:
    carriers = [
        {"name": "DHL", "code": "dhl"},
        {"name": "PostNord", "code": "postnord"},
        {"name": "FedEx", "code": "fedex"},
        {"name": "Cargo Express", "code": "cargoex"},
    ]
    characters_set = string.ascii_letters + string.digits
    shipment_id = "SHIPMENT-".join(random.choice(characters_set) for i in range(6))

    carrier = carriers[random.randint(0, len(carriers) - 1)]

    return OrderShipment(
        shipment_id=shipment_id,
        carrier_name=carrier.get("name", ""),
        carrier_code=carrier.get("code", ""),
    )


def generate_order() -> Order:
    customer: Customer = generate_customer()
    order_items: List[OrderItem] = [generate_order_item() for _ in range(random.randint(1, 5))]

    currency_iso_codes = ["SEK", "PLN", "DKK", "EUR", "NOK"]

    return Order(
        total_price=sum([order_item.price for order_item in order_items]),
        total_quantity=sum([order_item.quantity for order_item in order_items]),
        state=OrderState.SHIPPING,
        currency_iso_code=currency_iso_codes[random.randint(0, len(currency_iso_codes) - 1)],
        order_items=order_items,
        customer=customer,
    )


def country_to_flag() -> Dict[str, str]:
    return {
        "austria": "flag-at.svg",
        "belgium": "flag-be.svg",
        "germany": "flag-de.svg",
        "denmark": "flag-dk.svg",
        "spain": "flag-es.svg",
        "finland": "flag-fi.svg",
        "france": "flag-fr.svg",
        "italy": "flag-it.svg",
        "netherlands": "flag-nl.svg",
        "norway": "flag-no.svg",
        "poland": "flag-pl.svg",
        "portugal": "flag-pl.svg",
        "sweden": "flag-se.svg",
    }
