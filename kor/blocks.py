"""Extraction building blocks."""
import dataclasses
from kor.elements import ExtractionInput, ObjectInput, TextInput


@dataclasses.dataclass(frozen=True, kw_only=True)
class TimePeriod(ExtractionInput):
    """Built-in for more general time-periods; e.g., 'after dinner', 'next year'"""


@dataclasses.dataclass(frozen=True, kw_only=True)
class NumericRange(ExtractionInput):
    """Built-in numeric range input."""


ADDRESS_INPUT = ObjectInput(
    id="address",
    elements=[
        TextInput(id="street"),
        TextInput(id="city"),
        TextInput(id="state"),
        TextInput(id="zipcode"),
        TextInput(id="country"),
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

FIRST_NAME = TextInput(
    id="first_name",
    description="what is the person's first name",
    examples=[("Billy was here", "Billy"), ("Bob was very tall", "Bob")],
)

LAST_NAME = TextInput(
    id="last_name",
    description="what is the person's last name",
    examples=[("Joe Donatello was very tall", "Donatello")],
)
