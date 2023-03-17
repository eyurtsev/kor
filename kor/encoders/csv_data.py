"""Module that contains Kor flavored encoders/decoders for CSV data.

The code will need to eventually support handling some form of nested objects,
via either JSON encoded column values or by breaking down nested attributes
into additional columns (likely both methods).
"""
import csv
from io import StringIO
from typing import Any, Dict, List, Mapping, Sequence, cast

from kor.nodes import AbstractInput, Object
from kor.encoders.typedefs import Encoder


def _encode(fieldnames: Sequence[str], data: Sequence[Mapping[str, Any]]) -> str:
    """Encode CSV."""
    with StringIO() as string_io:
        writer = csv.DictWriter(string_io, fieldnames)
        writer.writeheader()
        writer.writerows(data)
        encoded_string = string_io.getvalue()
    return encoded_string


def _decode(fieldnames: Sequence[str], csv_text: str) -> List[Dict[str, Any]]:
    """Decode CSV text using the given fieldnames."""
    with StringIO(csv_text) as s:
        reader = csv.DictReader(s, fieldnames=fieldnames)
        header = cast(Dict[str, str], next(reader))

        if set(header.values()) != set(fieldnames):
            raise ValueError(
                f"Difference between expected fieldnames: {fieldnames} and header"
                f" {header.values()}"
            )
        return list(row for row in reader)


def _extract_top_level_fieldnames(node: AbstractInput) -> List[str]:
    """Temporary schema description for CSV extraction."""
    if isinstance(node, Object):
        return [attributes.id for attributes in node.attributes]
    else:
        return [node.id]


# PUBLIC API


class CSVEncoder(Encoder):
    """CSV encoder."""

    def __init__(self, node: AbstractInput) -> None:
        super().__init__(node)
        self.fieldnames = _extract_top_level_fieldnames(node)

    def encode(self, data: Any) -> str:
        """Encode the data."""
        raise NotImplementedError()
        if isinstance(data, dict):
            # How to take care of this correctly?
            data = [data]

        if not isinstance(data, list):
            data = [data]
        return _encode(self.fieldnames, data)

    def decode(self, text: str) -> List[Dict[str, Any]]:
        """Decode the text."""
        return _decode(self.fieldnames, text)

    def get_instruction_segment(self) -> str:
        """Format instructions."""
        return (
            "Please output the extracted information in CSV format in Excel dialect."
            "Do not output anything except for the extracted information. "
            "Do not add any clarifying information. "
            "All output must be in CSV format and follow the schema specified above."
        )
