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

from ._pydantic import PYDANTIC_MAJOR_VERSION
from .nodes import Bool, ExtractionSchemaNode, Number, Object, Option, Selection, Text
from .validators import PydanticValidator, Validator

# Not going to support dicts or lists since that requires recursive checks.
# May make sense to either drop the internal representation, or properly extend it
# to handle Lists, Unions etc.
# Not worth the effort, until it's clear that folks are using this functionality.
PRIMITIVE_TYPES = {str, float, int, type(None)}


def _is_many(annotation: Any) -> bool:
    """Determine if the given annotation should map to field many.

    Map to field many if the annotation is a list or a Union where at least one
    of the arguments is a list type.

    Args:
        annotation: The annotation to check.

    Returns:
        bool
    """
    origin = get_origin(annotation)
    if origin is Union:
        for arg in get_args(annotation):
            arg_origin = get_origin(arg)
            if isinstance(arg_origin, type) and issubclass(arg_origin, List):
                return True
    if isinstance(origin, type) and issubclass(origin, List):
        return True
    return False


def _unpack_if_optional_equivalent(annotation: Any) -> Tuple[bool, Any]:
    """Determine if type is equivalent to an Optional and if so return the inner type.

    Args:
        annotation: The annotation to check.

    Returns:
        Tuple[bool, Any]; e.g., Optional[str] -> (True, str)
    """
    origin = get_origin(annotation)
    if origin is Union:
        args = get_args(annotation)
        if len(args) == 2 and type(None) in args:
            if args[0] is type(None):
                return True, args[1]
            else:
                return True, args[0]

    if origin is Optional:
        return True, get_args(annotation)[0]

    return False, None


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

    if PYDANTIC_MAJOR_VERSION == 1:
        fields_info = model_class.__fields__.items()  # type: ignore[attr-defined]
    else:
        fields_info = model_class.model_fields.items()  # type: ignore[attr-defined]

    for field_name, field in fields_info:
        if PYDANTIC_MAJOR_VERSION == 1:
            field_info = field.field_info
            extra = field_info.extra
            field_examples = extra.get(  # type: ignore[attr-defined]
                "examples", tuple()
            )
            field_description = getattr(field_info, "description") or ""
            type_ = field.outer_type_
        else:
            type_ = field.annotation
            field_examples = field.examples or tuple()  # type: ignore[attr-defined]
            field_description = getattr(field, "description") or ""

        field_many = _is_many(type_)

        attribute: Union[ExtractionSchemaNode, Selection, "Object"]

        is_optional_equivalent, unpacked_optional = _unpack_if_optional_equivalent(
            type_
        )

        if get_origin(type_) is Union and not is_optional_equivalent:
            # Verify that all arguments are primitive types
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
            # If the type is an Optional or Union equivalent, use the inner type
            type_to_use = unpacked_optional if is_optional_equivalent else type_

            # If the type is a parameterized generic, we want to extract
            # the inner type; e.g., List[str] -> str
            if not isinstance(type_to_use, type):  # i.e., parameterized generic
                origin_ = get_origin(type_to_use)
                if not isinstance(origin_, type) or not issubclass(origin_, List):
                    raise NotImplementedError(f"Unsupported type: {type_to_use}")
                type_to_use = get_args(type_to_use)[0]  # extract the argument

            if issubclass(type_to_use, BaseModel):
                attribute = _translate_pydantic_to_kor(
                    type_to_use,
                    description=field_description,
                    examples=field_examples,
                    many=field_many,
                    name=field_name,
                )
            # Precedence matters here since bool is a subclass of int
            elif issubclass(type_to_use, bool):
                attribute = Bool(
                    id=field_name,
                    examples=field_examples,
                    description=field_description,
                    many=field_many,
                )
            elif issubclass(type_to_use, (int, float)):
                attribute = Number(
                    id=field_name,
                    examples=field_examples,
                    description=field_description,
                    many=field_many,
                )
            elif issubclass(type_to_use, enum.Enum):
                enum_choices = list(type_to_use)
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
