from typing import Any, List, Mapping, Sequence, Tuple, Type, Union, Literal

from kor.nodes import AbstractSchemaNode

from .csv_data import CSVEncoder
from .json_data import JSONEncoder
from .typedefs import Encoder, SchemaBasedEncoder
from .xml import XMLEncoder

_ENCODER_REGISTRY: Mapping[str, Type[Encoder]] = {
    "csv": CSVEncoder,
    "xml": XMLEncoder,
    "json": JSONEncoder,
}

# PUBLIC API


InputEncoding = Union[Literal["text"], None]


def input_encoder(text: str, input_encoding: InputEncoding) -> str:
    """An encoder for the input text."""
    if input_encoding == "text":
        return 'Text: """"\n' + text + '\n"""'
    elif input_encoding is None:
        return text
    else:
        raise NotImplementedError(f'No support for input encoding "{input_encoding}"')


def encode_examples(
    examples: Sequence[Tuple[str, str]], encoder: Encoder, input_encoding: InputEncoding
) -> List[Tuple[str, str]]:
    """Encode the output using the given encoder."""

    return [
        (input_encoder(input_example, input_encoding), encoder.encode(output_example))
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
        encoder_name = encoder_or_encoder_class.lower()
        if encoder_name not in _ENCODER_REGISTRY:
            raise ValueError(
                f"Unknown encoder {encoder_name}. "
                f"Use one of {sorted(_ENCODER_REGISTRY)}"
            )
        encoder_or_encoder_class = _ENCODER_REGISTRY[encoder_name]
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
