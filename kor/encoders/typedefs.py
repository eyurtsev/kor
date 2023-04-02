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
    """Abstract interface for an encoder.

    The encoder is responsible for encoding and decoding the Output
    portion of examples provided to the LLM.

    It must implement a method called get_instruction_segment that
    contains instructions for the LLM on how to format its output.
    """

    @abc.abstractmethod
    def encode(self, data: Any) -> str:
        """Encode the data."""

    @abc.abstractmethod
    def decode(self, text: str) -> Any:
        """Decode the text."""

    @abc.abstractmethod
    def get_instruction_segment(self) -> str:
        """Get the format instructions for the given decoder.

        Used to guide the LLM on how to format its output.
        """
        raise NotImplementedError()


class SchemaBasedEncoder(Encoder, abc.ABC):
    """Abstract interface for an encoder that has the data schema.

    Inherit from this encoder if the encoder needs to know the schema
    of the data that's being encoded.
    """

    def __init__(self, node: AbstractSchemaNode, **kwargs: Any) -> None:
        """Attach node to the encoder to allow the encoder to understand schema."""
        self.node = node
