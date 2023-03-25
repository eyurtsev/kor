"""Definitions of input elements."""
import abc
import copy
import inspect
import operator
import re
from typing import (
    Any,
    Generic,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)

# For now, limit what's allowed for identifiers.
# The main constraints
# 1) Relying on HTML parser to parse output
# 2) One of the type descriptors is TypeScript, so we want
#    to produce valid TypeScript identifiers.
# We can lift the constraints later if it becomes important,
# not worth the effort for a v0.
VALID_IDENTIFIER_PATTERN = re.compile(r"^[a-z_][0-9a-z_]*$")

T = TypeVar("T")


def _get_all_slots(node: "AbstractSchemaNode") -> List[str]:
    """Get a list of all slots."""
    slots: List[str] = []
    for class_ in inspect.getmro(type(node)):
        if hasattr(class_, "__slots__"):
            slots.extend(class_.__slots__)
    return sorted(slots)


class AbstractVisitor(Generic[T], abc.ABC):
    """An abstract visitor. Define here to avoid cyclical imports for now."""

    def visit_text(self, node: "Text") -> T:
        """Visit text node."""
        return self.visit_default(node)

    def visit_number(self, node: "Number") -> T:
        """Visit text node."""
        return self.visit_default(node)

    def visit_object(self, node: "Object") -> T:
        """Visit object node."""
        return self.visit_default(node)

    def visit_selection(self, node: "Selection") -> T:
        """Visit selection node."""
        return self.visit_default(node)

    def visit_option(self, node: "Option") -> T:
        """Visit option node."""
        return self.visit_default(node)

    def visit_default(self, node: "AbstractSchemaNode") -> T:
        """Default node implementation."""
        raise NotImplementedError()


class AbstractSchemaNode(abc.ABC):
    """Abstract schema node.

    Each node is expected to have a unique ID, and should
    only use alphanumeric characters.

    The ID should be unique across all inputs that belong
    to a given form.

    The description should describe what the node represents.
    It is used during prompt generation.
    """

    __slots__ = "id", "description", "many"

    def __init__(self, *, id: str, description: str = "", many: bool = False) -> None:
        self.id = id
        self.description = description
        self.many = many

        if not VALID_IDENTIFIER_PATTERN.match(self.id):
            raise ValueError(
                f"`{self.id}` is not a valid identifier. "
                "Please only use lower cased a-z, _ or the digits 0-9"
            )

    @abc.abstractmethod
    def accept(self, visitor: AbstractVisitor) -> Any:
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

    def __repr__(self) -> str:
        """Get representation of the node."""
        return f"{type(self).__name__}({self.id})"

    def __eq__(self: Any, other: Any) -> bool:
        """Equality check"""
        if not isinstance(self, AbstractSchemaNode):
            raise AssertionError(f"Cannot compare {type(self)} with {type(other)}")
        if type(self) != type(other):
            return False

        if _get_all_slots(self) == _get_all_slots(other):
            attr_getters = [operator.attrgetter(attr) for attr in self.__slots__]
            return all(getter(self) == getter(other) for getter in attr_getters)

        return False


class ExtractionSchemaNode(AbstractSchemaNode, abc.ABC):
    """An abstract definition for inputs that involve extraction.

    An extraction input can be associated with extraction examples.

    An extraction example is a 2-tuple composed of a text segment and the expected
    extraction.

    For example:
        [
            ("I bought this cookie for $10", "$10"),
            ("Eggs cost twelve dollars", "twelve dollars"),
        ]
    """

    __slots__ = ("examples",)

    def __init__(
        self,
        *,
        id: str,
        description: str = "",
        many: bool = False,
        examples: Sequence[Tuple[str, Union[str, Sequence[str]]]] = tuple(),
    ) -> None:
        """Initialize for extraction input."""
        super().__init__(id=id, description=description, many=many)
        self.examples = examples


class Number(ExtractionSchemaNode):
    """Built-in number input."""

    def accept(self, visitor: AbstractVisitor[T]) -> T:
        """Accept a visitor."""
        return visitor.visit_number(self)


class Text(ExtractionSchemaNode):
    """Built-in text input."""

    def accept(self, visitor: AbstractVisitor[T]) -> T:
        """Accept a visitor."""
        return visitor.visit_text(self)


class Option(AbstractSchemaNode):
    """Built-in option input must be part of a selection input."""

    __slots__ = ("examples",)

    def __init__(
        self,
        *,
        id: str,
        description: str = "",
        many: bool = False,
        examples: Sequence[str] = tuple(),
    ) -> None:
        """Initialize for extraction input."""
        if many:
            # TODO: Fix the type hierarchy so that `many` isn't provided to option.
            raise ValueError("Option inputs cannot be many.")

        super().__init__(id=id, description=description, many=many)
        self.examples = examples

    def accept(self, visitor: AbstractVisitor[T]) -> T:
        """Accept a visitor."""
        return visitor.visit_option(self)


class Selection(AbstractSchemaNode):
    """Built-in selection input.

    A selection input is composed of one or more options.

    ## Null examples

    Null examples are segments of text for which nothing should be extracted.
    Good null examples will likely be challenging, adversarial examples.

    For example:
        for an extraction input about company names nothing should be extracted
        from the text: "I eat an apple every day.".
    """

    __slots__ = "options", "examples", "null_examples"

    def __init__(
        self,
        *,
        id: str,
        description: str = "",
        many: bool = False,
        options: Sequence[Option],
        examples: Sequence[Tuple[str, Union[str, Sequence[str]]]] = tuple(),
        null_examples: Sequence[str] = tuple(),
    ) -> None:
        """Initialize for extraction input."""
        super().__init__(id=id, description=description, many=many)

        if not options:
            raise ValueError("Selection inputs must have at least one option.")
        self.options = options
        self.examples = examples
        self.null_examples = null_examples

    def accept(self, visitor: AbstractVisitor[T]) -> T:
        """Accept a visitor."""
        return visitor.visit_selection(self)


class Object(AbstractSchemaNode):
    """A definition for an object extraction.

    An extraction input can be associated with 2 different types of examples:

    1) extraction examples (called simply `examples`)
    2) null examples (called `null_examples`)

    ## Extraction examples

    A standard extraction example is a 2-tuple composed of a text segment
    and the expected extraction.

    For example:
        [
            ("I bought this cookie for $10", "$10"),
            ("Eggs cost twelve dollars", "twelve dollars"),
        ]

    ## Null examples

    Null examples are segments of text for which nothing should be extracted.
    Good null examples will likely be challenging, adversarial examples.

    For example:
        for an extraction input about company names nothing should be extracted
        from the text: "I eat an apple every day.".
    """

    __slots__ = ("attributes", "examples")

    def __init__(
        self,
        *,
        id: str,
        description: str = "",
        many: bool = False,
        # All attributes but Option are OK.
        # May could clean up the type system to simplify this.
        attributes: Sequence[Union[ExtractionSchemaNode, Selection, "Object"]],
        examples: Sequence[
            Tuple[str, Mapping[str, Union[str, Sequence[str]]]]
        ] = tuple(),
    ) -> None:
        """Initialize for extraction input."""
        super().__init__(id=id, description=description, many=many)
        self.attributes = attributes
        self.examples = examples

    def accept(self, visitor: AbstractVisitor[T]) -> T:
        """Accept a visitor."""
        return visitor.visit_object(self)
