"""Use to store Input elements."""
import dataclasses
from typing import Sequence

FLIGHT_BOOKING = (
    "You are interacting with a user who is attempting to buy a flight ticket. "
    "They need to specify an origin airport or "
    "city, a destination airport or city and a date or time for the flight. The user may also "
    "specify a price range for the tickets. Please read the user input and extract the relevant "
    "pieces of information. Format the extracted information between appropriate opening and "
    "closing tags (e.g., <origin>LAX</origin>). If no information can be found, output an empty "
    "string between for the given tag.\n "
    "\n"
    "Use only the tags: <destination>, <origin>, <time>, <price-min>, <price-max>\n"
    "\n"
    "Input: I want to fly at 8:00 AM 2011-01-01 to Hawaii.\n"
    "Output: <time>8:00 AM 2011-01-01</time>, <destination>Hawaii</destination>\n"
    "\n"
    "Input: Book me a flight from TLV to BOS on 06/06\n"
    "Output: <origin>TLV</origin>, <destination>BOS</destination>, <time>06/06</time>\n"
    "\n"
    "Input: Flight from LAX between $100-$200\n"
    "Output: <origin>LAX</origin>,<price-min>$100</price-min>,<price-max>$200</price-max>\n"
    "\n"
    "Input: {input}\n"
    "Output:\n"
)

FLIGHT_PROGRESS = """
"You are interacting with a user who is attempting to buy a flight ticket. "
"They need to specify an origin airport or "
"city, a destination airport or city and a date or time for the flight. The user may also "
"specify a price range for the tickets. Please read the user input and extract the relevant "
"pieces of information. Format the extracted information between appropriate opening and "
"closing tags (e.g., <origin>LAX</origin>). If no information can be found, output an empty "
"string between for the given tag.\n "
"\n"
"Use only the tags: <destination>, <origin>, <time>, <price-min>, <price-max>\n"
"\n"
"Input: I want to fly at 8:00 AM 2011-01-01 to Hawaii.\n"
"Output: <time>8:00 AM 2011-01-01</time>, <destination>Hawaii</destination>\n"
"\n"
"Input: Book me a flight from TLV to BOS on 06/06\n"
"Output: <origin>TLV</origin>, <destination>BOS</destination>, <time>06/06</time>\n"

You've already collected some information from the user. The user can specify that they
want to update a given piece of information or add more missing information. 

Input: {input}
"""


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
class DateInput:
    id: str
    description: str
    format: str
    examples: Sequence[str]


@dataclasses.dataclass(frozen=True)
class Form:
    id: str
    description: str
    inputs: Sequence[Selection]


CHOICE_TYPE = "RADIO"


def date_input_block(input: str, date_input: DateInput) -> str:
    """Get prompt for parsing a date input."""
    prompt = """
    You are interacting with a user. Your goal is to
    """


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
