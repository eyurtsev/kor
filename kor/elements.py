"""Definitions of input elements."""
import abc
import dataclasses
from typing import Sequence, Tuple


@dataclasses.dataclass(frozen=True, kw_only=True)
class AbstractInput(abc.ABC):
    """Abstract input element.

    Each input is expected to have a unique ID, and should
    use alphanumeric characters and not start with a number.

    The ID should be unique across all inputs that belong
    to a given form.

    The description should describe what the input is about.
    """

    id: str  # Unique ID
    description: str
    required: bool = False

    @property
    def input_full_description(self) -> str:
        """A full description for the input."""
        return f"<{self.id}>: {self.type_name} # {self.description}"

    @property
    def type_name(self) -> str:
        """Default implementation of a type name is just the class name."""
        return self.__class__.__name__

    def __post_init__(self) -> None:
        """Post initialization hook."""
        if not self.id.isidentifier():
            raise ValueError(f"`{self.id}` is not a valid identifier.")


@dataclasses.dataclass(frozen=True, kw_only=True)
class ExtractionInput(AbstractInput, abc.ABC):
    """An abstract definition for inputs that involve extraction.

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

    examples: Sequence[Tuple[str, str]]
    null_examples: Sequence[str] | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class DateInput(ExtractionInput):
    """Built-in date input."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class Number(ExtractionInput):
    """Built-in number input."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class NumericRange(ExtractionInput):
    """Built-in numeric range input."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class TextInput(ExtractionInput):
    """Built-in text input."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class Option(AbstractInput):
    """Built-in option input must be part of a selection input."""

    examples: Sequence[str]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Selection(AbstractInput):
    """Built-in selection input.

    A selection input is composed of one or more options.
    """

    options: Sequence[Option]
    examples: Sequence[str]
    # If multiple=true, selection input allows for multiple options to be selected.
    multiple: bool = False

    def option_ids(self) -> Sequence[str]:
        """Get a list of the option ids."""
        return [option.id for option in self.options]

    def type_name(self) -> str:
        """Over-ride type name to provide special behavior."""
        option_ids = sorted(option.id for option in self.options)
        if self.multiple:
            formatted_type = f"Multiple Select[{option_ids}]"
        else:
            formatted_type = f"Select[{option_ids}]"
        return formatted_type


@dataclasses.dataclass(frozen=True, kw_only=True)
class Form(AbstractInput):
    """A form encapsulated a collection of inputs.

    The form should have a good description of the context in which the data is collected.
    """

    elements: Sequence[AbstractInput]
    examples: Sequence[str]
