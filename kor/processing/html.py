"""Code to pre-process and HTML"""
import markdownify
from bs4 import BeautifulSoup
from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document
from langchain.text_splitter import TextSplitter, RecursiveCharacterTextSplitter
from typing import Union, Sequence, List, Optional


def _get_mini_html(content: str) -> str:
    """Clean up HTML content."""
    # Parse the HTML document using BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Remove all CSS stylesheets
    for stylesheet in soup.find_all("link", rel="stylesheet"):
        stylesheet.extract()

    # Remove all image elements
    for img in soup.find_all("img"):
        img.extract()

    # Remove all path elements
    for path in soup.find_all("path"):
        path.extract()

    # Remove all SVG elements
    for svg in soup.find_all("svg"):
        svg.extract()

    # Remove all style tags
    for style in soup.find_all("style"):
        style.extract()

    new_html = repr(soup)
    return new_html


def _convert_html(html: str) -> str:
    """Clean up HTML."""
    html = _get_mini_html(html)
    # return html
    md = markdownify.markdownify(html)
    return md


## PUBLIC API


class HTMLToMarkDown(BaseLoader):
    """A loader that converts HTML to Markdown."""

    def __init__(self, texts: Union[Sequence[str], Sequence[Document]]) -> None:
        """Convert HTML to markdown."""
        self.texts = texts

    def load(self) -> List[Document]:
        """Load data into document objects."""
        loaded_docs = []
        for text in self.texts:
            if isinstance(text, Document):
                new_document = text.copy()
                new_document.page_content = _convert_html(text.page_content)
                loaded_docs.append(new_document)
            elif isinstance(text, str):
                loaded_docs.append(Document(page_content=_convert_html(text)))
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
