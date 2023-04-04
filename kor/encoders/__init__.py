"""Declare public interface for encoders.

An encoder follows the `Encoder` interface.

It can encode, decode and contains instructions about the encoding format for an LLM.
"""
from .csv_data import CSVEncoder
from .encode import InputFormatter, encode_examples, initialize_encoder
from .json_data import JSONEncoder
from .typedefs import Encoder, SchemaBasedEncoder
from .xml import XMLEncoder

__all__ = [
    "CSVEncoder",
    "encode_examples",
    "Encoder",
    "initialize_encoder",
    "InputFormatter",
    "JSONEncoder",
    "SchemaBasedEncoder",
    "XMLEncoder",
]
