"""Module that contains Kor flavored encoders/decoders for CSV data.

The code will need to eventually support handling some form of nested objects,
via either JSON encoded column values or by breaking down nested attributes
into additional columns (likely both methods).
"""
import csv
from io import StringIO
from typing import Any, Dict, List, Mapping, Sequence, cast


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


# PUBLIC API


class CSVEncoder:
    def __init__(self, fieldnames: Sequence[str]) -> None:
        """Initialize a CSV encoder with fieldnames."""
        self.fieldnames = fieldnames

    def encode(self, data: Sequence[Mapping[str, Any]]) -> str:
        """Encode the data."""
        return _encode(self.fieldnames, data)

    def decode(self, text: str) -> List[Dict[str, Any]]:
        """Decode the text."""
        return _decode(self.fieldnames, text)
