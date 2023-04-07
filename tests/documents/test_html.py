from typing import Optional, Tuple

import pytest
from langchain.schema import Document

from kor.documents.html import MarkdownifyHTMLTransformer


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
        preprocessor = MarkdownifyHTMLTransformer(tags_to_remove=tags)
    else:
        preprocessor = MarkdownifyHTMLTransformer()

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
    document = Document(page_content=html, metadata={"a": 1})
    processed_document = preprocessor.transform(document)
    assert isinstance(processed_document, Document)
    assert processed_document.page_content == expected
    assert processed_document.metadata == {"a": 1}
