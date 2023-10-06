import json
from typing import Optional

from ._pydantic import PYDANTIC_MAJOR_VERSION
from .nodes import Object

# PUBLIC API


def loads(string: str) -> Object:
    """Deserialize a string to a schema node."""
    if PYDANTIC_MAJOR_VERSION == 1:
        return Object.parse_raw(string)
    return Object.model_validate_json(string)


def dumps(
    object: Object, *, indent: Optional[int] = None, sort_keys: bool = False
) -> str:
    """Serialize a schema node to a string."""
    if PYDANTIC_MAJOR_VERSION == 1:
        d = object.dict()
    else:
        d = object.model_dump()

    return json.dumps(d, indent=indent, sort_keys=sort_keys)