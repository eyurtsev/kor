"""Definitions of input elements."""
from __future__ import annotations

import abc
import copy
from typing import (
    Any,
    Generic,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)

from pydantic import BaseModel

T = TypeVar("T")


# Visitor is defined here for now, to avoid circular imports.
class AbstractVisitor(Generic[T], abc.ABC):
    """An abstract visitor."""

    def visit_text(self, node: Text, **kwargs: Any) -> T:
        """Visit text node."""
        return self.visit_default(node, **kwargs)

    def visit_number(self, node: Number, **kwargs: Any) -> T:
        """Visit text node."""
        return self.visit_default(node, **kwargs)

    def visit_object(self, node: Object, **kwargs: Any) -> T:
        """Visit object node."""
        return self.visit_default(node, **kwargs)

    def visit_selection(self, node: Selection, **kwargs: Any) -> T:
        """Visit selection node."""
        return self.visit_default(node, **kwargs)

    def visit_option(self, node: Option, **kwargs: Any) -> T:
        """Visit option node."""
        return self.visit_default(node, **kwargs)

    def visit_default(self, node: AbstractSchemaNode, **kwargs: Any) -> T:
        """Default node implementation."""
        raise NotImplementedError()

    def visit_bool(self, node: Bool, **kwargs: Any) -> T:
        """Visit bool node."""
        return self.visit_default(node, **kwargs)


class AbstractSchemaNode(BaseModel):
    """Abstract schema node.

    Each node is expected to have a unique ID, and should
    only use alphanumeric characters.

    The ID should be unique across all inputs that belong
    to a given form.

    The description should describe what the node represents.
    It is used during prompt generation.
    """

    id: str
    description: str = ""
    many: bool = False

    @abc.abstractmethod
    def accept(self, visitor: AbstractVisitor[T], **kwargs: Any) -> T:
        """Accept a visitor."""
        raise NotImplementedError()

    # Update return type to `Self` when bumping python version.
    def replace(
        self,
        id: Optional[str] = None,  # pylint: disable=redefined-builtin
        description: Optional[str] = None,
    ) -> "AbstractSchemaNode":
        """Wrapper around data-classes replace."""
        new_object = copy.copy(self)
        if id:
            new_object.id = id
        if description:
            new_object.description = description
        return new_object


class ExtractionSchemaNode(AbstractSchemaNode, abc.ABC):
    """An abstract definition for inputs that involve extraction.

    An extraction input can be associated with extraction examples.

    An extraction example is a 2-tuple composed of a text segment and the expected
    extraction.

    For example:

    .. code-block:: python

        [
            ("I bought this cookie for $10", "$10"),
            ("Eggs cost twelve dollars", "twelve dollars"),
        ]
    """

    examples: Sequence[
        Tuple[str, Union[bool, int, float, str, Sequence[Union[str, int, float, bool]]]]
    ] = tuple()


class Number(ExtractionSchemaNode):
    """Built-in number input."""

    examples: Sequence[
        Tuple[str, Union[int, float, Sequence[Union[float, int]]]]
    ] = tuple()

    type: Literal["number"] = "number"

    def accept(self, visitor: AbstractVisitor[T], **kwargs: Any) -> T:
        """Accept a visitor."""
        return visitor.visit_number(self, **kwargs)


class Text(ExtractionSchemaNode):
    """Built-in text input."""

    examples: Sequence[Tuple[str, Union[Sequence[str], str]]] = tuple()
    type: Literal["text"] = "text"

    def accept(self, visitor: AbstractVisitor[T], **kwargs: Any) -> T:
        """Accept a visitor."""
        return visitor.visit_text(self, **kwargs)


class Bool(ExtractionSchemaNode):
    """Built-in bool input."""

    examples: Sequence[Tuple[str, Union[Sequence[bool], bool]]] = tuple()
    type: Literal["bool"] = "bool"

    def accept(self, visitor: AbstractVisitor[T], **kwargs: Any) -> T:
        """Accept a visitor."""
        return visitor.visit_bool(self, **kwargs)


class Option(AbstractSchemaNode):
    """Built-in option input must be part of a selection input."""

    examples: Sequence[str] = tuple()
    type: Literal["option"] = "option"

    def accept(self, visitor: AbstractVisitor[T], **kwargs: Any) -> T:
        """Accept a visitor."""
        return visitor.visit_option(self, **kwargs)


class Selection(AbstractSchemaNode):
    """Built-in selection node (aka Enum).

    A selection input is composed of one or more options.

    A selectio node supports both examples and null_examples.

    Null examples are segments of text for which nothing should be extracted.

    Examples:

    .. code-block:: python

        selection = Selection(
            id="species",
            description="What is your favorite animal species?",
            options=[
                Option(id="dog", description="Dog"),
                Option(id="cat", description="Cat"),
                Option(id="bird", description="Bird"),
            ],
            examples=[
                ("I like dogs", "dog"),
                ("I like cats", "cat"),
                ("I like birds", "bird"),
            ],
            null_examples=[
                "I like flowers",
            ],
            many=False
        )
    """

    options: Sequence[Option]
    examples: Sequence[Tuple[str, Union[str, Sequence[str]]]] = tuple()
    null_examples: Sequence[str] = tuple()
    type: Literal["selection"] = "selection"

    def accept(self, visitor: AbstractVisitor[T], **kwargs: Any) -> T:
        """Accept a visitor."""
        return visitor.visit_selection(self, **kwargs)


class Object(AbstractSchemaNode):
    """Built-in representation for an object.

    Use an object node to represent an entire object that should be extracted.

    An extraction input can be associated with 2 different types of examples:

    Example:

    .. code-block:: python

        object = Object(
            id="cookie",
            description="Information about a cookie including price and name.",
            attributes=[
                Text(id="name", description="The name of the cookie"),
                Number(id="price", description="The price of the cookie"),
            ],
            examples=[
                ("I bought this Big Cookie for $10",
                    {"name": "Big Cookie", "price": "$10"}),
                ("Eggs cost twelve dollars", {}), # Not a cookie
            ],
        )

    """

    attributes: Sequence[Union[Selection, Object, Number, Text, Bool]]
    type: Literal["object"] = "object"

    examples: Sequence[
        Tuple[
            str,
            Union[
                Sequence[Mapping[str, Any]],
                Mapping[str, Any],
            ],
        ]
    ] = tuple()

    def accept(self, visitor: AbstractVisitor[T], **kwargs: Any) -> T:
        """Accept a visitor."""
        return visitor.visit_object(self, **kwargs)
