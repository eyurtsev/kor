"""Module that contains Kor flavored encoders/decoders for CSV data.

The code will need to eventually support handling some form of nested objects,
via either JSON encoded column values or by breaking down nested attributes
into additional columns (likely both methods).
"""
from io import StringIO
from typing import Any, Dict, List

import pandas as pd

from kor.encoders.typedefs import Encoder
from kor.nodes import AbstractInput, Object

DELIMITER = "|"


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
        """Attach node to the encoder to allow the encoder to understand schema."""
        super().__init__(node)

        # Verify that if we have an Object then none of its attributes are lists or objects
        # as that functionality is not yet supported.
        if isinstance(node, Object):
            for attribute in node.attributes:
                if attribute.many or isinstance(attribute, Object):
                    raise AssertionError(
                        "CSV Encoder does not yet support embedded lists or "
                        f"objects (attribute `{attribute.id}`)."
                    )

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
            " Only output the table. Output an opening <table> tag before the table and"
            " a closing </table> after the table. Do not output anything except for the"
            " table. Do not add any clarifying information. Output must follow the"
            " schema above. Do not add any additional columns that do not appear in the"
            " schema. If a column corresponds to an array or an object, use a JSON"
            " encoding to encode its value."
        )
