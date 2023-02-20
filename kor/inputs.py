"""Use to store Input elements."""
import dataclasses
from typing import Sequence


@dataclasses.dataclass(frozen=True)
class Input:
    id: str  # Unique ID
    examples: Sequence[str]


@dataclasses.dataclass(frozen=True)
class DateInput(Input):
    description: str
    format: str


@dataclasses.dataclass(frozen=True)
class TextInput:
    id: str
    description: str
    examples: Sequence[str]


@dataclasses.dataclass(frozen=True)
class AutocompleteInput:
    id: str
    description: str


@dataclasses.dataclass(frozen=True)
class Option:
    id: str
    description: str
    examples: Sequence[str]


@dataclasses.dataclass(frozen=True)
class Selection:
    id: str
    description: str
    options: Sequence[Option]


@dataclasses.dataclass(frozen=True)
class Form:
    id: str
    description: str
    inputs: Sequence[Selection]


CHOICE_TYPE = "RADIO"


def compile_examples(input: Input):
    formatted_examples = []

    for example in input.examples:
        formatted_examples.extend([f"Input: {example}", f"Output: <{option.id}>"])


def date_input_block(input: str, date_input: DateInput) -> str:
    """Get prompt for parsing a date input."""

    prompt = (
        "The input may or may not contain a date. If it contains a date, please "
        " include it in the output inside of <date> and </date> tags, and report it"
        "in ISO-8601 format (YYYY-MM-DD). If it doesn't contain a date, please "
        "output <null/>. Do not output anything else.\n"
        "\n"
        "Input: I went to the store on January 7th, 2023.\n"
        "Output: <date>2023-01-07</date>\n"
        "Input: Next \n"
        "Output: <date>2023-01-07</date>\n"
        "Input: {input}\n"
        "Output: ",
    )
    return prompt


def choice_block(input: str, kind: str, options: Sequence[Option]) -> str:
    """Choice bock with options."""
    options_block = [f"<{option.id}> - {option.description}" for option in options]
    options_block = "\n".join(options_block)

    formatted_examples = ["Input: blaheoiqwd", "Output: <unsure>"]

    for option in options:
        for example in option.examples:
            formatted_examples.extend([f"Input: {example}", f"Output: <{option.id}>"])

    examples_block = "\n".join(formatted_examples)

    prompt = (
        f"You are interacting with a user. The user has to choose one of options below. "
        f"Please determine which of the options the user is selecting. The user may select "
        f"one and only one option. For the output, output the option name without any whitespace, "
        f"and nothing else. If you're not sure, please output <unsure>. \n"
        "\n"
        "Options:\n"
        f"{options_block}\n\n"
        f"{examples_block}\n"
        f"Input: {input}\n"
        f"Output:\n"
    )
    return prompt


PROCEED_OPTIONS = [
    Option(
        id="yes",
        description="user wants to proceed / continue",
        examples=["Yes", "OK", "correct"],
    ),
    Option(
        id="no",
        description="user wants to cancel",
        examples=["no", "wrong", "bad", "abort", "cancel"],
    ),
]


def date_block(input: str, options: Sequence[Option]) -> str:
    """User is supposed to enter a date."""
    options_block = [f"<{option.id}> - {option.description}" for option in options]

    options_block = "\n".join(options_block)

    formatted_examples = ["Input: blaheoiqwd", "Output: <unsure>"]

    for option in options:
        for example in option.examples:
            formatted_examples.append(f"Input: {example}")
            formatted_examples.append(f"Output: <{option.id}>")
            break

    examples_block = "\n".join(formatted_examples)

    prompt = (
        f"You are interacting with a user. The user has to choose one of options below. "
        f"Please determine which of the options the user is selecting. The user may select "
        f"one and only one option. For the output, output the option name without any whitespace, "
        f"and nothing else. If you're not sure, please output <unsure>. \n"
        "\n"
        "Options:\n"
        f"{options_block}\n\n"
        f"{examples_block}\n"
        f"Input: {input}\n"
        f"Output:\n"
    )
    return prompt


def generate_proceed_block(input: str) -> str:
    """Parse yes/no choice."""
    return (
        "You are interacting with a human and are trying to determine if the person is "
        "selecting to proceed (<yes/>) or cancel (<no/>). If you don't know say <unsure/>\n"
        "\n"
        "Input: No, I need to make some changes\n"
        "Output: <no/>\n"
        "\n"
        "Input: OK\n"
        "Output: <yes/>\n"
        "\n"
        "Input: Yes\n"
        "Output: <yes/>\n"
        "\n"
        "Input: hmmm\n"
        "Output: <unsure/>\n"
        "\n"
        "Input: {input}\n"
        "Output:\n"
    )
