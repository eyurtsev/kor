"""Test serialization and deserialization of nodes."""

import pytest
from pydantic import ValidationError

from kor import Bool, Number, Object, Selection, Text
from kor.serializer import dumps, loads


def test_serialize_deserialize_equals() -> None:
    """Test if serialization and deserialization are inverse operations."""
    expected = Object(
        id="root",
        description="root-object",
        attributes=[
            Number(id="number", description="Number description", examples=[]),
            Text(id="text", description="text description", examples=[]),
            Bool(id="bool", description="bool description", examples=[]),
        ],
        examples=[],
    )
    stringified = dumps(expected)
    assert isinstance(stringified, str)
    loaded_obj = loads(stringified)
    assert loaded_obj == expected
    assert loaded_obj.schema() == expected.schema()


def test_simple_deserialization() -> None:
    json = """
    {
        "id": "sample_object",
        "description": "Deserialization Example",
        "many": true,
        "type": "object",
        "attributes": [
            {
                "id": "number_attribute",
                "description": "Description for Number",
                "many": true,
                "type": "number",
                "examples": [
                    ["Here is 1 number", 1],
                    ["Here are 0 numbers", 0]
                ]
            },
            {
                "id": "text_attribute",
                "description": "Description for Text",
                "many": true,
                "type": "text",
                "examples": [
                    ["Here is a text", "a text"],
                    ["Here is no text", "no text"]
                ]
            },
            {
                "id": "bool_attribute",
                "description": "Description for Bool",
                "many": true,
                "type": "bool",
                "examples": [
                    ["This is soo true", true],
                    ["This is wrong", false]
                ]
            },
            {
                "id": "selection_attribute",
                "description": "Description for Selection",
                "many": true,
                "type": "selection",
                "options": [
                    {
                        "id": "option1",
                        "description": "description for option 1",
                        "type": "option"
                    },
                    {
                        "id": "option2",
                        "description": "description for option 2",
                        "type": "option"
                    }
                ],
                "examples": [
                    ["This is soo true", "true"],
                    ["This is wrong", "false"]
                ]
            }
        ]
    }
    """
    scheme = loads(json)

    assert scheme.id == "sample_object"
    assert scheme.description == "Deserialization Example"
    assert scheme.many is True

    assert isinstance(scheme.attributes[0], Number)
    assert scheme.attributes[0].id == "number_attribute"
    assert scheme.attributes[0].description == "Description for Number"
    assert scheme.attributes[0].many is True
    assert len(scheme.attributes[0].examples) == 2

    assert isinstance(scheme.attributes[1], Text)
    assert scheme.attributes[1].id == "text_attribute"
    assert scheme.attributes[1].description == "Description for Text"
    assert scheme.attributes[1].many is True
    assert len(scheme.attributes[1].examples) == 2

    assert isinstance(scheme.attributes[2], Bool)
    assert scheme.attributes[2].id == "bool_attribute"
    assert scheme.attributes[2].description == "Description for Bool"
    assert scheme.attributes[2].many is True
    assert len(scheme.attributes[2].examples) == 2

    assert isinstance(scheme.attributes[3], Selection)
    assert scheme.attributes[3].id == "selection_attribute"
    assert scheme.attributes[3].description == "Description for Selection"
    assert scheme.attributes[3].many is True
    assert len(scheme.attributes[3].options) == 2
    assert len(scheme.attributes[3].examples) == 2


def test_nested_object_deserialization() -> None:
    json = """
    {
        "id": "root_object",
        "description": "Deserialization Example",
        "many": true,
        "type": "object",
        "attributes": [
            {
                "id": "nested_object",
                "description": "Description nested object",
                "many": true,
                "type": "object",
                "attributes": [
                    {
                        "id": "number_attribute",
                        "description": "Description for Number",
                        "many": true,
                        "type": "number",
                        "examples": [
                            ["Here is 1 number", 1],
                            ["Here are 0 numbers", 0]
                        ]
                    }
                ]
            }
        ]
    }
    """
    scheme = loads(json)

    assert scheme.id == "root_object"
    assert scheme.description == "Deserialization Example"
    assert scheme.many is True

    assert isinstance(scheme.attributes[0], Object)
    assert scheme.attributes[0].id == "nested_object"
    assert scheme.attributes[0].description == "Description nested object"
    assert scheme.attributes[0].many is True
    assert len(scheme.attributes[0].attributes) == 1


def test_inconsistent_attribute_cannot_be_deserialized() -> None:
    """Test if inconsistent attributes cannot be deserialized."""

    # Here the examples are a mix of string and float, which should not be allowed
    json = """
    {
        "id": "root_object",
        "description": "Deserialization Example",
        "many": true,
        "attributes": [
            {
                "id": "number_attribute",
                "description": "Description for Number",
                "many": true,
                "examples": [
                    ["Here is 1 number", "true"],
                    ["Here are 0 numbers", 2.3]
                ]
            }
        ]
    }
    """
    with pytest.raises(ValidationError):
        loads(json)
