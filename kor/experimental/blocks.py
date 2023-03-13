"""Extraction building blocks."""
from kor.nodes import Number, Object, Text

ADDRESS_INPUT = Object(
    id="address",
    attributes=[
        Text(id="street"),
        Text(id="city"),
        Text(id="state"),
        Text(id="zipcode"),
        Text(id="country", description="A country in the world; e.g., France."),
    ],
    examples=[
        (
            "100 Main St, Boston,MA, 23232, USA",
            {
                "street": "100 Marlo St",
                "city": "Boston",
                "state": "MA",
                "zipcode": "23232",
                "country": "USA",
            },
        )
    ],
)

FIRST_NAME = Text(
    id="first_name",
    description="The person's first name",
    examples=[("Billy was here", "Billy"), ("Bob was very tall", "Bob")],
)

BOILING_POINT = Text(id="boiling_point", description="Boiling Point of compound. ")

LAST_NAME = Text(
    id="last_name",
    description="The person's last name",
    examples=[("Joe Donatello was very tall", "Donatello")],
)

COMPANY_NAME = Text(
    id="company_name",
    description="The name of the company",
    examples=[
        ("Apple stock price was down today", "Apple"),
        ("I bought games from Microsoft", "Microsoft"),
    ],
)

PRODUCT_NAME = Text(
    id="product_name",
    description="The name of the product",
    examples=[
        ("Apple stock price was down today", "Apple"),
        ("I bought games from Microsoft", "Microsoft"),
    ],
)

PRICE = Object(
    id="price",
    description="The price of the item, including currency",
    attributes=[
        Number(id="amount", description="The amount in digit format."),
        Text(id="currency", description="The currency."),
    ],
    examples=[("The 20 apples cost $11.13", {"amount": "11.13", "currency": "$"})],
)
