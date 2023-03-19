from typing import Any

import pytest

from kor.encoders import JSONEncoder, XMLEncoder
from kor.nodes import AbstractSchemaNode, Number, Object, Option, Selection, Text


def _get_schema() -> AbstractSchemaNode:
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
    node = _get_schema()
    xml_encoder = XMLEncoder(node)  # None
    assert xml_encoder.encode(node_data) == expected


@pytest.mark.parametrize(
    "node_data,expected",
    [
        ({"object": [{"number": ["1"]}]}, '{"object": [{"number": ["1"]}]}'),
        ({"object": [{"text": ["3"]}]}, '{"object": [{"text": ["3"]}]}'),
        (
            {"object": [{"selection": ["option"]}]},
            '{"object": [{"selection": ["option"]}]}',
        ),
    ],
)
def test_json_encoding(node_data: Any, expected: str) -> None:
    """Test JSON encoding. This is just json.dumps, so no need to test extensively."""
    node = _get_schema()
    xml_encoder = JSONEncoder(node)  # None
    assert xml_encoder.encode(node_data) == expected
