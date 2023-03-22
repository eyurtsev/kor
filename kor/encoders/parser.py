from __future__ import annotations

from typing import Any, Dict

from langchain.output_parsers import BaseOutputParser
from pydantic import Extra

from kor.encoders import Encoder
from kor.encoders.exceptions import ParseError


class KorParser(BaseOutputParser):
    """A Kor langchain parser integration.

    This parser can use any of Kor's encoders to support encoding/decoding
    different data formats.
    """

    encoder: Encoder

    @property
    def _type(self) -> str:
        """Declare the type property."""
        return "KorEncoder"

    def parse(self, text: str) -> Dict[str, Any]:
        """Parse the text."""
        try:
            data = self.encoder.decode(text)
        except ParseError as e:
            return {"data": {}, "raw": text, "errors": [repr(e)]}

        return {
            "data": data,
            "raw": text,
            "errors": [],
        }

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True
