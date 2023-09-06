import enum
from typing import List, Union, get_type_hints

import pydantic
import pytest
from pydantic.fields import Field

from kor.adapters import (
    _is_many,
    _translate_pydantic_to_kor,
    from_pydantic,
)
from kor.nodes import Bool, Number, Object, Option, Optional, Selection, Text


@pytest.mark.parametrize(
    "field,expected",
    [
        ("no_a", False),
        ("no_b", False),
        ("no_c", False),
        ("no_d", False),
        ("no_e", False),
        ("no_f", False),
        ("yes_a", True),
        ("yes_b", True),
        ("yes_c", True),
        ("yes_d", True),
    ],
)
def test_is_many(field: str, expected: bool) -> None:
    """Test if a type hint contains a Sequence argument."""

    class A:
        no_a: Optional[int]
        no_b: Union[None, str]
        no_c: Union[None, str, int]
        no_d: str
        no_e: float
        no_f: bool
        yes_a: Optional[List[str]]
        yes_b: List[Optional[str]]
        yes_c: List[str]
        yes_d: Union[None, str, List[int]]

    assert _is_many(get_type_hints(A)[field]) == expected


def test_convert_pydantic() -> None:
    """Convert a pydantic object to a dictionary."""

    class Child(pydantic.BaseModel):
        """Child pydantic object."""

        a: str

    class Toy(pydantic.BaseModel):
        """Toy pydantic object."""

        a: str = Field(description="hello")
        b: int = Field(examples=[("b is 1", 1)])
        c: float
        d: bool
        e: Optional[int] = None
        f: List[int] = []
        g: Optional[List[str]] = None
        h: List[Child] = Field(default=[], examples=[("h.a 1", {"a": "1"})])
        # Same as `g` but with Union format instead
        i: Union[None, List[str]] = None

    node = _translate_pydantic_to_kor(Toy)

    # Doing a few isinstance checks explicitly because pydantic does not do
    # the correct comparison based on the type itself!!
    assert isinstance(node.attributes[2], Number)
    assert not isinstance(node.attributes[2], Bool)
    assert not isinstance(node.attributes[3], Number)
    assert isinstance(node.attributes[3], Bool)

    assert node == Object(
        id="toy",
        attributes=[
            Text(id="a", description="hello"),
            Number(id="b", examples=[("b is 1", 1)]),
            Number(id="c", many=False),
            Bool(id="d"),
            # We don't have optional yet internally, so we don't check the
            # optional setting.
            Number(id="e"),  # We don't have a boolean type yet.
            Number(id="f", many=True),
            Text(id="g", many=True),
            Object(
                id="h",
                many=True,
                attributes=[Text(id="a")],
                examples=[("h.a 1", {"a": "1"})],
            ),
            Text(id="i", many=True),
        ],
    )


def test_convert_pydantic_with_enum() -> None:
    """Test conversion with an enum field."""

    class Choice(enum.Enum):
        """Choice field."""

        A = "a"
        B = "b"
        C = "c"

    class Toy(pydantic.BaseModel):
        """Toy pydantic object."""

        single_choice: Optional[Choice] = Field(examples=[("a", "a")])
        multiple_choices: List[Choice] = Field(examples=[("a b", ["a", "b"])])

    node = _translate_pydantic_to_kor(Toy)
    assert node == Object(
        id="toy",
        attributes=[
            Selection(
                id="single_choice",
                options=[
                    Option(id="a"),
                    Option(id="b"),
                    Option(id="c"),
                ],
                examples=[("a", "a")],
            ),
            Selection(
                id="multiple_choices",
                many=True,
                options=[
                    Option(id="a"),
                    Option(id="b"),
                    Option(id="c"),
                ],
                examples=[("a b", ["a", "b"])],
            ),
        ],
    )


def test_convert_pydantic_with_union() -> None:
    """Test behavior with Union field."""

    class Toy(pydantic.BaseModel):
        """Toy pydantic object."""

        a: Union[int, float, None]

    node = _translate_pydantic_to_kor(Toy)
    assert node == Object(
        id="toy",
        attributes=[
            Text(
                # Any union type of primitives is mapped to a text field for now.
                id="a"
            ),
        ],
    )


def test_convert_pydantic_with_complex_union() -> None:
    """Test behavior with Union field that has nested pydantic objects."""

    class Child(pydantic.BaseModel):
        """Child pydantic object."""

        y: str

    class ModelWithComplexUnion(pydantic.BaseModel):
        """Model that has a union with a pydantic object."""

        x: Union[Child, int]

    with pytest.raises(NotImplementedError):
        _translate_pydantic_to_kor(ModelWithComplexUnion)


def test_from_pydantic() -> None:
    """Test from pydantic function."""

    class Toy(pydantic.BaseModel):
        """Toy pydantic object."""

        a: str
        b: int

    node, validator = from_pydantic(Toy)
    assert validator.clean_data({"a": "hello", "b": 5}) == (Toy(a="hello", b=5), [])
    assert node == Object(
        id="toy",
        attributes=[Text(id="a"), Number(id="b")],
    )
