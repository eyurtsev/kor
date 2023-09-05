from typing import Any

import pytest

from kor import nodes
from kor.nodes import AbstractVisitor


class FakeSchemaNode(nodes.AbstractSchemaNode):
    """Fake Schema Node for testing purposes."""

    def accept(self, visitor: AbstractVisitor, **kwargs: Any) -> Any:
        """Visitor acceptor."""
        raise NotImplementedError()


def test_extraction_input_cannot_be_instantiated() -> None:
    """ExtractionInput is abstract and should not be instantiated."""
    with pytest.raises(TypeError):
        nodes.ExtractionSchemaNode(  # type: ignore[abstract]
            id="help",
            description="description",
            examples=[],
        )


def test_object_examples() -> None:
    """Object examples.

    Verifying that examples do not get re-interpreted in a strange way. The reason
    for these tests is that we're using pydantic and pydantic does auto-coercion, which
    has caused issues in the past with incorrect auto-coercion.
    """
    # No examples
    assert (
        nodes.Object(
            id="obj",
            description="description",
            attributes=[],
            examples=[],
        ).examples
        == []
    )

    # One example with single extraction
    assert nodes.Object(
        id="obj",
        description="description",
        attributes=[],
        examples=[("input", {"key1": "value1"})],
    ).examples == [("input", {"key1": "value1"})]

    # One example with multiple extractions
    assert nodes.Object(
        id="obj",
        description="description",
        attributes=[],
        examples=[("input", [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}])],
        many=True,
    ).examples == [("input", [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}])]

    # One example with multiple extractions
    assert nodes.Object(
        id="obj",
        description="description",
        attributes=[],
        examples=[
            ("input", [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]),
            ("input2", {}),
        ],
        many=True,
    ).examples == [
        ("input", [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]),
        ("input2", {}),
    ]


def test_text_examples() -> None:
    """Text examples.

    Verify that examples do not get re-interpreted in a strange way.
    """
    assert nodes.Text(
        id="text",
        description="description",
        examples=[("input", "output")],
    ).examples == [("input", "output")]

    assert nodes.Text(
        id="text",
        description="description",
        examples=[("input", "")],
    ).examples == [("input", "")]

    assert (
        nodes.Text(
            id="text",
            description="description",
            examples=[],
        ).examples
        == []
    )
