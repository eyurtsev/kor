from typing import Any, Callable, List, Literal, Mapping, Sequence, Tuple, Type, Union

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

# Use to denote different types of formatters for the input.
InputFormatter = Union[
    Literal["text_prefix"], Literal["triple_quotes"], None, Callable[[str], str]
]


# PUBLIC API


def format_text(text: str, input_formatter: InputFormatter = None) -> str:
    """An encoder for the input text.

    Args:
        text: the text to encode
        input_formatter: the formatter to use for the input
            * None: use for single sentences or single paragraphs, no formatting
            * triple_quotes: surround input with \"\"\", use for long text
            * text_prefix: same as triple_quote but with `TEXT: ` prefix
            * Callable: user provided function

    Returns:
        The encoded text if it was encoded
    """
    if input_formatter == "text_prefix":
        return 'Text: """\n' + text + '\n"""'
    elif input_formatter == "triple_quotes":
        return '"""\n' + text + '\n"""'
    elif input_formatter is None:
        return text
    else:
        raise NotImplementedError(
            f'No support for input encoding "{input_formatter}". '
            ' Use one of "long_text" or None.'
        )


def encode_examples(
    examples: Sequence[Tuple[str, str]],
    encoder: Encoder,
    input_formatter: InputFormatter = None,
) -> List[Tuple[str, str]]:
    """Encode the output using the given encoder."""

    return [
        (
            format_text(input_example, input_formatter=input_formatter),
            encoder.encode(output_example),
        )
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
