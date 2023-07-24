"""Module that contains Kor flavored encoders/decoders for CSV data.
The code supports handling some form of nested objects,
via JSON-encoded column values for nested attributes.
"""

import json
from io import StringIO
from typing import Any, Dict, List

import pandas as pd

from kor.encoders.typedefs import SchemaBasedEncoder
from kor.encoders.utils import unwrap_tag, wrap_in_tag
from kor.exceptions import ParseError
from kor.nodes import AbstractSchemaNode, Object

DELIMITER = "|"


def _extract_top_level_fieldnames(node: AbstractSchemaNode) -> List[str]:
    """Temporary schema description for CSV extraction."""
    if isinstance(node, Object):
        return [attributes.id for attributes in node.attributes]
    else:
        return [node.id]


def _nested_attribute_to_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert nested attributes to JSON strings."""
    json_data = {}
    for key, value in data.items():
        if isinstance(value, (list, dict)):
            json_data[key] = json.dumps(value)
        else:
            json_data[key] = value
    return json_data


def _json_to_nested_attribute(data: Dict[str, str]) -> Dict[str, Any]:
    """Convert JSON strings to nested attributes."""
    nested_data = {}
    for key, value in data.items():
        try:
            nested_data[key] = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            nested_data[key] = value
    return nested_data


# PUBLIC API

class CSVEncoder(SchemaBasedEncoder):
    """CSV encoder."""

    def __init__(self, node: AbstractSchemaNode, use_tags: bool = False) -> None:
        """Attach node to the encoder to allow the encoder to understand schema.
        Args:
            node: The schema node to attach to the encoder.
            use_tags: Whether to wrap the output in tags. This may help identify
                      the table content in cases when the model attempts to add
                      clarifying explanations.
        """
        super().__init__(node)
        self.use_tags = use_tags

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

        json_data_to_output = [_nested_attribute_to_json(item) for item in data_to_output]

        table_content = pd.DataFrame(json_data_to_output, columns=field_names).to_csv(
            index=False, sep=DELIMITER
        )

        if self.use_tags:
            return wrap_in_tag("csv", table_content)

        return table_content

    def decode(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Decode the text."""
        # First get the content between the table tags
        if self.use_tags:
            table_str = unwrap_tag("csv", text)
        else:
            table_str = text

        if table_str:
            with StringIO(table_str) as buffer:
                try:
                    df = pd.read_csv(
                        buffer,
                        dtype=str,
                        keep_default_na=False,
                        sep=DELIMITER,
                        skipinitialspace=True,
                    )
                except Exception as e:
                    raise ParseError(e)

            records = df.to_dict(orient="records")
            nested_records = [_json_to_nested_attribute(record) for record in records]
        else:
            nested_records = []

        namespace = self.node.id
        return {namespace: nested_records}

    def get_instruction_segment(self) -> str:
        """Format instructions."""
        instructions = [
            "Please output the extracted information in CSV format in Excel dialect.",
            f"Please use a {DELIMITER} as the delimiter.",
            "If a column corresponds to an array or an object, use a JSON encoding to "
            "encode its value.",
        ]

        if self.use_tags:
            instructions.append(
                "Please output a <csv> tag before and a closing </csv> after the table."
            )

        instructions.extend(
            [
                "\n",
                "Do NOT add any clarifying information.",
                "Output MUST follow the schema above.",
                "Do NOT add any additional columns that do not appear in the schema.",
            ]
        )

        return " ".join(instructions)
