from typing import Any

import pytest

from kor.nodes import (
    AbstractSchemaNode,
    AbstractVisitor,
    Number,
    Object,
    Option,
    Selection,
    Text,
)


class TestVisitor(AbstractVisitor[Any]):
    """Toy input for tests."""

    def visit_default(self, node: AbstractSchemaNode, **kwargs: Any) -> Any:
        """Verify default is invoked"""
        return node.id, kwargs

    def visit(self, node: AbstractSchemaNode, **kwargs: Any) -> Any:
        """Convenience method."""
        return node.accept(self, **kwargs)


OPTION = Option(id="uid")


@pytest.mark.parametrize(
    "node",
    [
        Number(id="uid"),
        Text(id="uid"),
        Object(id="uid", attributes=[]),
        Selection(id="uid", options=[OPTION]),
        Option(id="uid"),
    ],
)
def test_visit_default_is_invoked(node: AbstractSchemaNode) -> None:
    visitor = TestVisitor()
    assert visitor.visit(node, a="a", b="b") == (
        "uid",
        {"a": "a", "b": "b"},
    )
