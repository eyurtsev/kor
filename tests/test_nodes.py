from typing import Any

import pytest

from kor import nodes
from kor.nodes import AbstractVisitor


class ToyInput(nodes.AbstractInput):
    """Toy input for tests."""

    def accept(self, visitor: AbstractVisitor) -> Any:
        raise NotImplementedError()


@pytest.mark.parametrize("invalid_id", ["", "@@#", " ", "NAME", "1name", "name-name"])
def test_invalid_identifier_raises_error(invalid_id: str) -> None:
    with pytest.raises(ValueError):
        ToyInput(id=invalid_id, description="Toy")


@pytest.mark.parametrize("valid_id", ["name", "name_name", "_name", "n1ame"])
def test_can_instantiate_with_valid_id(valid_id: str) -> None:
    """Can instantiate an abstract input with a valid ID."""
    ToyInput(id=valid_id, description="Toy")


def test_extraction_input_cannot_be_instantiated() -> None:
    """ExtractionInput is abstract and should not be instantiated."""
    with pytest.raises(TypeError):
        nodes.ExtractionInput(id="help", description="description", examples=[])  # type: ignore[abstract]


def test_multiple_option_force_enabled() -> None:
    """Verifying that multiple option is force enabled for now."""
    with pytest.raises(ValueError):
        ToyInput(id="name", description="Toy", multiple=False)
