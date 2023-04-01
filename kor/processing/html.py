"""Code to pre-process and HTML"""
import markdownify
from bs4 import BeautifulSoup
from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from typing import List, Optional, Sequence, Union


def _get_mini_html(content: str) -> str:
    """Clean up HTML content."""
    # Parse the HTML document using BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Remove all CSS stylesheets
    for stylesheet in soup.find_all("link", rel="stylesheet"):
        stylesheet.extract()

    elements_to_remove = ("img", "path", "svg", "style")

    for element_to_remove in elements_to_remove:
        # Remove all image elements
        for img in soup.find_all(element_to_remove):
            img.extract()

    new_html = repr(soup)
    return new_html


def _convert_html(html: str) -> str:
    """Clean up HTML and convert to markdown using markdownify."""
    html = _get_mini_html(html)
    # return html
    md = markdownify.markdownify(html)
    return md


## PUBLIC API


def download_html(url: str) -> str:
    """Download HTML from a URL."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="load")
        # Wait for the page to finish rendering
        html = page.content()
        browser.close()
    return html


async def a_download_html(url: str) -> str:
    """Download an HTML from a URL."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="load")
        html_content = await page.content()
        await browser.close()
    return html_content


class HTMLToMarkDown(BaseLoader):
    """A loader that converts HTML to Markdown.
    
    This lolader
    
    
    """

    def __init__(self, htmls: Union[Sequence[str], Sequence[Document]]) -> None:
        """Convert HTML to markdown."""
        self.htmls = htmls

    def load(self) -> List[Document]:
        """Load data into document objects."""
        loaded_docs = []
        for text in self.htmls:
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
            _text_splitter: TextSplitter = RecursiveCharacterTextSplitter(chunk_size=600)
        else:
            _text_splitter = text_splitter
        docs = self.load()
        return _text_splitter.split_documents(docs)
