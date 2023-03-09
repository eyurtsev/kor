"""Definitions of input elements."""
import abc
import dataclasses
import re
from typing import Sequence, Mapping, Any, Generic, TypeVar

# For now, limit what's allowed for identifiers.
# The main constraints
# 1) Relying on HTML parser to parse output
# 2) One of the type descriptors is TypeScript, so we want to produce valid TypeScript identifiers.
# We can lift the constraints later if it becomes important, not worth the effort for a v0.
VALID_IDENTIFIER_PATTERN = re.compile(r"^[a-z_][0-9a-z_]*$")

T = TypeVar("T")


class AbstractVisitor(Generic[T], abc.ABC):
    """An abstract visitor. Define here to avoid cyclical imports for now."""

    def visit_text(self, node: "Text") -> T:
        """Visit text node."""
        return self.visit_default(node)

    def visit_number(self, node: "Number") -> T:
        """Visit text node."""
        return self.visit_default(node)

    def visit_object(self, node: "ObjectInput") -> T:
        """Visit object node."""
        return self.visit_default(node)

    def visit_selection(self, node: "Selection") -> T:
        """Visit selection node."""
        return self.visit_default(node)

    def visit_option(self, node: "Option") -> T:
        """Visit option node."""
        return self.visit_default(node)

    def visit_default(self, node: "AbstractInput") -> T:
        """Default node implementation."""
        raise NotImplementedError()


@dataclasses.dataclass(frozen=True, kw_only=True)
class AbstractInput(abc.ABC):
    """Abstract input element.

    Each input is expected to have a unique ID, and should
    only use alphanumeric characters.

    The ID should be unique across all inputs that belong
    to a given form.

    The description should describe what the input is about.
    """

    id: str  # Unique ID
    description: str = ""
    multiple: bool = True

    def __post_init__(self) -> None:
        """Post initialization hook."""
        if not VALID_IDENTIFIER_PATTERN.match(self.id):
            raise ValueError(
                f"`{self.id}` is not a valid identifier. "
                f"Please only use lower cased a-z, _ or the digits 0-9"
            )

        if not self.multiple:
            raise ValueError(
                "Reserved parameter. At the moment, multiple has to be True."
            )

    @abc.abstractmethod
    def accept(self, visitor: AbstractVisitor) -> Any:
        """Accept a visitor."""
        raise NotImplementedError()


@dataclasses.dataclass(frozen=True, kw_only=True)
class ExtractionInput(AbstractInput, abc.ABC):
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

    examples: Sequence[tuple[str, str | Sequence[str]]] = tuple()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Number(ExtractionInput):
    """Built-in number input."""

    def accept(self, visitor: AbstractVisitor[T]) -> T:
        """Accept a visitor."""
        return visitor.visit_number(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Text(ExtractionInput):
    """Built-in text input."""

    def accept(self, visitor: AbstractVisitor[T]) -> T:
        """Accept a visitor."""
        return visitor.visit_text(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Option(AbstractInput):
    """Built-in option input must be part of a selection input."""

    examples: Sequence[str] = tuple()

    def accept(self, visitor: AbstractVisitor[T]) -> T:
        """Accept a visitor."""
        return visitor.visit_option(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Selection(AbstractInput):
    """Built-in selection input.

    A selection input is composed of one or more options.

    ## Null examples

    Null examples are segments of text for which nothing should be extracted.
    Good null examples will likely be challenging, adversarial examples.

    For example:
        for an extraction input about company names nothing should be extracted
        from the text: "I eat an apple every day.".
    """

    options: Sequence[Option]
    null_examples: Sequence[str] = tuple()

    # @property
    # def option_ids(self) -> list[str]:
    #     """Get a list of the option ids."""
    #     return sorted(option.id for option in self.options)
    #
    def accept(self, visitor: AbstractVisitor[T]) -> T:
        """Accept a visitor."""
        return visitor.visit_selection(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ObjectInput(AbstractInput):
    """A definition for an object extraction.

    An extraction input can be associated with 2 different types of examples:

    1) extraction examples (called simply `examples`)
    2) null examples (called `null_examples`)

    ## Extraction examples

    A standard extraction example is a 2-tuple composed of a text segment and the expected
    extraction.

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

    elements: Sequence[ExtractionInput]
    examples: Sequence[tuple[str, Mapping[str, str | Sequence[str]]]] = tuple()
    # If false, will treat the inputs independent.
    # Is there a better name for this?! I want it to be True by default
    # which rules out as_input_bag
    group_as_object: bool = True

    def accept(self, visitor: AbstractVisitor[T]) -> T:
        """Accept a visitor."""
        return visitor.visit_object(self)
