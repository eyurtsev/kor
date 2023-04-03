from collections import defaultdict
from html.parser import HTMLParser
from typing import Any, DefaultDict, Dict, List, Mapping, Optional, Sequence, Union

from kor.encoders.typedefs import Encoder

LiteralType = Union[str, int, float]


def _write_literal(tag_name: str, value: LiteralType) -> str:
    """Write literal."""
    return f"<{tag_name}>{value}</{tag_name}>"


def _write_list(tag_name: str, values: Sequence[LiteralType]) -> str:
    """Write list."""
    return "".join(_write_tag(tag_name, value) for value in values)


def _write_dict(tag_name: str, data: Mapping[str, Any]) -> str:
    """Write a dict."""
    s_data = "".join(
        [
            _write_tag(key, value)
            for key, value in sorted(data.items(), key=lambda item: item[0])
        ]
    )
    return _write_tag(tag_name, s_data)


def _write_tag(
    tag_name: str, data: Union[LiteralType, Sequence[LiteralType], Mapping[str, Any]]
) -> str:
    """Write a tag."""
    # Dispatch based on type.
    if isinstance(data, (str, int, float)):
        return _write_literal(tag_name, data)
    elif isinstance(data, list):
        return _write_list(tag_name, data)
    elif isinstance(data, dict):
        return _write_dict(tag_name, data)
    else:
        raise NotImplementedError(f"No support for {tag_name}")


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


# PUBLIC API


class XMLEncoder(Encoder):
    """Experimental XML encoder to encode and decode data.

    .. warning::
        This encoder is not recommended for usage, at least not without further
        benchmarking for your use-case.

    The decoder re-interprets all data types as lists, which makes validating
    and using parser results more involved. It's unclear whether the encoder
    offers more advantages over other encoders (e.g., JSON or CSV).

    The encoder would encode the following dictionary

    .. code-block:: JSON

        {
            "color": ["red", "blue"],
            "height": ["6.1"],
            "width": ["3"],
        }

    As:

    .. code-block:: XML

        <color>red</color><height>6.1</height><width>3</width><color>blue</color>

    A tag be repeated multiple times to represent multiple list elements.
    """

    def encode(self, obj: Mapping[str, Any]) -> str:
        """Encode the object as XML."""
        if not isinstance(obj, dict):
            raise TypeError(f"Expected {obj} to be of type dict, got {type(obj)}")
        return "".join(_write_tag(key, value) for key, value in obj.items())

    def decode(self, text: str) -> Dict[str, List[str]]:
        """Decode the XML as an object."""
        tag_parser = TagParser()
        tag_parser.feed(text)
        if not tag_parser.success:
            return {}
        return dict(tag_parser.parse_data)

    def get_instruction_segment(self) -> str:
        """Format the instructions segment."""
        return (
            "Please enclose the extracted information in HTML style tags with the tag"
            " name corresponding to the corresponding component ID. Use angle style"
            " brackets for the tags ('>' and '<'). Only output tags when you're"
            " confident about the information that was extracted from the user's query."
            " If you can extract several pieces of relevant information from the query,"
            " then include all of them. If the type is an array, please repeat the"
            " corresponding tag name multiple times once for each relevant extraction."
            " Do NOT output anything except for the extracted information. Only output"
            " information inside the HTML style tags. Do not include any notes or any"
            " clarifications. "
        )
