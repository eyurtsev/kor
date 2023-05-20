import pytest

from kor import Number, Object, Text
from kor.nodes import Option, Selection
from kor.type_descriptors import (
    BulletPointDescriptor,
    PostgresDescriptor,
    TypeScriptDescriptor,
)

OPTION_1 = Option(id="blue", description="Option Description", examples=["blue"])
OPTION_2 = Option(id="red", description="Red color", examples=["red"])

NUMBER = Number(
    id="number", description="Number Description", examples=[("number", "2")]
)

TEXT = Text(id="text", description="Text Description", examples=[("text", "3")])

TEXT_ARRAY = Text(
    id="text_array",
    description="Text Array Description",
    examples=[("list of text", ["1", "2", "3"])],
    many=True,
)

SELECTION = Selection(
    id="selection",
    description="Selection Description",
    options=[OPTION_1],
    null_examples=["foo"],
)

SELECTION_2 = Selection(
    id="selection2",
    description="Selection2 Description",
    options=[OPTION_1, OPTION_2],
    null_examples=["foo"],
    many=True,
)

OBJ = Object(
    id="object",
    description="Object Description",
    examples=[("another number", {"number": "1"})],
    attributes=[NUMBER, TEXT, SELECTION, SELECTION_2],
)

OBJ1 = Object(
    id="object",
    description="Object Description",
    examples=[("few numbers", {"numbers": ["1", "2", "3"]})],
    attributes=[NUMBER, TEXT_ARRAY, SELECTION, SELECTION_2],
)


def test_no_obvious_crashes() -> None:
    """Lightweight test to verify that we can generate type descriptions for nodes.

    This test doesn't verify correctness, only that code doesn't crash!
    """

    nodes_to_check = [OBJ]
    descriptors = [TypeScriptDescriptor(), BulletPointDescriptor()]

    for node in nodes_to_check:
        # Verify that we can generate description
        for descriptor in descriptors:
            assert isinstance(descriptor.describe(node), str)


@pytest.mark.parametrize(
    "node,description",
    [
        (
            OBJ,
            (
                "* object: Object # Object Description\n"
                "*  number: Number # Number Description\n"
                "*  text: Text # Text Description\n"
                "*  selection: Selection # Selection Description\n"
                "*  selection2: Selection # Selection2 Description"
            ),
        ),
    ],
)
def test_bullet_point_descriptions(node: Object, description: str) -> None:
    """Verify bullet point descriptions."""
    assert BulletPointDescriptor().describe(node) == description


@pytest.mark.parametrize(
    "node,description",
    [
        (
            OBJ,
            (
                "```TypeScript\n"
                "\n"
                "object: { // Object Description\n"
                " number: number // Number Description\n"
                " text: string // Text Description\n"
                ' selection: "blue" // Selection Description\n'
                ' selection2: Array<"blue" | "red"> // Selection2 Description\n'
                "}\n"
                "```\n"
            ),
        ),
    ],
)
def test_typescript_description(node: Object, description: str) -> None:
    """Verify typescript descriptions."""
    assert TypeScriptDescriptor().describe(node) == description


@pytest.mark.parametrize(
    "node,description",
    [
        (
            OBJ1,
            (
                "```Postgres\n"
                "\n"
                "object: { // Object Description\n"
                " number: NUMERIC // Number Description\n"
                " text_array: TEXT ARRAY[] // Text Array Description\n"
                ' selection: "blue" // Selection Description\n'
                ' selection2: ENUM("blue" , "red") // Selection2 Description\n'
                "}\n"
                "```\n"
            ),
        ),
    ],
)
def test_postgres_description(node: Object, description: str) -> None:
    """Verify postgres descriptions."""
    assert PostgresDescriptor().describe(node) == description
