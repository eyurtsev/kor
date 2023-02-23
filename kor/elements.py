"""Definitions of input elements."""
import dataclasses
import abc
from typing import Sequence


@dataclasses.dataclass(frozen=True)
class AbstractInput(abc.ABC):
    id: str  # Unique ID
    examples: Sequence[str]


@dataclasses.dataclass(frozen=True)
class DateInput(AbstractInput):
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
class Option(AbstractInput):
    examples: Sequence[str]
    description: str


@dataclasses.dataclass(frozen=True)
class Selection(AbstractInput):
    description: str
    options: Sequence[Option]

    def allowed_transitions(self):
        return [option.id for option in self.options]


@dataclasses.dataclass(frozen=True)
class Form(AbstractInput):
    description: str
    elements: Sequence[Selection]


CHOICE_TYPE = "RADIO"


def compile_option_examples(id: str, input: Option) -> str:
    """Compile examples of an option input."""
    formatted_examples = []

    if not isinstance(input, Option):
        raise TypeError(type(input))

    for example in input.examples:
        formatted_examples.extend(
            [f"Input: {example}", f"Output: <{id}>{input.id}</{id}>"]
        )

    return "\n".join(formatted_examples)


def _compile_selection_examples(selection: Selection) -> str:
    if not isinstance(selection, Selection):
        raise AssertionError()
    return "\n".join(
        compile_option_examples(selection.id, option) for option in selection.options
    )


def _generate_prompt_for_selection(input: str, selection: Selection) -> str:
    """Choice bock with options."""
    options_block = [
        f"<{option.id}> - {option.description}" for option in selection.options
    ]

    options_block = "\n".join(options_block)

    examples_block = _compile_selection_examples(selection)

    return (
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


def _generate_prompt_for_form(user_input: str, form: Form) -> str:
    """Generate a prompt for a form."""
    elements_info = []
    for element in form.elements:
        if not isinstance(element, Selection):
            raise NotImplemented()

        values = ",".join(element.allowed_transitions())

        formatted_type = f"Selection[{values}]"

        elements_info.append(
            f"* <{element.id}>: {formatted_type} # {element.description}"
        )

    elements_info = "\n".join(elements_info)

    individual_examples = [
        _compile_selection_examples(element) for element in form.elements
    ]

    examples_block = "\n".join(individual_examples)

    return (
        f"You are helping a user fill out a form. The user will type information and your goal will "
        f"be to parse the user's input.\n"
        f'The description of the form is: "{form.description}"'
        "Below is a list of the components showing the component ID, its type and "
        "a short description of it.\n\n"
        f"{elements_info}\n\n"
        "Your task is to parse the user input and determine to what values the user is attempting "
        "to set each component of the form. "
        "Please enclose the extracted information in HTML style tags with the tag name "
        "corresponding to the corresponding component ID. Use angle style brackets for the "
        "tags ('>' and '<'). "
        "Only output tags when you're confident about the information that was extracted "
        "from the user's query. If you can extract several pieces of relevant information "
        "from the query include use a comma to separate the tags."
        "\n\n"
        f"{examples_block}\n"
        f"Input: {user_input}\n"
        "Output: "
    )


def generate_prompt_for_input(user_input: str, element: AbstractInput):
    if isinstance(element, Form):
        return _generate_prompt_for_form(user_input, element)
    elif isinstance(element, Selection):
        return _generate_prompt_for_selection(user_input, element)
    else:
        raise NotImplemented()


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
