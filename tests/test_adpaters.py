from kor.adapters import translate_pydantic_to_kor
from kor.nodes import Number, Object, Text

import pydantic


def test_convert_pydantic() -> None:
    """Convert a pydantic object to a dictionary."""

    class Toy(pydantic.BaseModel):
        """Toy pydantic object."""

        a: str
        b: int

    assert translate_pydantic_to_kor(Toy) == Object(
        id="toy",
        attributes=[Text(id="a"), Number(id="b")],
    )
