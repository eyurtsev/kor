from typing import Any

import pytest

from kor import JSONEncoder


@pytest.mark.parametrize(
    "node_data,expected",
    [
        ({"object": [{"number": ["1"]}]}, '{"object": [{"number": ["1"]}]}'),
        ({"object": [{"text": ["3"]}]}, '{"object": [{"text": ["3"]}]}'),
        (
            {"object": [{"selection": ["option"]}]},
            '{"object": [{"selection": ["option"]}]}',
        ),
    ],
)
def test_json_encoding(node_data: Any, expected: str) -> None:
    """Test JSON encoding. This is just json.dumps, so no need to test extensively."""
    json_encoder = JSONEncoder(use_tags=False)
    assert json_encoder.encode(node_data) == expected
    assert json_encoder.decode(expected) == node_data


def test_json_encoding_with_tags() -> None:
    """Test JSON encoder with content wrapped in tags."""
    json_encoder = JSONEncoder(use_tags=True)
    assert (
        json_encoder.encode({"object": [{"a": 1}]})
        == '<json>{"object": [{"a": 1}]}</json>'
    )
    assert json_encoder.decode('<json>{"object": [{"a": 1}]}</json>') == {
        "object": [{"a": 1}]
    }


def test_json_encoding_with_non_ascii_chars() -> None:
    """Test json encoder with chinese characters."""
    text = "我喜欢珍珠奶茶"

    # Test encoding / decoding with chinese characters and ensure_ascii = True
    json_encoder = JSONEncoder(use_tags=True, ensure_ascii=True)
    assert (
        json_encoder.encode(text)
        == '<json>"\\u6211\\u559c\\u6b22\\u73cd\\u73e0\\u5976\\u8336"</json>'
    )

    # Test encoding/decoding with chinese characters and ensure_ascii = False
    assert json_encoder.decode(json_encoder.encode(text)) == "我喜欢珍珠奶茶"

    json_encoder = JSONEncoder(use_tags=True, ensure_ascii=False)
    assert json_encoder.encode(text) == '<json>"我喜欢珍珠奶茶"</json>'
    assert json_encoder.decode('<json>"我喜欢珍珠奶茶"</json>') == text
