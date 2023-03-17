from typing import Any, Type, Union

import pytest

from kor.encoders.xml import XMLEncoder, _write_tag


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
    encoder = XMLEncoder(None)
    assert encoder.decode(xml_string) == output


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
    encoder = XMLEncoder(None)
    if isinstance(output, str):
        assert encoder.encode(obj) == output
    else:
        with pytest.raises(output):
            encoder.encode(obj)


def test_write_tag() -> None:
    """Verify XML encoding works as expected."""
    assert _write_tag("tag", "data") == "<tag>data</tag>"
    assert _write_tag("tag", ["data1", "data2"]) == "<tag>data1</tag><tag>data2</tag>"
    assert _write_tag("tag", {"key1": "value1"}) == "<tag><key1>value1</key1></tag>"
    assert (
        _write_tag("tag", {"key1": "value1", "key2": "value2"})
        == "<tag><key1>value1</key1><key2>value2</key2></tag>"
    )
    assert (
        _write_tag("tag", {"key1": "value1", "key2": ["a", "b"]})
        == "<tag><key1>value1</key1><key2>a</key2><key2>b</key2></tag>"
    )
