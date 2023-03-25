"""Adapters to convert from validation frameworks to Kor internal representation."""
import enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
)

from pydantic import BaseModel

from .nodes import ExtractionSchemaNode, Number, Object, Option, Selection, Text
from .validators import PydanticValidator, Validator

# Not going to support dicts or lists since that requires recursive checks.
# May make sense to either drop the internal representation, or properly extend it
# to handle Lists, Unions etc.
# Not worth the effort, until it's clear that folks are using this functionality.
PRIMITIVE_TYPES = {str, float, int, type(None)}


def _translate_pydantic_to_kor(
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
        name: The name of the model.
        description: The description of the model.
        examples: A sequence of examples of the model.
        many: Whether the model is a list of models.

    Returns:
        The Kor internal representation of the model.
    """

    attributes: List[Union[ExtractionSchemaNode, Selection, "Object"]] = []
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
        attribute: Union[ExtractionSchemaNode, Selection, "Object"]
        # Precedence matters here since bool is a subclass of int
        if get_origin(type_) is Union:
            args = get_args(type_)

            if not all(arg in PRIMITIVE_TYPES for arg in args):
                raise NotImplementedError(
                    "Union of non-primitive types not supported. Issue with"
                    f"field: `{field_name}`. Has type: `{type_}`"
                )

            attribute = Text(
                id=field_name,
                examples=field_examples,
                description=field_description,
                many=field_many,
            )
        else:
            if issubclass(type_, BaseModel):
                attribute = _translate_pydantic_to_kor(
                    type_,
                    description=field_description,
                    examples=field_examples,
                    many=field_many,
                    name=field_name,
                )
            elif issubclass(type_, bool):
                attribute = Text(
                    id=field_name,
                    examples=field_examples,
                    description=field_description,
                    many=field_many,
                )
            elif issubclass(type_, (int, float)):
                attribute = Number(
                    id=field_name,
                    examples=field_examples,
                    description=field_description,
                    many=field_many,
                )
            elif issubclass(type_, enum.Enum):
                enum_choices = list(type_)
                attribute = Selection(
                    id=field_name,
                    description=field_description,
                    many=field_many,
                    examples=field_examples,
                    options=[Option(id=choice.value) for choice in enum_choices],
                )
            else:
                attribute = Text(
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


# PUBLIC API


def from_pydantic(
    model_class: Type[BaseModel],
    *,
    description: str = "",
    examples: Sequence[Tuple[str, Dict[str, Any]]] = tuple(),
    many: bool = False,
) -> Tuple[Object, Validator]:
    """Convert a pydantic model to Kor internal representation.

    Args:
        model_class: The pydantic model class to convert.
        description: The description of the model.
        examples: A sequence of examples to be used for the model.
        many: Whether to expect the model to be a list of models.

    Returns:
        A tuple of the Kor internal representation of the model and a validator.
    """
    schema = _translate_pydantic_to_kor(
        model_class,
        description=description,
        examples=examples,
        many=many,
    )
    validator = PydanticValidator(model_class, schema.many)
    return schema, validator
