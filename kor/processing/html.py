"""Code to pre-process and HTML"""

from bs4 import BeautifulSoup
import markdownify


def get_mini_html(content: str) -> str:
    """Get HTML text."""
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


def convert_html(html: str) -> str:
    """Clean up HTML."""
    html = get_mini_html(html)
    # return html
    md = markdownify.markdownify(html)
    return md
