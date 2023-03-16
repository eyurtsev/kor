"""Module that contains Kor flavored encoders/decoders for CSV data.

The code will need to eventually support handling some form of nested objects,
via either JSON encoded column values or by breaking down nested attributes
into additional columns (likely both methods).
"""
import csv
from io import StringIO
from typing import Sequence, List, Dict, Any, Mapping


# PUBLIC API


def encode(
    fields: Sequence[str], data: Sequence[Mapping[str, Any]], lineterminator: str = "\r\n"
) -> str:
    """Encode CSV."""
    with StringIO() as string_io:
        writer = csv.DictWriter(
            string_io, fields, delimiter=",", lineterminator=lineterminator
        )
        writer.writeheader()
        writer.writerows(data)
        encoded_string = string_io.getvalue()
    return encoded_string


def decode(csv_text: str):
    """Decode"""
    with StringIO(csv_text) as s:
        reader = csv.DictReader()

    return data
