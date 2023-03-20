from typing import Any, List, Sequence, Tuple, Type, Union

from kor.nodes import AbstractSchemaNode

from .csv_data import CSVEncoder
from .json_data import JSONEncoder
from .typedefs import Encoder, SchemaBasedEncoder
from .xml import XMLEncoder

# PUBLIC API


def encode_examples(
    examples: Sequence[Tuple[str, str]], encoder: Encoder
) -> List[Tuple[str, str]]:
    """Encode the output using the given encoder."""
    return [
        (input_example, encoder.encode(output_example))
        for input_example, output_example in examples
    ]


def initialize_encoder(
    encoder_or_encoder_class: Union[Type[Encoder], Encoder, str],
    schema: AbstractSchemaNode,
    **kwargs: Any,
) -> Encoder:
    """Flexible way to initialize an encoder, used only for top level API.

    Args:
        encoder_or_encoder_class: Either an encoder instance, an encoder class
                                  or a string representing the encoder class.
        schema: The schema to use for the encoder.
        **kwargs: Keyword arguments to pass to the encoder class.

    Returns:
        An encoder instance
    """
    if isinstance(encoder_or_encoder_class, str):
        encoder_or_encoder_class = {
            "csv": CSVEncoder,
            "xml": XMLEncoder,
            "json": JSONEncoder,
        }[encoder_or_encoder_class.lower()]

    if isinstance(encoder_or_encoder_class, type(Encoder)):
        if issubclass(encoder_or_encoder_class, SchemaBasedEncoder):
            return encoder_or_encoder_class(schema, **kwargs)
        else:
            return encoder_or_encoder_class(**kwargs)
    elif isinstance(encoder_or_encoder_class, Encoder):
        if kwargs:
            raise ValueError("Unable to use kwargs with an encoder instance")
        return encoder_or_encoder_class
    else:
        raise TypeError(
            "Expected str, an encoder or encoder class, got"
            f" {type(encoder_or_encoder_class)}"
        )
