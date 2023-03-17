"""Module that contains Kor flavored encoders/decoders for CSV data.

The code will need to eventually support handling some form of nested objects,
via either JSON encoded column values or by breaking down nested attributes
into additional columns (likely both methods).
"""
import csv
from io import StringIO
from typing import Any, Dict, List, Mapping, Sequence, cast

import pandas as pd

from kor.encoders.typedefs import Encoder
from kor.nodes import AbstractInput, Object

DELIMITER = ","


def _encode(fieldnames: Sequence[str], data: Sequence[Mapping[str, Any]]) -> str:
    """Encode CSV."""
    with StringIO() as string_io:
        writer = csv.DictWriter(string_io, fieldnames, delimiter=DELIMITER)
        writer.writeheader()
        writer.writerows(data)
        encoded_string = string_io.getvalue()
    return encoded_string


def _decode(fieldnames: Sequence[str], csv_text: str) -> List[Dict[str, Any]]:
    """Decode CSV text using the given fieldnames."""
    with StringIO(csv_text) as s:
        reader = csv.DictReader(s, fieldnames=fieldnames, delimiter=DELIMITER)
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

    def encode(self, data: Any) -> str:
        """Encode the data."""
        if isinstance(data, dict):
            data = data["personal_info"]

        if not isinstance(self.node, Object):
            raise AssertionError()

        # new_records = []
        #
        # for attribute in self.node.attributes:
        #     attribute.id
        #
        # for record in data:
        #
        #
        #
        #
        # fieldnames = _extract_top_level_fieldnames(self.node)
        return pd.DataFrame(data, columns=fieldnames).to_csv(index=False)

    def decode(self, text: str) -> List[Dict[str, Any]]:
        """Decode the text."""
        with StringIO(text) as s:
            return pd.read_csv(s).to_dict(orient="records")

    def get_instruction_segment(self) -> str:
        """Format instructions."""
        return (
            "Please output the extracted information in CSV format in Excel dialect. "
            "Do not output anything except for the extracted information. "
            "Do not add any clarifying information. "
            "All output must be in CSV format and follow the schema specified above."
            "If the attribute is an array or an object, please JSON encode it."
        )
