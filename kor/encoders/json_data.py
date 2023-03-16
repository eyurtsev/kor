import json
from typing import Any

from kor.encoders.typedefs import Encoder


class JSONEncoder(Encoder):
    def encode(self, data: Any) -> str:
        """Encode."""
        return json.dumps(data)

    def decode(self, text: str) -> Any:
        """Decode."""
        return json.loads(text)

    def get_instruction_segment(self) -> str:
        """Format instruction"""
        return (
            "Please output the extracted information in JSON format. "
            "Do not output anything except for the extracted information. "
            "Do not add any clarifying information. "
            "All output must be in JSON format and follow the schema specified above."
        )
