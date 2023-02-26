"""Utilities to work with LLMs."""
import os
from collections import defaultdict
from html.parser import HTMLParser
from typing import Any

import openai


def _set_in(d: dict[str, Any], path: tuple[str], value: str):
    """Mutate d in place to add a value at the given path."""
    if len(path) == 1:
        key = path[0]
        d[key] = value
    else:
        key = path[0]
        rest_path = path[1:]
        # TODO(Eugene): Verify that we're not mutating str -> dict, or dict -> str
        if key in d:
            new_d = d[key]
        else:
            new_d = {}
            d[key] = new_d

        _set_in(new_d, rest_path, value)


class TagParser(HTMLParser):
    def __init__(self) -> None:
        """A heavy-handed solution, but it's fast for prototyping.

        Might be re-implemented later to restrict scope to the limited grammar, and
        more efficiency.

        Uses an HTML parser to parse a limited grammar that allows for syntax of the form:

            INPUT -> JUNK? VALUE*
            JUNK -> JUNK_CHARACTER+
            JUNK_CHARACTER -> whitespace | ,
            VALUE -> <IDENTIFIER>DATA</IDENTIFIER>
            IDENTIFIER -> [a-Z][a-Z0-9_]*
            DATA -> .*

        ^ Approximate grammar specification, probably has some error
        """
        super().__init__()
        # self.stack: list[str] = []
        self.depth = 0
        self.stack: list[defaultdict[list]] = [defaultdict(list)]
        self.all_data = []
        self.current_data = None
        self.success = True

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        """Hook when a new tag is encountered."""
        self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        """Hook when a tag is closed."""
        self.depth -= 1
        self.stack.pop(-1)

    def handle_data(self, data: str) -> None:
        """Hook when handling data."""
        # The only data that's allowed is whitespace or a comma surrounded by whitespace
        if not self.stack:
            if data.strip() not in (",", ""):
                self.success = False
        else:
            self.current_data = data
            # self.all_data.append((tuple(self.stack), data))

    def finalized_data(self):
        """Get interpreted data.

        Super clunky -- only top level namespace allows for repetition.
        """


# PUBLIC API


def parse_llm_output(llm_output: str) -> dict[str, list[str]]:
    """Parse a response from an LLM.

    The format of the response is to enclose the input id in angle brackets and
    the value of the input is the data inside the tag.

    <input_id>selected value</input_id>

    The input_id can be repeated multiple times to support the use case of a selection
    that allows for multiple options to be selected.

    The response can contain selections for multiple different inputs.

    Tags are to be optionally separated by one or more commas or whitespace.

    <color>red</color>,<height>6.1</height>,<width>3</width>,<color>blue</color>

    Would represent a valid output. It would be interpreted as:

    {
        "color": ["red", "blue"],
        "height": ["6.1"],
        "width": ["3"],
    }
    """
    tag_parser = TagParser()
    tag_parser.feed(llm_output)
    return tag_parser.all_data

    return all_data
    return dict(all_data)

    if not tag_parser.success:
        return {}
    return dict(tag_parser.data)


class LLM:
    def __init__(self, verbose: bool = False) -> None:
        """Initialize the LLM model."""
        openai.api_key = os.environ["OPENAI_API_KEY"]
        self.verbose = verbose

    def __call__(self, prompt: str) -> str:
        """Invoke the LLM with the given prompt."""
        if self.verbose:
            print("-" * 80)
            print("Prompt: ")
            print(prompt)
            print("-" * 80)
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0,
            max_tokens=100,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        print("Model response: ")
        print(response)
        text = response["choices"][0]["text"]
        return text
