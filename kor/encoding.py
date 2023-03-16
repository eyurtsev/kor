import json
from typing import Sequence, Tuple, List, Callable, Any

from kor import Object
from kor.nodes import AbstractInput
from kor.parsers import xml, csv_data
from kor.parsers.typedefs import Encoder


def _extract_top_level_fieldnames(node: AbstractInput) -> List[str]:
    """Temporary schema description for CSV extraction."""
    if isinstance(node, Object):
        return [attributes.id for attributes in node.attributes]
    else:
        return [node.id]


class JSONEncoder(Encoder):
    def encode(self, examples: Sequence[Tuple[str, str]]) -> str:
        """Encode"""
        return json.dumps(examples)

    def decode(self, text: str) -> List[Tuple[str, str]]:
        """Decode"""
        return json.loads(text)

    def format_instruction_segment(self) -> str:
        """"""


# PUBLIC API


def encode_examples(
    node: AbstractInput, examples: Sequence[Tuple[str, str]], encoding: str
) -> List[Tuple[str, str]]:
    """Encode the output using the given encoder."""
    if encoding == "none":
        return list(examples)
    elif encoding == "JSON":
        encoder: Callable[[Any], str] = json.dumps
    elif encoding == "XML":
        encoder = xml.encode
    elif encoding == "CSV":
        fieldnames = _extract_top_level_fieldnames(node)
        encoder = csv_data.CSVEncoder(fieldnames=fieldnames).encode
    else:
        raise NotImplementedError(f"No support for encoding {encoding}")

    return [
        (input_example, encoder(output_example))
        for input_example, output_example in examples
    ]
