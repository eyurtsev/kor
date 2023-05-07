"""JSON encoder and decoder."""
import json
from typing import Any

from kor.exceptions import ParseError

from .typedefs import Encoder
from .utils import unwrap_tag, wrap_in_tag


class JSONEncoder(Encoder):
    """JSON encoder and decoder.

    The encoder by default adds additional <json> tags around the JSON output,

    Additional tags are added to the output to help identify the JSON content
    within the LLM response and extract it.

    The usage of <json> tags is similar to the usage of ```JSON and ``` marks.

    Examples:

        .. code-block:: python

            from kor import JSONEncoder

            json_encoder = JSONEncoder(use_tags=True)
            data = {"name": "Café"}
            json_encoder.encode(data)
            # '<json>{"name": "Café"}</json>'

            json_encoder = JSONEncoder(use_tags=True, ensure_ascii=True)
            data = {"name": "Café"}
            json_encoder.encode(data)
            # '<json>{"name": "Caf\\u00e9"}</json>'

    """

    def __init__(self, use_tags: bool = True, ensure_ascii: bool = False) -> None:
        """Initialize the JSON encoder.

        Args:
            use_tags: Whether to wrap the output in a special JSON tags.
                      This may help identify the JSON content in cases when
                      the model attempts to add clarifying explanations.
            ensure_ascii: Whether to escape non-ASCII characters.
                      Default is False to preserve non-ASCII characters as
                      that it a more sensible behavior for the extraction
                      use cases.
        """
        self.use_tags = use_tags
        self.ensure_ascii = ensure_ascii

    def encode(self, data: Any) -> str:
        """Encode the data as JSON.

        Args:
            data: JSON serializable data.

        Returns:
            The JSON encoded data as a string optionally wrapped in <json> tags.
        """
        content = json.dumps(data)
        if self.use_tags:
            return wrap_in_tag("json", json.dumps(data, ensure_ascii=self.ensure_ascii))
        return content

    def decode(self, text: str) -> Any:
        """Decode the text as JSON.

        If the encoder is using tags, the <json> content is identified within the text
        and then is decoded.

        Args:
            text: the text to be decoded

        Returns:
            The decoded JSON data.
        """
        if self.use_tags:
            content = unwrap_tag("json", text)
        else:
            content = text

        if content is None:
            return {}
        try:
            return json.loads(
                content,
            )
        except json.JSONDecodeError as e:
            raise ParseError(e)

    def get_instruction_segment(self) -> str:
        """Get the format instructions for the given decoder.

        This is a specification to the LLM that tells it how to shape its response
        so that the response can be structured properly using the given decoder.
        """
        format_instructions = (
            "Please output the extracted information in JSON format. Do not output"
            " anything except for the extracted information. Do not add any clarifying"
            " information. Do not add any fields that are not in the schema. If the"
            " text contains attributes that do not appear in the schema, please ignore"
            " them. All output must be in JSON format and follow the schema specified"
            " above."
        )
        if self.use_tags:
            format_instructions += " Wrap the JSON in <json> tags."
        return format_instructions
