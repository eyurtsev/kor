"""Definitions of input elements."""
import abc
import dataclasses
from typing import Sequence, Tuple


@dataclasses.dataclass(frozen=True, kw_only=True)
class AbstractInput(abc.ABC):
    """Abstract input element.

    Each input is expected to have a unique ID, and should
    use alpha numeric characters and not start with a number.

    The ID should be unique across all inputs that belong
    to a given form.

    The description should describe what the input is about.
    """

    id: str  # Unique ID
    description: str

    def __post_init__(self) -> None:
        """Post initialization hook."""
        if not self.id.isidentifier():
            raise ValueError(f"`{self.id}` is not a valid identifier.")


@dataclasses.dataclass(frozen=True, kw_only=True)
class ExtractionInput(AbstractInput, abc.ABC):
    """An abstract definition for inputs that involve extraction.

    Examples are a sequence of 2-tuples.

    Each 2-tuple is of the format (example text, desired extracted output).

    For example, if one created a numeric class
    """

    examples: Sequence[Tuple[str, str]]


@dataclasses.dataclass(frozen=True, kw_only=True)
class DateInput(ExtractionInput):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Number(ExtractionInput):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NumericRange(ExtractionInput):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class TextInput(ExtractionInput):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class AutocompleteInput(AbstractInput):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Option(AbstractInput):
    examples: Sequence[str]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Selection(AbstractInput):
    options: Sequence[Option]
    examples: Sequence[str]
    # If true, allows for multiple options to be selected.
    multiple: bool = False

    def option_ids(self) -> Sequence[str]:
        """Get a list of the option ids."""
        return [option.id for option in self.options]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Form(AbstractInput):
    """A form encapsulated a collection of inputs.

    The form should have a good description of the context in which the data is collected.
    """

    elements: Sequence[AbstractInput]
    examples: Sequence[str]
