"""Load and chunk HTMLs with potential pre-processing to clean the html."""

import markdownify
import re
from bs4 import BeautifulSoup
from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter
from typing import Callable, List, Optional, Sequence, Union, Tuple

from kor.documents.typedefs import AbstractHTMLPreprocessor

# Regular expression pattern to detect multiple new lines in a row with optional
# whitespace in between
CONSECUTIVE_NEW_LINES = re.compile(r"\n(\s*\n)+", flags=re.UNICODE)


def _get_mini_html(content: str, *, tags_to_remove: Tuple[str] = tuple()) -> str:
    """Clean up HTML content."""
    # Parse the HTML document using BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Remove all CSS stylesheets
    for stylesheet in soup.find_all("link", rel="stylesheet"):
        stylesheet.extract()

    for tags_to_remove in tags_to_remove:
        # Remove all matching tags
        for tag in soup.find_all(tags_to_remove):
            tag.extract()

    new_html = repr(soup)
    return new_html


def _clean_html(html: str, *, tags_to_remove: Tuple[str, ...] = tuple()) -> str:
    """Clean up HTML and convert to markdown using markdownify."""
    html = _get_mini_html(html, tags_to_remove=tags_to_remove)
    md = markdownify.markdownify(html)
    return CONSECUTIVE_NEW_LINES.sub("\n\n", md).strip()


## PUBLIC API


class MarkDownifyHTMLPreprocessor(AbstractHTMLPreprocessor):
    """A preprocessor to clean HTML and convert to markdown using markdownify."""

    def __init__(
        self, tags_to_remove: Tuple[str, ...] = ("svg", "img", "script", "style")
    ) -> None:
        """Initialize the preprocessor.

        Args:
            tags_to_remove: A tuple of tags to remove from the HTML
        """
        self.tags_to_remove = tags_to_remove

    def process(self, html: str) -> str:
        """Clean up HTML and convert to markdown using markdownify.

        Args:
            html: The HTML to clean

        Returns:
            The cleaned HTML
        """
        return _clean_html(html, tags_to_remove=self.tags_to_remove)


class HTMLLoader(BaseLoader):
    """Load and chunk HTMLs with potential pre-processing to clean the html."""

    def __init__(
        self,
        htmls: Union[Sequence[str], Sequence[Document]],
        preprocessor: Optional[
            Union[AbstractHTMLPreprocessor, Callable[[str], str]]
        ] = None,
    ) -> None:
        """Load with optional preprocessor.

        Args:
            htmls: A sequence of HTML strings or Document objects
                   Pass in Document objects if you want to preserve the metadata
            preprocessor: optional, preprocessor to clean the HTML
        """
        self.htmls = htmls
        self.preprocessor = preprocessor

    def _process_html(self, html: str) -> str:
        """A tiny wrapper to deal with different types of preprocessors.

        Args:
            html: The HTML to process

        Returns:
            processed HTML if a preprocessor is provided, otherwise the original HTML
        """
        if self.preprocessor:
            if isinstance(self.preprocessor, AbstractHTMLPreprocessor):
                return self.preprocessor.process(html)
            else:
                return self.preprocessor(html)
        else:
            return html

    def load(self) -> List[Document]:
        """Load data into document objects."""
        loaded_docs = []
        for text in self.htmls:
            if isinstance(text, Document):
                new_document = text.copy()
                new_document.page_content = self._process_html(text.page_content)
                loaded_docs.append(new_document)
            elif isinstance(text, str):
                loaded_docs.append(Document(page_content=self._process_html(text)))
            else:
                raise TypeError(f"Expected str or Document got {type(text)}")
        return loaded_docs

    def load_and_split(
        self, text_splitter: Optional[TextSplitter] = None
    ) -> List[Document]:
        """Load documents and split into chunks."""
        if text_splitter is None:
            _text_splitter: TextSplitter = RecursiveCharacterTextSplitter()
        else:
            _text_splitter = text_splitter
        docs = self.load()
        return _text_splitter.split_documents(docs)
