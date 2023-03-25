"""JSON encoder and decoder.

The encoder adds additional <json> tags around the JSON output,
while the decoder looks for these tags and removes them.

The usage of additional tags to wrap the content as an additional
layer of protection against the LLMs tendencies to provide explanations
about the output despite being told not to do that.
"""
import json
from typing import Any

from kor.exceptions import ParseError

from .typedefs import Encoder
from .utils import unwrap_tag, wrap_in_tag


class JSONEncoder(Encoder):
    def __init__(self, use_tags: bool = True) -> None:
        """Initialize the JSON encoder.

        Args:
            use_tags: Whether to wrap the output in a special JSON tags.
                      This may help identify the JSON content in cases when
                      the model attempts to add clarifying explanations.
        """
        self.use_tags = use_tags

    def encode(self, data: Any) -> str:
        """Encode."""
        content = json.dumps(data)
        if self.use_tags:
            return wrap_in_tag("json", json.dumps(data))
        return content

    def decode(self, text: str) -> Any:
        """Decode."""
        if self.use_tags:
            content = unwrap_tag("json", text)
        else:
            content = text

        if content is None:
            return {}
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ParseError(e)

    def get_instruction_segment(self) -> str:
        """Format instruction."""
        return (
            "Please output the extracted information in JSON format. Do not output"
            " anything except for the extracted information. Do not add any clarifying"
            " information. Do not add any fields that are not in the schema. If the"
            " text contains attributes that do not appear in the schema, please ignore"
            " them. All output must be in JSON format and follow the schema specified"
            " above. Wrap the JSON in <json> tags."
        )
