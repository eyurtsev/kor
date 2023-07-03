from typing import Any

import pytest

from kor import Bool, Number, Object, Text
from kor.nodes import ExtractionSchemaNode


@pytest.fixture(params=ExtractionSchemaNode.__subclasses__())
def extraction_subclass(request: Any) -> Any:
    return request.param


def test_extractionschemanode_has_type_discriminator(
    extraction_subclass: Any,
) -> None:
    sut = extraction_subclass(id="test")
    assert sut.dict()["$type"] == extraction_subclass.__name__


def test_serialize_deserialize_equals() -> None:
    expected = Object(
        id="root",
        description="root-object",
        attributes=[
            Number(id="number", description="Number description", examples=[]),
            Text(id="text", description="text description", examples=[]),
            Bool(id="bool", description="bool description", examples=[]),
        ],
        examples=[],
    )

    json = expected.json()
    sut = Object.parse_raw(json)

    assert sut == expected
