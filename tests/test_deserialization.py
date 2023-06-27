import pytest

from kor import Bool, Number, Object, Selection, Text


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

    with pytest.raises(ValueError):
        Object.parse_raw(json)
