"""Load and chunk HTMLs with potential pre-processing to clean the html."""

import re
from typing import Tuple

from langchain.schema import Document

from kor.documents.typedefs import AbstractDocumentProcessor

# Regular expression pattern to detect multiple new lines in a row with optional
# whitespace in between
CONSECUTIVE_NEW_LINES = re.compile(r"\n(\s*\n)+", flags=re.UNICODE)


def _get_mini_html(html: str, *, tags_to_remove: Tuple[str, ...] = tuple()) -> str:
    """Clean up HTML tags."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError(
            "Please install BeautifulSoup to use the HTML document processor. "
            "You can do so by running `pip install beautifulsoup4`."
        )
    # Parse the HTML document using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Remove all CSS stylesheets
    for stylesheet in soup.find_all("link", rel="stylesheet"):
        stylesheet.extract()

    for tag_to_remove in tags_to_remove:
        # Remove all matching tags
        for tag in soup.find_all(tag_to_remove):
            tag.extract()

    new_html = repr(soup)
    return new_html


def _clean_html(html: str, *, tags_to_remove: Tuple[str, ...] = tuple()) -> str:
    """Clean up HTML and convert to markdown using markdownify."""
    try:
        import markdownify
    except ImportError:
        raise ImportError(
            "Please install markdownify to use the HTML document processor. "
            "You can do so by running `pip install markdownify`."
        )

    html = _get_mini_html(html, tags_to_remove=tags_to_remove)
    md = markdownify.markdownify(html)
    return CONSECUTIVE_NEW_LINES.sub("\n\n", md).strip()


## PUBLIC API


class MarkdownifyHTMLProcessor(AbstractDocumentProcessor):
    """A preprocessor to clean HTML and convert to markdown using markdownify."""

    def __init__(
        self,
        tags_to_remove: Tuple[str, ...] = ("svg", "img", "script", "style"),
    ) -> None:
        """Initialize the preprocessor.

        Args:
            tags_to_remove: A tuple of tags to remove from the HTML
        """
        self.tags_to_remove = tags_to_remove

    def process(self, document: Document) -> Document:
        """Clean up HTML and convert to markdown using markdownify.

        Args:
            document: a document with HTML content

        Returns:
            The cleaned HTML
        """
        new_document = document.copy()
        new_document.page_content = _clean_html(
            document.page_content, tags_to_remove=self.tags_to_remove
        )
        return new_document
