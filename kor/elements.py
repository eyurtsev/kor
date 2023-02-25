"""Definitions of input elements."""
import abc
import dataclasses
from typing import Sequence

import re

VALID_IDENTIFIER_PATTERN = re.compile(r"\w+")


def _write_tag(tag_name: str, data: str) -> str:
    """Write a tag."""
    return f"<{tag_name}>{data}</{tag_name}>"


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
    description: str

    @property
    def input_full_description(self) -> str:
        """A full description for the input."""
        return f"<{self.id}>: {self.type_name} # {self.description}"

    @property
    def type_name(self) -> str:
        """Default implementation of a type name is just the class name."""
        class_name = self.__class__.__name__
        if class_name.endswith("Input"):
            return class_name.removesuffix("Input")
        return class_name

    def __post_init__(self) -> None:
        """Post initialization hook."""
        if not VALID_IDENTIFIER_PATTERN.match(self.id):
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

    examples: Sequence[tuple[str, str]]
    null_examples: Sequence[str] = tuple()

    @property
    def llm_examples(self) -> list[tuple[str, str]]:
        """List of 2-tuples of input, output.

        Does not include the `Input: ` or `Output: ` prefix
        """
        formatted_examples = []
        for text, extraction in self.examples:
            formatted_examples.append((text, _write_tag(self.id, extraction)))

        for null_example in self.null_examples:
            formatted_examples.append((null_example, f""))
        return formatted_examples


@dataclasses.dataclass(frozen=True, kw_only=True)
class DateInput(ExtractionInput):
    """Built-in date input."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class Number(ExtractionInput):
    """Built-in number input."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class TimePeriod(ExtractionInput):
    """Built-in for more general time-periods; e.g., 'after dinner', 'next year'"""


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
    # If multiple=true, selection input allows for multiple options to be selected.
    multiple: bool = False

    @property
    def llm_examples(self) -> list[tuple[str, str]]:
        """Examples ready for llm-consumption."""
        formatted_examples = []
        for option in self.options:
            for example in option.examples:
                formatted_examples.append((example, _write_tag(self.id, option.id)))
        return formatted_examples

    @property
    def option_ids(self) -> list[str]:
        """Get a list of the option ids."""
        return sorted(option.id for option in self.options)

    @property
    def type_name(self) -> str:
        """Over-ride type name to provide special behavior."""
        options_string = ",".join(self.option_ids)
        if self.multiple:
            formatted_type = f"Multiple Select[{options_string}]"
        else:
            formatted_type = f"Select[{options_string}]"
        return formatted_type


@dataclasses.dataclass(frozen=True, kw_only=True)
class Form(AbstractInput):
    """A form encapsulated a collection of inputs.

    The form should have a good description of the context in which the data is collected.
    """

    elements: Sequence[ExtractionInput]
