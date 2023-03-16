import json
from typing import List, Sequence, Tuple

from kor.encoders.typedefs import Encoder


class JSONEncoder(Encoder):
    def encode(self, examples: Sequence[Tuple[str, str]]) -> str:
        """Encode."""
        return json.dumps(examples)

    def decode(self, text: str) -> List[Tuple[str, str]]:
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
