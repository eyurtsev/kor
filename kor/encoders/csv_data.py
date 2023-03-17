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

DELIMITER = "|"


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


def _assert_object_is_supported(node: AbstractInput) -> None:
    """Assert that the node is an object and that it has only flat attributes."""
    if not isinstance(node, Object):
        return

    for attribute in node.attributes:
        if attribute.many or isinstance(attribute, Object):
            raise AssertionError(
                "CSV Encoder does not yet support embedded lists or "
                f"objects (attribute `{attribute.id}`)."
            )


# PUBLIC API


class CSVEncoder(Encoder):
    """CSV encoder."""

    def __init__(self, node: AbstractInput) -> None:
        """Attach node to the encoder to allow the encoder to understand schema."""
        super().__init__(node)
        _assert_object_is_supported(self.node)

    def encode(self, data: Any) -> str:
        """Encode the data."""
        if not isinstance(data, dict):
            raise TypeError(f"Was expecting a dictionary got {type(data)}")

        expected_key = self.node.id

        if expected_key not in data:
            raise AssertionError(f"Expected a key: `{expected_key} to appear in data.")

        if isinstance(self.node, Object):
            field_names = _extract_top_level_fieldnames(self.node)
        else:
            field_names = [self.node.id]

        data_to_output = data[expected_key]

        if not isinstance(data_to_output, list):
            # Should always output records for pd.Dataframe
            data_to_output = [data_to_output]
        return (
            "<table>\n"
            + pd.DataFrame(data_to_output, columns=field_names).to_csv(
                index=False,
                sep=DELIMITER,
            )
            + "</table>"
        )

    def decode(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Decode the text."""
        text = (
            text.strip().removeprefix("<table>").removesuffix("</table>").lstrip("\n")
        )
        with StringIO(text) as buffer:
            records = pd.read_csv(
                buffer, dtype=str, keep_default_na=False, sep=DELIMITER
            ).to_dict(orient="records")

        namespace = self.node.id
        return {namespace: records}

    def get_instruction_segment(self) -> str:
        """Format instructions."""
        return (
            "Please output the extracted information in CSV format in Excel dialect."
            "Only output the table. "
            "Precede the table with a <table> tag and use a closing tag </table> after the table."
            "Do not output anything except for the table. "
            "Do not add any clarifying information. "
            "All output must be in CSV format and follow the schema specified above. "
            "Do not add any additional columns that do not appear in the schema. "
            "If the attribute is an array or an object, please JSON encode it."
        )
