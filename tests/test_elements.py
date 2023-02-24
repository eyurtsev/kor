import pytest

from kor import elements


class ToyInput(elements.AbstractInput):
    """Toy input for tests."""


@pytest.mark.parametrize("invalid_id", ["", "@@#", "1hello"])
def test_invalid_identifier_raises_error(invalid_id: str) -> None:
    with pytest.raises(ValueError):
        ToyInput(id=invalid_id, description="Toy")


def test_can_instantiate_with_valid_id() -> None:
    """Can instantiate an abstract input with a valid ID."""
    ToyInput(id="good_id", description="Toy")


def test_extraction_input_cannot_be_instantiated() -> None:
    """ExtractionInput is abstract and should not be instantiated."""
    elements.ExtractionInput(id="hell", description="description", examples=[])
