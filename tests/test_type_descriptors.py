import pytest

from kor import Object, Number, Text
from kor.nodes import Selection, Option, AbstractInput

from kor.type_descriptors import (
    generate_typescript_description,
    generate_bullet_point_description,
)


OPTION = Option(id="option", description="Option Description", examples=["selection"])
NUMBER = Number(
    id="number", description="Number Description", examples=[("number", "2")]
)
TEXT = Text(id="text", description="Text Description", examples=[("text", "3")])

SELECTION = Selection(
    id="selection",
    description="Selection Description",
    options=[OPTION],
    null_examples=["foo"],
)

OBJ = Object(
    id="object",
    description="Object Description",
    examples=[("another number", {"number": "1"})],
    attributes=[NUMBER, TEXT, SELECTION],
)


def test_no_obvious_crashes() -> None:
    """Lightweight test to verify that we can generate type descriptions for nodes.

    This test doesn't verify correctness, only that code doesn't crash!
    """

    nodes_to_check = [NUMBER, TEXT, SELECTION, OBJ]
    descriptors = [generate_typescript_description, generate_bullet_point_description]

    for node in nodes_to_check:
        # Verify that we can generate description
        for descriptor in descriptors:
            assert isinstance(descriptor(node), str)


@pytest.mark.parametrize(
    "node,description",
    [
        (
            NUMBER,
            "* number: Number # Number Description",
        ),
        (
            TEXT,
            "* text: Text # Text Description",
        ),
        (SELECTION, "* selection: Selection # Selection Description"),
        (
            OBJ,
            "* object: Object # Object Description\n"
            "*  number: Number # Number Description\n"
            "*  text: Text # Text Description\n"
            "*  selection: Selection # Selection Description",
        ),
    ],
)
def test_bullet_point_descriptions(node: AbstractInput, description: str) -> None:
    """Verify bullet point descriptions."""
    assert generate_bullet_point_description(node) == description


@pytest.mark.parametrize(
    "node,description",
    [
        (
            NUMBER,
            "```TypeScript\n\n{\n number: number[] // Number Description\n}\n```\n",
        ),
        (TEXT, "```TypeScript\n\n{\n text: string[] // Text Description\n}\n```\n"),
        (
            SELECTION,
            (
                "```TypeScript\n"
                "\n"
                "{\n"
                ' selection: ("option")[] // Selection Description\n'
                "}\n"
                "```\n"
            ),
        ),
        (
            OBJ,
            (
                "```TypeScript\n"
                "\n"
                "object: { // Object Description\n"
                " number: number[] // Number Description\n"
                " text: string[] // Text Description\n"
                ' selection: ("option")[] // Selection Description\n'
                "}\n"
                "```\n"
            ),
        ),
    ],
)
def test_typescript_description(node: AbstractInput, description: str) -> None:
    """Verify typescript descriptions."""
    assert generate_typescript_description(node) == description
