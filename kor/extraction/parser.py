from __future__ import annotations

from typing import List, Optional

from pydantic import Extra

from kor.encoders import Encoder
from kor.exceptions import ParseError
from kor.extraction.typedefs import Extraction
from kor.nodes import Object
from kor.validators import Validator

try:
    from langchain.output_parsers.base import BaseOutputParser
except ImportError:
    from langchain.schema import BaseOutputParser  # type: ignore


class KorParser(BaseOutputParser):
    """A Kor langchain parser integration.

    This parser can use any of Kor's encoders to support encoding/decoding
    different data formats.
    """

    encoder: Encoder
    schema_: Object
    validator: Optional[Validator] = None

    @property
    def _type(self) -> str:
        """Declare the type property."""
        return "KorEncoder"

    def parse(self, text: str) -> Extraction:
        """Parse the text."""
        try:
            data = self.encoder.decode(text)
        except ParseError as e:
            return {"data": {}, "raw": text, "errors": [e], "validated_data": {}}

        key_id = self.schema_.id

        errors: List[Exception]

        if key_id not in data:
            if data:  # We got something parsed, but it doesn't match the schema.
                errors = [
                    ParseError(
                        "The LLM has returned structured data which does not match the"
                        " expected schema. Providing additional examples may help"
                        " improve the parse."
                    )
                ]
            else:
                errors = []
            return {"data": {}, "raw": text, "errors": errors, "validated_data": {}}

        obj_data = data[key_id]

        if self.validator:
            validated_data, errors = self.validator.clean_data(obj_data)
        else:
            validated_data, errors = {}, []

        return {
            "data": data,
            "raw": text,
            "errors": errors,
            "validated_data": validated_data,
        }

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True
