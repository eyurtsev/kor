from pydantic import BaseModel
from typing import Type, Sequence, Tuple

from .nodes import Object, Text, Number


def convert_pydantic(
    model_class: Type[BaseModel], examples: Sequence[Tuple[str, str]] = tuple()
) -> Object:
    """Convert a pydantic model to a kor Object."""
    attributes = []
    for field_name, field in model_class.__fields__.items():
        type_ = field.type_
        if issubclass(type_, BaseModel):
            attr = convert_pydantic(type_)
        elif isinstance(type_, (int, float)):
            attr = Number(id=field.name)
        else:
            attr = Text(id=field.name)

        attributes.append(attr)

    return Object(
        id=model_class.__class__.__name__.lower(),
        attributes=attributes,
        examples=examples,
    )
