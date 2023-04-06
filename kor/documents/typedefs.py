import abc

from langchain.schema import Document


class AbstractDocumentTransformer(abc.ABC):
    """An interface for document transformers."""

    @abc.abstractmethod
    def transform(self, document: Document) -> Document:
        """Process document."""
        raise NotImplementedError()
