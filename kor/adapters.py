"""Adapters to convert from validation frameworks to Kor internal representation."""
from pydantic import BaseModel
from typing import Type, Sequence, Tuple, Any, Dict, get_origin, Optional

from .nodes import Object, Text, Number
from .validators import Validator, PydanticValidator


# PUBLIC API


def translate_pydantic_to_kor(
    model_class: Type[BaseModel],
    *,
    name: Optional[str] = None,
    description: str = "",
    examples: Sequence[Tuple[str, Dict[str, Any]]] = tuple(),
    many: bool = False,
) -> Object:
    """Convert a pydantic model to Kor internal representation.

    Args:
        model_class: The pydantic model class to convert.
        description: The description of the model.
        examples: A sequence of examples of the model.
        many: Whether the model is a list of models.

    Returns:
        The Kor internal representation of the model.
    """

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
            attribute = translate_pydantic_to_kor(
                type_,
                description=field_description,
                examples=field_examples,
                many=field_many,
                name=field_name,
            )
        else:
            if isinstance(type_, (int, float)):
                node_class = Number
            else:
                node_class = Text

            attribute = node_class(
                id=field_name,
                examples=field_examples,
                description=field_description,
                many=field_many,
            )

        attributes.append(attribute)

    return Object(
        id=name or model_class.__name__.lower(),
        attributes=attributes,
        description=description,
        examples=examples,
        many=many,
    )


def foo(
    model_class: Type[BaseModel],
    *,
    description: str = "",
    examples: Sequence[Tuple[str, Dict[str, Any]]] = tuple(),
    many: bool = False,
) -> Tuple[Object, Validator]:
    """Convert a pydantic model to Kor internal representation."""
    validator = PydanticValidator(model_class, many)
    schema = translate_pydantic_to_kor(
        model_class,
        description=description,
        examples=examples,
        many=many,
    )
    return schema, validator
