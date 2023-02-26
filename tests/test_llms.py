import pytest

from kor.llm_utils import parse_llm_output


@pytest.mark.parametrize(
    "test_input,output",
    [
        # ("", {}),
        # ("<123>", {}),
        # ("<d>blah</d>", {"d": ["blah"]}),
        # ("<a>meow</a>,<b>woof</b>", {"a": ["meow"], "b": ["woof"]}),
        # ("   <a>meow</a>,<b>woof</b>\n", {"a": ["meow"], "b": ["woof"]}),
        # ("<a><b>b</b><c>c</c></a>", {}),
        ("<a><b>b</b><c>c</c></a><a><b>b2</b></a>", {}),
    ],
)
def test_parse_llm_response(test_input, output):
    """Parse LLM response."""
    assert parse_llm_output(test_input) == output
