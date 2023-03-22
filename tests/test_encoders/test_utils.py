from kor.encoders.utils import unwrap_tag, wrap_in_tag


def test_unwrap_tag() -> None:
    """Test unwrap_tag."""
    # Test with an empty string
    assert unwrap_tag("", "") is None

    # Test with a string that doesn't contain the tag
    assert unwrap_tag("table", "This is some text.") is None

    # Test with a string that does contain the tag
    assert unwrap_tag("table", "<table>hello</table>") == "hello"

    # Test with a string that does contain the tag and some stuff before and after
    assert unwrap_tag("table", "prefix<table>hello</table>suffix") == "hello"


def test_wrap_in_tag() -> None:
    """Test wrap_in_tag."""
    assert wrap_in_tag("table", "hello") == "<table>hello</table>"
