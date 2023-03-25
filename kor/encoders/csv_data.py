"""Module that contains Kor flavored encoders/decoders for CSV data.

The code will need to eventually support handling some form of nested objects,
via either JSON encoded column values or by breaking down nested attributes
into additional columns (likely both methods).
"""

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

        # Verify that if we have an Object then none of its attributes are lists
        # or objects as that functionality is not yet supported.
        if isinstance(node, Object):
            for attribute in node.attributes:
                if attribute.many or isinstance(attribute, Object):
                    raise NotImplementedError(
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
        table_content = pd.DataFrame(data_to_output, columns=field_names).to_csv(
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
        else:
            records = []

        namespace = self.node.id
        return {namespace: records}

    def get_instruction_segment(self) -> str:
        """Format instructions."""
        instructions = [
            "Please output the extracted information in CSV format in Excel dialect.",
            f"Please use a {DELIMITER} as the delimiter."
            # TODO(Eugene): Add this when we start supporting embedded columns.
            # "If a column corresponds to an array or an object,
            # use a JSON encoding to "
            # "encode its value.",
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
