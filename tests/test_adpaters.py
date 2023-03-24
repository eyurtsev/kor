import pydantic
from pydantic.fields import Field

from kor.adapters import _translate_pydantic_to_kor, from_pydantic
from kor.nodes import List, Number, Object, Optional, Text


def test_convert_pydantic() -> None:
    """Convert a pydantic object to a dictionary."""

    class Child(pydantic.BaseModel):
        """Child pydantic object."""

        a: str

    class Toy(pydantic.BaseModel):
        """Toy pydantic object."""

        a: str = Field(description="hello")
        b: int = Field(examples=[("b is 1", "1")])
        c: float
        d: bool
        e: Optional[int] = None
        f: List[int] = []
        g: Optional[List[str]] = None
        h: List[Child] = Field(default=[], examples=[("h.a 1", {"a": "1"})])

    node = _translate_pydantic_to_kor(Toy)
    assert node == Object(
        id="toy",
        attributes=[
            Text(id="a", description="hello"),
            Number(id="b", examples=[("b is 1", "1")]),
            Number(id="c"),
            Text(id="d"),  # We do not support boolean types yet.
            # We don't have optional yet internally, so we don't check the optional setting.
            Number(id="e"),  # We don't have a boolean type yet.
            Number(id="f", many=True),
            Text(id="g", many=True),
            Object(
                id="h",
                many=True,
                attributes=[Text(id="a")],
                examples=[("h.a 1", {"a": "1"})],
            ),
        ],
    )


def test_from_pydantic() -> None:
    """Test from pydantic function."""

    class Toy(pydantic.BaseModel):
        """Toy pydantic object."""

        a: str
        b: int

    node, validator = from_pydantic(Toy)
    assert validator.clean_data({"a": "hello", "b": 5}) == Toy(a="hello", b=5)
    assert node == Object(
        id="toy",
        attributes=[Text(id="a"), Number(id="b")],
    )
