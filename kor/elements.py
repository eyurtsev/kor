"""Definitions of input elements."""
import abc
import dataclasses
from typing import Sequence, Tuple


@dataclasses.dataclass(frozen=True)
class AbstractInput(abc.ABC):
    id: str  # Unique ID
    description: str


@dataclasses.dataclass(frozen=True)
class ExtractionInput(AbstractInput):
    examples: Sequence[Tuple[str, str]]


@dataclasses.dataclass(frozen=True)
class DateInput(ExtractionInput):
    pass


@dataclasses.dataclass(frozen=True)
class Number(ExtractionInput):
    pass


@dataclasses.dataclass(frozen=True)
class NumericRange(ExtractionInput):
    pass


@dataclasses.dataclass(frozen=True)
class TextInput(ExtractionInput):
    pass


@dataclasses.dataclass(frozen=True)
class AutocompleteInput(AbstractInput):
    pass


@dataclasses.dataclass(frozen=True)
class Option(AbstractInput):
    examples: Sequence[str]


@dataclasses.dataclass(frozen=True)
class Selection(AbstractInput):
    options: Sequence[Option]
    examples: Sequence[str]
    # If true, allows for multiple options to be selected.
    multiple: bool = False

    def option_ids(self) -> Sequence[str]:
        """Get a list of the option ids."""
        return [option.id for option in self.options]


@dataclasses.dataclass(frozen=True)
class Form(AbstractInput):
    elements: Sequence[AbstractInput]
    examples: Sequence[str]
