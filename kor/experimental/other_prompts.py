#
# def date_input_block(user_input: str, date_input: DateInput) -> str:
#     """Get prompt for parsing a date input."""
#
#     prompt = (
#         "The input may or may not contain a date. If it contains a date, please "
#         " include it in the output inside of <date> and </date> tags, and report it"
#         "in ISO-8601 format (YYYY-MM-DD). If it doesn't contain a date, please "
#         "output <null/>. Do not output anything else.\n"
#         "\n"
#         "Input: I went to the store on January 7th, 2023.\n"
#         "Output: <date>2023-01-07</date>\n"
#         "Input: Next \n"
#         "Output: <date>2023-01-07</date>\n"
#         "Input: {user_input}\n"
#         "Output: ",
#     )
#     return prompt
#
#
# def date_block(user_input: str, options: Sequence[Option]) -> str:
#     """User is supposed to enter a date."""
#     options_block = [f"<{option.id}> - {option.description}" for option in options]
#
#     options_block = "\n".join(options_block)
#
#     formatted_examples = ["Input: blaheoiqwd", "Output: <unsure>"]
#
#     for option in options:
#         for example in option.examples:
#             formatted_examples.append(f"Input: {example}")
#             formatted_examples.append(f"Output: <{option.id}>")
#             break
#
#     examples_block = "\n".join(formatted_examples)
#
#     prompt = (
#         f"You are interacting with a user. The user has to choose one of options below. "
#         f"Please determine which of the options the user is selecting. The user may select "
#         f"one and only one option. For the output, output the option name without any whitespace, "
#         f"and nothing else. If you're not sure, please output <unsure>. \n"
#         "\n"
#         "Options:\n"
#         f"{options_block}\n\n"
#         f"{examples_block}\n"
#         f"Input: {user_input}\n"
#         f"Output:\n"
#     )
#     return prompt
#
#
# # TEMPORARY
#
#
# def generate_proceed_block(user_input: str) -> str:
#     """Parse yes/no choice."""
#     return (
#         "You are interacting with a human and are trying to determine if the person is"
#         "selecting to proceed (<yes/>) or cancel (<no/>). If you don't know say <unsure/>\n"
#         "\n"
#         "Input: No, I need to make some changes\n"
#         "Output: <no/>\n"
#         "\n"
#         "Input: OK\n"
#         "Output: <yes/>\n"
#         "\n"
#         "Input: Yes\n"
#         "Output: <yes/>\n"
#         "\n"
#         "Input: hmmm\n"
#         "Output: <unsure/>\n"
#         "\n"
#         "Input: {user_input}\n"
#         "Output:\n"
#     )
#
#
# FLIGHT_BOOKING = (
#     "You are interacting with a user who is attempting to buy a flight ticket. "
#     "They need to specify an origin airport or "
#     "city, a destination airport or city and a date or time for the flight. The user may also "
#     "specify a price range for the tickets. Please read the user input and extract the relevant "
#     "pieces of information. Format the extracted information between appropriate opening and "
#     "closing tags (e.g., <origin>LAX</origin>). If no information can be found, output an empty "
#     "string between for the given tag.\n "
#     "\n"
#     "Use only the tags: <destination>, <origin>, <time>, <price-min>, <price-max>\n"
#     "\n"
#     "Input: I want to fly at 8:00 AM 2011-01-01 to Hawaii.\n"
#     "Output: <time>8:00 AM 2011-01-01</time>, <destination>Hawaii</destination>\n"
#     "\n"
#     "Input: Book me a flight from TLV to BOS on 06/06\n"
#     "Output: <origin>TLV</origin>, <destination>BOS</destination>, <time>06/06</time>\n"
#     "\n"
#     "Input: Flight from LAX between $100-$200\n"
#     "Output: <origin>LAX</origin>,<price-min>$100</price-min>,<price-max>$200</price-max>\n"
#     "\n"
#     "Input: {user_input}\n"
#     "Output:\n"
# )
#
# FLIGHT_PROGRESS = """
# "You are interacting with a user who is attempting to buy a flight ticket. "
# "They need to specify an origin airport or "
# "city, a destination airport or city and a date or time for the flight. The user may also "
# "specify a price range for the tickets. Please read the user input and extract the relevant "
# "pieces of information. Format the extracted information between appropriate opening and "
# "closing tags (e.g., <origin>LAX</origin>). If no information can be found, output an empty "
# "string between for the given tag.\n "
# "\n"
# "Use only the tags: <destination>, <origin>, <time>, <price-min>, <price-max>\n"
# "\n"
# "Input: I want to fly at 8:00 AM 2011-01-01 to Hawaii.\n"
# "Output: <time>8:00 AM 2011-01-01</time>, <destination>Hawaii</destination>\n"
# "\n"
# "Input: Book me a flight from TLV to BOS on 06/06\n"
# "Output: <origin>TLV</origin>, <destination>BOS</destination>, <time>06/06</time>\n"
#
# You've already collected some information from the user. The user can specify that they
# want to update a given piece of information or add more missing information.
#
# Input: {user_input}
# """
#
#
# PROCEED_OPTIONS = [
#     Option(
#         id="yes",
#         description="user wants to proceed / continue",
#         examples=["Yes", "OK", "correct"],
#     ),
#     Option(
#         id="no",
#         description="user wants to cancel",
#         examples=["no", "wrong", "bad", "abort", "cancel"],
#     ),
# ]
from kor.elements import Option, Selection


def _compile_option_examples(id: str, option: Option) -> str:
    """Compile examples of an option input."""
    formatted_examples = []

    if not isinstance(option, Option):
        raise TypeError(type(option))

    for example in option.examples:
        formatted_examples.extend(
            [f"Input: {example}", f"Output: <{id}>{option.id}</{id}>"]
        )

    return "\n".join(formatted_examples)


def _compile_selection_examples(selection: Selection) -> str:
    if not isinstance(selection, Selection):
        raise AssertionError()
    return "\n".join(
        _compile_option_examples(selection.id, option) for option in selection.options
    )


def _generate_prompt_for_selection(user_input: str, selection: Selection) -> str:
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
        f"Input: {user_input}\n"
        f"Output:\n"
    )
