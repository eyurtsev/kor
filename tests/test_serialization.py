"""Test serialization and deserialization of nodes."""
from typing import Any, Type

import pytest

from kor import Bool, Number, Object, Selection, Text
from kor._pydantic import PYDANTIC_MAJOR_VERSION
from kor.nodes import ExtractionSchemaNode


@pytest.fixture(params=ExtractionSchemaNode.__subclasses__())
def extraction_subclass(request: Any) -> Any:
    """Fixture to test all subclasses of ExtractionSchemaNode."""
    return request.param


@pytest.mark.skipif(
    PYDANTIC_MAJOR_VERSION != 1, reason="Only implemented for pydantic 1"
)
def test_extraction_schema_node_has_type_discriminator(
    extraction_subclass: Type[ExtractionSchemaNode],
) -> None:
    """Test if all subclasses of ExtractionSchemaNode have a type discriminator."""
    node_type = extraction_subclass(id="test")
    assert node_type.dict()["$type"] == extraction_subclass.__name__


@pytest.mark.skipif(
    PYDANTIC_MAJOR_VERSION != 1, reason="Only implemented for pydantic 1"
)
def test_serialize_deserialize_equals() -> None:
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

    stringified = expected.json()
    assert Object.parse_raw(stringified) == expected
    assert isinstance(stringified, str)
    assert expected.dict() == {
        "attributes": [
            {
                "description": "Number description",
                "examples": [],
                "id": "number",
                "many": False,
                "$type": "Number",
            },
            {
                "description": "text description",
                "examples": [],
                "id": "text",
                "many": False,
                "$type": "Text",
            },
            {
                "description": "bool description",
                "examples": [],
                "id": "bool",
                "many": False,
                "$type": "Bool",
            },
        ],
        "description": "root-object",
        "examples": [],
        "id": "root",
        "many": False,
    }

    assert Object.parse_raw(stringified) == expected


def test_simple_deserialization() -> None:
    json = """
    {
        "id": "sample_object",
        "description": "Deserialization Example",
        "many": true,
        "attributes": [
            {
                "$type": "Number",
                "id": "number_attribute",
                "description": "Description for Number",
                "many": true,
                "examples": [
                    ["Here is 1 number", 1],
                    ["Here are 0 numbers", 0]
                ]
            },
            {
                "$type": "Text",
                "id": "text_attribute",
                "description": "Description for Text",
                "many": true,
                "examples": [
                    ["Here is a text", "a text"],
                    ["Here is no text", "no text"]
                ]
            },
            {
                "$type": "Bool",
                "id": "bool_attribute",
                "description": "Description for Bool",
                "many": true,
                "examples": [
                    ["This is soo true", true],
                    ["This is wrong", false]
                ]
            },
            {
                "$type": "Selection",
                "id": "selection_attribute",
                "description": "Description for Selection",
                "many": true,
                "options": [
                    {
                        "id": "option1",
                        "description": "description for option 1"
                    },
                    {
                        "id": "option2",
                        "description": "description for option 2"
                    }
                ],
                "examples": [
                    ["This is soo true", true],
                    ["This is wrong", false]
                ]
            }
        ]
    }
    """
    if PYDANTIC_MAJOR_VERSION == 2:
        with pytest.raises(NotImplementedError):
            scheme = Object.parse_raw(json)
        return

    scheme = Object.parse_raw(json)
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
        "attributes": [
            {
                "id": "nested_object",
                "description": "Description nested object",
                "many": true,
                "attributes": [
                    {
                        "$type": "Number",
                        "id": "number_attribute",
                        "description": "Description for Number",
                        "many": true,
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
    if PYDANTIC_MAJOR_VERSION == 2:
        with pytest.raises(NotImplementedError):
            scheme = Object.parse_raw(json)
        return
    scheme = Object.parse_raw(json)

    assert scheme.id == "root_object"
    assert scheme.description == "Deserialization Example"
    assert scheme.many is True

    assert isinstance(scheme.attributes[0], Object)
    assert scheme.attributes[0].id == "nested_object"
    assert scheme.attributes[0].description == "Description nested object"
    assert scheme.attributes[0].many is True
    assert len(scheme.attributes[0].attributes) == 1


def test_extractionschemanode_without_type_cannot_be_deserialized() -> None:
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
                    ["Here is 1 number", 1],
                    ["Here are 0 numbers", 0]
                ]
            }
        ]
    }
    """
    if PYDANTIC_MAJOR_VERSION == 1:
        exception_class: Type[Exception] = ValueError
    else:
        exception_class = NotImplementedError

    with pytest.raises(exception_class):
        Object.parse_raw(json)
