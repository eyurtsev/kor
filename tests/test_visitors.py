from typing import Any, Tuple

import pytest

from kor.nodes import (
    AbstractValueNode,
    AbstractVisitor,
    Number,
    Object,
    Option,
    Selection,
    Text,
)


class TestVisitor(AbstractVisitor[Tuple[str, Any]]):
    """Toy input for tests."""

    def visit_default(self, node: AbstractValueNode, **kwargs: Any) -> Tuple[str, Any]:
        """Verify default is invoked"""
        return node.id, kwargs

    def visit(self, node: AbstractValueNode, **kwargs: Any) -> Tuple[str, Any]:
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
def test_visit_default_is_invoked(node: AbstractValueNode) -> None:
    visitor = TestVisitor()
    assert visitor.visit(node, a="a", b="b") == ("uid", {"a": "a", "b": "b"})
