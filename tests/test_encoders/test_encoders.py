from typing import Any

import pytest

from kor.encoders import Encoder, JSONEncoder, XMLEncoder, encode_examples
from kor.nodes import AbstractValueNode, Number, Object, Option, Selection, Text


def _get_schema() -> AbstractValueNode:
    """Make an abstract input node."""
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
    return obj


@pytest.mark.parametrize(
    "node_data,expected",
    [
        ({"object": [{"number": ["1"]}]}, "<object><number>1</number></object>"),
        ({"object": [{"text": ["3"]}]}, "<object><text>3</text></object>"),
        (
            {"object": [{"selection": ["option"]}]},
            "<object><selection>option</selection></object>",
        ),
        ({}, ""),
        (
            {"object": [{"age": ["1", "2"]}]},
            "<object><age>1</age><age>2</age></object>",
        ),
    ],
)
def test_xml_encoding(node_data: Any, expected: str) -> None:
    """Test XML encoding."""
    xml_encoder = XMLEncoder()
    assert xml_encoder.encode(node_data) == expected


class NoOpEncoder(Encoder):
    def encode(self, data: Any) -> str:
        """Identity function for encoding."""
        return data

    def decode(self, text: str) -> Any:
        """Identity function for decoding."""
        return text

    def get_instruction_segment(self) -> str:
        return ""


def test_encode_examples() -> None:
    """Test that examples are encoded properly."""
    examples = [("input", "output"), ("input2", "output2")]

    assert encode_examples(examples, JSONEncoder(use_tags=True), None) == [
        ("input", '<json>"output"</json>'),
        ("input2", '<json>"output2"</json>'),
    ]

    assert encode_examples(examples, NoOpEncoder(), input_formatter=None) == [
        ("input", "output"),
        ("input2", "output2"),
    ]

    assert encode_examples(examples, NoOpEncoder(), input_formatter="text_prefix") == [
        ('Text: """\ninput\n"""', "output"),
        ('Text: """\ninput2\n"""', "output2"),
    ]

    assert encode_examples(
        examples, NoOpEncoder(), input_formatter="triple_quotes"
    ) == [
        ('"""\ninput\n"""', "output"),
        ('"""\ninput2\n"""', "output2"),
    ]
