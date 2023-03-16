from kor.parsers import csv_data
from typing import Sequence, Mapping, Any
import pytest


@pytest.mark.parametrize(
    "data,output",
    [([{"a": 1}, {"b": 0}, {"a": 5}], "a,b\n1,\n,0\n5,\n"), ([], "a,b\n"),
     ([{"a": ",", "b": 5}], "a,b\n")
     ],
)
def test_encoding(data: Sequence[Mapping[str, Any]], output: str) -> None:
    """Test CSV Encodings."""
    assert csv_data.encode(["a", "b"], data, lineterminator="\n") == output


def test_raise_error_on_extra_fields() -> None:
    """Any fields that appear in the object better appear in the encoding.

    This may later change this behavior to make it convenient for a user to
    check extraction against selected fields of an object.

    Keep as strict for now to catch errors in the code.
    """
    with pytest.raises(ValueError):
        csv_data.encode(["a", "b"], [{"a": 1}, {"b": 0}])
