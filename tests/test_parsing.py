from typing import Any

import pytest

from kor.parsing import parse_llm_output


@pytest.mark.parametrize(
    "test_input,output",
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
def test_parse_llm_response(test_input: str, output: Any) -> None:
    """Parse LLM response."""
    assert parse_llm_output(test_input) == output
