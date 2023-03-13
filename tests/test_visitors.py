import pytest

from kor.nodes import (
    AbstractVisitor,
    AbstractInput,
    Number,
    Text,
    Option,
    Selection,
    Object,
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
def test_visit_default_is_invoked(node: AbstractInput):
    visitor = TestVisitor()
    assert visitor.visit(node) == "uid"
