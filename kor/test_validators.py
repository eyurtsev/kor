"""Test validator module."""
import pytest
from pydantic import BaseModel, ValidationError
from pydantic import validator as pydantic_validator

from kor.validators import (
    PydanticValidator,
)


def test_pydantic_validator():
    """Test the PydanticValidator wrapper around pydantic."""

    class ToyModel(BaseModel):
        name: str
        age: int

        @pydantic_validator("age")
        def age_must_be_positive(cls, v: int) -> int:
            """Add an age constraint"""
            if v < 0:
                raise ValueError("age must be positive")
            return v

    validator = PydanticValidator(ToyModel)
    assert validator.clean_data({"name": "Eugene", "age": 5}) == ToyModel(
        name="Eugene", age=5
    )

    with pytest.raises(ValidationError):
        validator.clean_data({"name": "Eugene", "age": -1})
