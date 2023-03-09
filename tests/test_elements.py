import pytest

from kor import nodes


class ToyInput(elements.AbstractInput):
    """Toy input for tests."""


@pytest.mark.parametrize("invalid_id", ["", "@@#", " "])
def test_invalid_identifier_raises_error(invalid_id: str) -> None:
    with pytest.raises(ValueError):
        ToyInput(id=invalid_id, description="Toy")


@pytest.mark.parametrize("valid_id", ["name", "NAME", "name-name", "_name", "1name"])
def test_can_instantiate_with_valid_id(valid_id) -> None:
    """Can instantiate an abstract input with a valid ID."""
    ToyInput(id=valid_id, description="Toy")


def test_extraction_input_cannot_be_instantiated() -> None:
    """ExtractionInput is abstract and should not be instantiated."""
    elements.ExtractionInput(id="help", description="description", examples=[])
