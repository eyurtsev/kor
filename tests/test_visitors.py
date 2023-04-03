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

    def visit_default(self, node: AbstractSchemaNode, *args: Any, **kwargs: Any) -> Any:
        """Verify default is invoked"""
        return node.id, args, kwargs

    def visit(self, node: AbstractSchemaNode, *args: Any, **kwargs: Any) -> Any:
        """Convenience method."""
        return node.accept(self, *args, **kwargs)


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
    assert visitor.visit(node, 1, 2, a="a", b="b") == (
        "uid",
        (1, 2),
        {"a": "a", "b": "b"},
    )
