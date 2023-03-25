from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import Extra

from kor.encoders import Encoder
from kor.exceptions import ParseError
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

    def parse(self, text: str) -> Dict[str, Any]:
        """Parse the text."""
        try:
            data = self.encoder.decode(text)
        except ParseError as e:
            return {"data": {}, "raw": text, "errors": [e], "validated_data": {}}

        key_id = self.schema_.id

        if key_id not in data:
            return {"data": {}, "raw": text, "errors": [], "validated_data": {}}

        obj_data = data[key_id]

        if self.validator:
            validated_data, exceptions = self.validator.clean_data(obj_data)
        else:
            validated_data, exceptions = {}, []

        return {
            "data": data,
            "raw": text,
            "errors": exceptions,
            "validated_data": validated_data,
        }

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True
