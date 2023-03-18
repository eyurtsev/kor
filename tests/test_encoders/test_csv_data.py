from kor.encoders.csv_data import _get_table_content


def test_extract_table_content() -> None:
    # Test with an empty string
    assert _get_table_content("") is None

    # Test with a string that doesn't contain a <table> tag
    assert _get_table_content("This is some text.") is None

    # Test with a string that contains a <table> tag but no </table> tag
    assert _get_table_content("<table>test") is None

    assert _get_table_content("<table>hello</table>") == "hello"
    assert _get_table_content("prefix<table>hello</table>suffix") == "hello"
