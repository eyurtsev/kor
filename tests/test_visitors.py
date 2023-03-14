import pytest

from kor.nodes import (
    AbstractInput,
    AbstractVisitor,
    Number,
    Object,
    Option,
    Selection,
    Text,
)


class TestVisitor(AbstractVisitor[str]):
    """Toy input for tests."""

    def visit_default(self, node: AbstractInput) -> str:
        """Verify default is invoked"""
        return node.id

    def visit(self, node: AbstractInput) -> str:
        """Convenience method."""
        return node.accept(self)


@pytest.mark.parametrize(
    "node",
    [
        Number(id="uid"),
        Text(id="uid"),
        Object(id="uid", attributes=[]),
        Selection(id="uid", options=[]),
        Option(id="uid"),
    ],
)
def test_visit_default_is_invoked(node: AbstractInput) -> None:
    visitor = TestVisitor()
    assert visitor.visit(node) == "uid"
