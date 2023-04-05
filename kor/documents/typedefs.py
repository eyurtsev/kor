import abc


class AbstractHTMLPreprocessor(abc.ABC):
    """Preprocessor for HTML documents."""

    @abc.abstractmethod
    def process(self, html: str) -> str:
        """Process HTML document."""
