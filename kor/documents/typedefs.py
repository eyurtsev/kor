import abc

from langchain_core.documents import Document


class AbstractDocumentProcessor(abc.ABC):
    """An interface for document transformers."""

    @abc.abstractmethod
    def process(self, document: Document) -> Document:
        """Process document."""
        raise NotImplementedError()
