from typing import List

import pytest

from kor.examples import _write_tag, generate_examples
from kor.nodes import Number, Object, Option, Selection, Text


def test_write_tag() -> None:
    """Verify XML encoding works as expected."""
    assert _write_tag("tag", "data") == "<tag>data</tag>"
    assert _write_tag("tag", ["data1", "data2"]) == "<tag>data1</tag><tag>data2</tag>"
    assert _write_tag("tag", {"key1": "value1"}) == "<tag><key1>value1</key1></tag>"
    assert (
        _write_tag("tag", {"key1": "value1", "key2": "value2"})
        == "<tag><key1>value1</key1><key2>value2</key2></tag>"
    )
    assert (
        _write_tag("tag", {"key1": "value1", "key2": ["a", "b"]})
        == "<tag><key1>value1</key1><key2>a</key2><key2>b</key2></tag>"
    )


def test_example_generation() -> None:
    """Light-weight test for example generator.

    Verifies that examples are getting picked up and encoded properly.
    """
    option = Option(id="option", description="Option", examples=["selection"])
    number = Number(id="number", description="Number", examples=[("number", "2")])
    text = Text(id="text", description="Text", examples=[("text", "3")])

    selection = Selection(
        id="selection",
        description="Selection",
        options=[option],
        null_examples=["foo"],
    )

    obj = Object(
        id="object",
        description="object",
        examples=[("another number", {"number": "1"})],
        attributes=[number, text, selection],
    )

    examples = generate_examples(obj)
    assert isinstance(examples, list)
    assert len(examples) == 5
    # Verify a few generated examples
    assert examples[0] == ("another number", "<object><number>1</number></object>")
    assert examples[1] == ("number", "<object><number>2</number></object>")
    assert examples[2] == ("text", "<object><text>3</text></object>")


@pytest.mark.parametrize(
    "encoding,expected",
    [
        (
            "plain",
            [
                ("another number", {"object": [{"number": ["1"]}]}),
                ("number", {"object": [{"number": ["2"]}]}),
                ("text", {"object": [{"text": ["3"]}]}),
                ("selection", {"object": [{"selection": ["option"]}]}),
                ("foo", {}),
                ("1 2", {"object": [{"age": ["1", "2"]}]}),
            ],
        ),
        (
            "JSON",
            [
                ("another number", '{"object": [{"number": ["1"]}]}'),
                ("number", '{"object": [{"number": ["2"]}]}'),
                ("text", '{"object": [{"text": ["3"]}]}'),
                ("selection", '{"object": [{"selection": ["option"]}]}'),
                ("foo", "{}"),
                ("1 2", '{"object": [{"age": ["1", "2"]}]}'),
            ],
        ),
    ],
)
def test_example_generation_with_plain_encoding(
    encoding: str, expected: List[dict]
) -> None:
    """Light test for plain encoding.

    Verifies that examples are getting picked up and encoded properly.
    """
    option = Option(id="option", description="Option", examples=["selection"])
    number = Number(id="number", description="Number", examples=[("number", "2")])
    age = Number(id="age", description="Age", examples=[("1 2", ["1", "2"])])
    text = Text(id="text", description="Text", examples=[("text", "3")])

    selection = Selection(
        id="selection",
        description="Selection",
        options=[option],
        null_examples=["foo"],
    )

    obj = Object(
        id="object",
        description="object",
        examples=[("another number", {"number": ["1"]})],
        attributes=[number, text, selection, age],
    )

    examples = generate_examples(obj, encoding=encoding)
    assert isinstance(examples, list)
    # Verify a few generated examples
    assert examples == expected
