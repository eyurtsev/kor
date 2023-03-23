"""Adapters to convert from validation frameworks to Kor internal representation."""
from pydantic import BaseModel
from typing import Type, Sequence, Tuple, Any, Dict, get_origin

from .nodes import Object, Text, Number


def _convert_pydantic_internal(
    model_class: Type[BaseModel],
    *,
    description: str = "",
    examples: Sequence[Tuple[str, Dict[str, Any]]] = tuple(),
    many: bool = False,
) -> Object:
    """Same as main API but many is now controllable."""
    attributes = []
    for field_name, field in model_class.__fields__.items():
        field_info = field.field_info
        extra = field_info.extra
        if "examples" in extra:
            field_examples = extra["examples"]
        else:
            field_examples = tuple()

        field_description = field_info.description or ""

        type_ = field.type_
        field_many = get_origin(field.outer_type_) is list
        if issubclass(type_, BaseModel):
            attr = _convert_pydantic_internal(
                type_,
                description=field_description,
                examples=field_examples,
                many=field_many,
            )
        elif isinstance(type_, (int, float)):
            attr = Number(
                id=field.name,
                examples=field_examples,
                description=field_description,
                many=field_many,
            )
        else:
            attr = Text(
                id=field.name,
                examples=field_examples,
                description=field_description,
                many=field_many,
            )

        attributes.append(attr)

    return Object(
        id=model_class.__name__.lower(),
        attributes=attributes,
        description=description,
        examples=examples,
        many=many,
    )


# PUBLIC API


def convert_pydantic(
    model_class: Type[BaseModel],
    *,
    description: str = "",
    examples: Sequence[Tuple[str, Dict[str, Any]]] = tuple(),
) -> Object:
    """Convert a pydantic model to Kor internal representation.

    Args:
        model_class: The pydantic model class to convert.
        description: The description of the model.
        examples: A sequence of examples of the model.
    """
    return _convert_pydantic_internal(
        model_class, description=description, examples=examples
    )
