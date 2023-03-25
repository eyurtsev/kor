"""Test validator module."""
from pydantic import BaseModel, ValidationError
from pydantic import validator as pydantic_validator

from kor.validators import (
    PydanticValidator,
)


def test_pydantic_validator() -> None:
    """Test the PydanticValidator wrapper around pydantic."""

    class ToyModel(BaseModel):
        """Toy model for testing purposes."""

        name: str
        age: int

        @pydantic_validator("age")
        def age_must_be_positive(cls, v: int) -> int:
            """Add an age constraint"""
            if v < 0:
                raise ValueError("age must be positive")
            return v

    # Adding an unused
    validator = PydanticValidator(ToyModel, None)  # type: ignore
    assert validator.clean_data({"name": "Eugene", "age": 5}) == (
        ToyModel(name="Eugene", age=5),
        [],
    )

    clean_data, exceptions = validator.clean_data({"name": "Eugene", "age": -1})
    assert clean_data is None
    assert len(exceptions) == 1
    assert isinstance(exceptions[0], ValidationError)
