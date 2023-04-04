"""Definitions of input elements."""
import abc
import copy
import re
from typing import (
    Any,
    Generic,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)

from pydantic import BaseModel, validator

# For now, limit what's allowed for identifiers.
# The main constraints
# 1) Relying on HTML parser to parse output
# 2) One of the type descriptors is TypeScript, so we want
#    to produce valid TypeScript identifiers.
# We can lift the constraints later if it becomes important,
# not worth the effort for a v0.
VALID_IDENTIFIER_PATTERN = re.compile(r"^[a-z_][0-9a-z_]*$")

T = TypeVar("T")


# Visitor is defined here for now, to avoid circular imports.
class AbstractVisitor(Generic[T], abc.ABC):
    """An abstract visitor."""

    def visit_text(self, node: "Text", **kwargs: Any) -> T:
        """Visit text node."""
        return self.visit_default(node, **kwargs)

    def visit_number(self, node: "Number", **kwargs: Any) -> T:
        """Visit text node."""
        return self.visit_default(node, **kwargs)

    def visit_object(self, node: "Object", **kwargs: Any) -> T:
        """Visit object node."""
        return self.visit_default(node, **kwargs)

    def visit_selection(self, node: "Selection", **kwargs: Any) -> T:
        """Visit selection node."""
        return self.visit_default(node, **kwargs)

    def visit_option(self, node: "Option", **kwargs: Any) -> T:
        """Visit option node."""
        return self.visit_default(node, **kwargs)

    def visit_default(self, node: "AbstractSchemaNode", **kwargs: Any) -> T:
        """Default node implementation."""
        raise NotImplementedError()


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

    @validator("id")
    def ensure_valid_uid(cls, uid: str) -> str:
        """Validate that using a valid identifier."""
        if not VALID_IDENTIFIER_PATTERN.match(uid):
            raise ValueError(
                f"`{id}` is not a valid identifier. "
                f"Please only use lower cased a-z, _ or the digits 0-9"
            )
        return uid

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

    examples: Sequence[Tuple[str, Union[str, Sequence[str]]]] = tuple()


class Number(ExtractionSchemaNode):
    """Built-in number input."""

    def accept(self, visitor: AbstractVisitor[T], **kwargs: Any) -> T:
        """Accept a visitor."""
        return visitor.visit_number(self, **kwargs)


class Text(ExtractionSchemaNode):
    """Built-in text input."""

    def accept(self, visitor: AbstractVisitor[T], **kwargs: Any) -> T:
        """Accept a visitor."""
        return visitor.visit_text(self, **kwargs)


class Option(AbstractSchemaNode):
    """Built-in option input must be part of a selection input."""

    examples: Sequence[str] = tuple()

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

    attributes: Sequence[Union[ExtractionSchemaNode, Selection, "Object"]]

    examples: Sequence[
        Tuple[
            str,
            Union[
                Mapping[str, Any],
                Sequence[Mapping[str, Any]],
            ],
        ]
    ] = tuple()

    def accept(self, visitor: AbstractVisitor[T], **kwargs: Any) -> T:
        """Accept a visitor."""
        return visitor.visit_object(self, **kwargs)
