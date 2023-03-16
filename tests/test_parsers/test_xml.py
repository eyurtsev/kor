from typing import Any, Type, Union

import pytest

from kor.parsers.xml import decode, encode


@pytest.mark.parametrize(
    "xml_string,output",
    [
        ("", {}),
        ("<123>", {}),
        ("<d>blah</d>", {"d": ["blah"]}),
        ("<a>1</a><a>2</a>", {"a": ["1", "2"]}),
        ("<a>1</a><b>2</b>", {"a": ["1"], "b": ["2"]}),
        (
            "<a><a1>1</a1><a2>2</a2></a><b>2</b>",
            {"a": [{"a1": ["1"], "a2": ["2"]}], "b": ["2"]},
        ),
        (
            "<a><a1>1</a1><a2>2</a2></a><b>2</b><a><a1>1</a1></a>",
            {"a": [{"a1": ["1"], "a2": ["2"]}, {"a1": ["1"]}], "b": ["2"]},
        ),
    ],
)
def test_xml_decode(xml_string: str, output: Any) -> None:
    """Decode XML."""
    assert decode(xml_string) == output


@pytest.mark.parametrize(
    "obj,output",
    [
        ({}, ""),
        ("hello", TypeError),
        ({"obj": []}, ""),
        ({"obj": 5}, "<obj>5</obj>"),
        ({"obj": {"name": ["Eugene"]}}, "<obj><name>Eugene</name></obj>"),
        (
            {"obj": {"name": ["Eugene", "Vadym"]}},
            "<obj><name>Eugene</name><name>Vadym</name></obj>",
        ),
        (
            {"obj": [{"name": ["Eugene"]}, {"name": ["Vadym"]}]},
            "<obj><name>Eugene</name></obj><obj><name>Vadym</name></obj>",
        ),
        (
            {"obj": [{"name": ["Eugene"]}, {"name": ["Vadym"]}]},
            "<obj><name>Eugene</name></obj><obj><name>Vadym</name></obj>",
        ),
    ],
)
def test_xml_encode(obj: Any, output: Union[Type[Exception], str]) -> None:
    """Test XML encoding."""
    if isinstance(output, str):
        assert encode(obj) == output
    else:
        with pytest.raises(output):
            encode(obj)
