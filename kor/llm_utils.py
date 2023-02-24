"""Parse LLM Response."""

from collections import defaultdict

from html.parser import HTMLParser
from typing import Any


class TagParser(HTMLParser):
    def __init__(self) -> None:
        """A heavy-handed solution, but it's fast for prototyping.

        Might be re-implemented later to restrict scope to the limited grammar.

        Uses an HTML parser to parse a limited grammar that allows for syntax of the form:

            INPUT -> JUNK? VALUE*
            JUNK -> JUNK_CHARACTER+
            JUNK_CHARACTER -> whitespace | ,
            VALUE -> <IDENTIFIER>DATA</IDENTIFIER>
            IDENTIFIER -> [a-Z][a-Z0-9_]*
            DATA -> .*

        ^ Just another approximately wrong grammar specification.
        """
        super().__init__()
        self.current_tag = None
        self.data = defaultdict(list)
        self.success = True

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        """Hook when a new tag is encountered."""
        self.current_tag = tag

    def handle_endtag(self, tag: str) -> None:
        """Hook when a tag is closed."""
        self.current_tag = None

    def handle_data(self, data: str) -> None:
        """Hook when handling data."""
        # The only data that's allowed is whitespace or a comma surrounded by whitespace
        if self.current_tag is None:
            if data.strip() not in (",", ""):
                self.success = False
        else:
            self.data[self.current_tag].append(data)


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
        "height": "6.1",
        "width": "3",
    }
    """
    tag_parser = TagParser()
    tag_parser.feed(llm_output)
    if not tag_parser.success:
        return {}
    return dict(tag_parser.data)
