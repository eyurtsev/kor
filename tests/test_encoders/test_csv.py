from typing import Any, Mapping, Sequence

import pytest

from kor.encoders import csv_data


@pytest.mark.parametrize(
    "data,output",
    [
        ([{"a": 1}, {"b": 0}, {"a": 5}], "a,b\r\n1,\r\n,0\r\n5,\r\n"),
        ([], "a,b\r\n"),
        ([{"a": ",", "b": 5}], 'a,b\r\n",",5\r\n'),
    ],
)
def test_encoding(data: Sequence[Mapping[str, Any]], output: str) -> None:
    """Test CSV Encodings."""
    assert csv_data._encode(["a", "b"], data) == output


def test_raise_error_on_extra_fields() -> None:
    """Any fields that appear in the object better appear in the encoding.

    This may later change this behavior to make it convenient for a user to
    check extraction against selected fields of an object.

    Keep as strict for now to catch errors in the code.
    """
    with pytest.raises(ValueError):
        csv_data._encode(["a", "b"], [{"a": 1}, {"b": 0}, {"c": 5}])


@pytest.mark.parametrize(
    "data,output",
    [
        (
            "a,b\n1,\n,0\n5,\n",
            [
                {"a": "1", "b": ""},
                {"a": "", "b": "0"},
                {"a": "5", "b": ""},
            ],
        ),
        (
            "a,b\n",
            [],
        ),
    ],
)
def test_decoding(data: str, output: Sequence[Mapping[str, Any]]) -> None:
    """Test CSV decoding."""
    assert csv_data._decode(["a", "b"], data) == output


def test_csv_encoder_class() -> None:
    """Test the CSV encoding/decoding interface."""
    encoder = csv_data.CSVEncoder(["a"])
    assert encoder.encode([{"a": 5}]) == "a\r\n5\r\n"
