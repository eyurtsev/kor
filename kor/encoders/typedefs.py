"""Type-definitions for encoders.

This file only contains the interface for encoders.

* Added a pre-built format instruction segment.
* May remove it at some point later or modify it if we discover that
  there are many ways of phrasing the format instructions.
"""
import abc
from typing import Any

from kor.nodes import AbstractSchemaNode


class Encoder(abc.ABC):
    @abc.abstractmethod
    def encode(self, data: Any) -> str:
        """Encode the examples."""

    @abc.abstractmethod
    def decode(self, text: str) -> Any:
        """Decode the examples."""

    @abc.abstractmethod
    def get_instruction_segment(self) -> str:
        """Format instruction segment."""
        raise NotImplementedError()


class SchemaBasedEncoder(Encoder):
    def __init__(self, node: AbstractSchemaNode, **kwargs: Any) -> None:
        """Attach node to the encoder to allow the encoder to understand schema."""
        self.node = node
