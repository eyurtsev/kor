import pydantic

from kor.adapters import _translate_pydantic_to_kor, from_pydantic
from kor.nodes import Number, Object, Text, Optional, List


def test_convert_pydantic() -> None:
    """Convert a pydantic object to a dictionary."""

    class Toy(pydantic.BaseModel):
        """Toy pydantic object."""

        a: str
        b: int
        c: Optional[int] = None
        d: List[int] = []

    node = _translate_pydantic_to_kor(Toy)
    assert node == Object(
        id="toy",
        attributes=[
            Text(id="a"),
            Number(id="b"),
            Number(id="c"),
            Number(id="d", many=True),
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
