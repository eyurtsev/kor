from kor.documents.html import HTMLLoader, MarkDownifyHTMLPreprocessor
import pytest
from typing import Optional, Tuple


@pytest.mark.parametrize(
    "tags,expected",
    [
        (None, "Title\n\nTest"),  # Use default
        (tuple(), "Title\nSvg\nStyle\nScript\n\nTest"),
        (("title",), "Svg\nStyle\nScript\n\nTest"),
    ],
)
def test_markdownify_html_preprocessor(
    tags: Optional[Tuple[str, ...]], expected: str
) -> None:
    """Test the MarkDownifyHTMLPreprocessor."""
    if tags is not None:
        preprocessor = MarkDownifyHTMLPreprocessor(tags_to_remove=tags)
    else:
        preprocessor = MarkDownifyHTMLPreprocessor()

    html = """
    <html>
    <head>
    <title>Title</title>
    <svg>Svg</svg>
    <style>Style</style>
    <script>Script</script>
    </head>
    <body>
    <p>Test
    
    
    </p>
    </body>
    </html>
    """
    assert preprocessor.process(html) == expected


def test_html_loader() -> None:
    """Test the HTMLLoader."""
    html = """
    <html>
    <head>
    <title>Test</title>
    </head>
    <body>
    <p>Test</p>
    </body>
    </html>
    """

    # No pre-processor
    loader = HTMLLoader([html])
    docs = loader.load()
    assert len(docs) == 1
    assert docs[0].page_content == html

    # With callable
    loader = HTMLLoader([html], preprocessor=lambda x: "html" + x)
    docs = loader.load()
    assert len(docs) == 1
    assert docs[0].page_content == "html" + html

    # With pre-processor
    loader = HTMLLoader(
        [html], preprocessor=MarkDownifyHTMLPreprocessor(tags_to_remove=("title",))
    )
    docs = loader.load()
    assert len(docs) == 1
    assert docs[0].page_content == "Test"
