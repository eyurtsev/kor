from collections import defaultdict
from html.parser import HTMLParser
from typing import Any, DefaultDict, Dict, List, Optional


class TagParser(HTMLParser):
    def __init__(self) -> None:
        """A heavy-handed solution, but it's fast for prototyping.

        Might be re-implemented later to restrict scope to the limited grammar, and
        more efficiency.

        Uses an HTML parser to parse a limited grammar that allows
        for syntax of the form:

            INPUT -> JUNK? VALUE*
            JUNK -> JUNK_CHARACTER+
            JUNK_CHARACTER -> whitespace | ,
            VALUE -> <IDENTIFIER>DATA</IDENTIFIER> | OBJECT
            OBJECT -> <IDENTIFIER>VALUE+</IDENTIFIER>
            IDENTIFIER -> [a-Z][a-Z0-9_]*
            DATA -> .*

        Interprets the data to allow repetition of tags and recursion
        to support representation of complex types.

        ^ Just another approximately wrong grammar specification.
        """
        super().__init__()

        self.parse_data: DefaultDict[str, List[Any]] = defaultdict(list)
        self.stack: List[DefaultDict[str, List[str]]] = [self.parse_data]
        self.success = True
        self.depth = 0
        self.data: Optional[str] = None

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        """Hook when a new tag is encountered."""
        self.depth += 1
        self.stack.append(defaultdict(list))
        self.data = None

    def handle_endtag(self, tag: str) -> None:
        """Hook when a tag is closed."""
        self.depth -= 1
        top_of_stack = dict(self.stack.pop(-1))  # Pop the dictionary we don't need it

        # If a lead node
        is_leaf = self.data is not None
        # Annoying to type here, code is tested, hopefully OK
        value = self.data if is_leaf else top_of_stack
        # Difficult to type this correctly with mypy (maybe impossible?)
        # Can be nested indefinitely, so requires self referencing type
        self.stack[-1][tag].append(value)  # type: ignore
        # Reset the data so we if we encounter a sequence of end tags, we
        # don't confuse an outer end tag for belonging to a leaf node.
        self.data = None

    def handle_data(self, data: str) -> None:
        """Hook when handling data."""
        # The only data that's allowed is whitespace or a comma surrounded by whitespace
        if self.depth == 0 and data.strip() not in (",", ""):
            # If this is triggered the parse should be considered invalid.
            self.success = False
        self.data = data


def parse_llm_output(llm_output: str) -> Dict[str, List[str]]:
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
    if not tag_parser.success:
        return {}
    return dict(tag_parser.parse_data)
