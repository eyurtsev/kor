import abc
from langchain.schema import Document
from typing import List


class AbstractDocumentTransformer(abc.ABC):
    """An interface for document transformers."""

    @abc.abstractmethod
    def transform(self, document: Document) -> Document:
        """Process document."""
        raise NotImplementedError()


class AbstractDocumentSplitter(abc.ABC):
    """An interface for splitting a document into chunks."""

    @abc.abstractmethod
    def split(self, document: Document) -> List[Document]:
        """Load document."""
        raise NotImplementedError()
