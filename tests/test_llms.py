from kor.llm_utils import parse_llm_response
import pytest


@pytest.mark.parametrize(
    "test_input,output",
    [
        ("", None),
        ("<123>", None),
        ("<1>", "1"),
        ("<2>", "2"),
        ("<4>", None),
        ("qwd<1>", None),
        ("   <1> \n", "1"),
    ],
)
def test_parse_llm_response(test_input, output):
    """Parse LLM response."""
    allowed_options = ["1", "2", "3"]
    assert parse_llm_response(test_input, allowed_options) == output
