from kor.examples import generate_examples
from kor.nodes import Number, Object, Option, Selection, Text


def test_example_generation() -> None:
    """Light-weight test for example generator.

    Verifies that examples are getting picked up and encoded properly.
    """
    option = Option(id="option", description="Option", examples=["selection"])
    number = Number(
        id="number", description="Number", examples=[("number", 2)], many=True
    )
    text = Text(id="text", description="Text", examples=[("text", "3")], many=True)

    selection = Selection(
        id="selection",
        description="Selection",
        options=[option],
        null_examples=["foo"],
        many=True,
    )

    obj = Object(
        id="object",
        description="object",
        examples=[("another number", {"number": 1})],
        attributes=[number, text, selection],
        many=True,
    )

    examples = generate_examples(obj)
    assert examples == [
        ("another number", {"object": [{"number": 1}]}),
        ("number", {"object": [{"number": [2]}]}),
        ("text", {"object": [{"text": ["3"]}]}),
        ("selection", {"object": [{"selection": ["option"]}]}),
        ("foo", {}),
    ]


def test_example_generation_with_plain_encoding() -> None:
    """Light test for plain encoding."""
    option = Option(id="option", description="Option", examples=["selection"])
    number = Number(
        id="number",
        description="Number",
        examples=[("number", 2)],
        many=True,
    )
    age = Number(
        id="age",
        description="Age",
        examples=[("1 2", [1, 2])],
        many=True,
    )
    text = Text(
        id="text",
        description="Text",
        examples=[("text", "3")],
        many=True,
    )

    selection = Selection(
        id="selection",
        description="Selection",
        options=[option],
        null_examples=["foo"],
        many=True,
    )

    obj = Object(
        id="object",
        description="object",
        examples=[("another number", {"number": [1]})],
        attributes=[number, text, selection, age],
        many=True,
    )

    examples = generate_examples(obj)
    assert isinstance(examples, list)
    # Verify a few generated examples
    assert examples == [
        ("another number", {"object": [{"number": [1]}]}),
        ("number", {"object": [{"number": [2]}]}),
        ("text", {"object": [{"text": ["3"]}]}),
        ("selection", {"object": [{"selection": ["option"]}]}),
        ("foo", {}),
        ("1 2", {"object": [{"age": [1, 2]}]}),
    ]
