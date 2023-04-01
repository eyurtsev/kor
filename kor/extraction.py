from langchain.chains import LLMChain
from langchain.schema import BaseLanguageModel
from typing import Any, Optional, Type, Union

from kor.encoders import Encoder, InputFormatter, initialize_encoder
from kor.nodes import Object
from kor.prompts import create_langchain_prompt
from kor.type_descriptors import TypeDescriptor, initialize_type_descriptors
from kor.validators import Validator


# PUBLIC API


def create_extraction_chain(
    llm: BaseLanguageModel,
    node: Object,
    *,
    encoder_or_encoder_class: Union[Type[Encoder], Encoder, str] = "csv",
    type_descriptor: Union[TypeDescriptor, str] = "typescript",
    validator: Optional[Validator] = None,
    input_formatter: InputFormatter = None,
    **encoder_kwargs: Any,
) -> LLMChain:
    """Create an extraction chain.

    Args:
        llm: The language model used for extraction
        node: the schematic description of what to extract from text
        encoder_or_encoder_class: Either an encoder instance, an encoder class
                                  or a string representing the encoder class
        type_descriptor: The type descriptor to use. This can be either a TypeDescriptor
                          or a string representing the type descriptor name
        validator: optional validator to use for validation
        input_formatter: the formatter to use for encoding the input. Used for
                         both input examples and the text to be analyzed.
            * None: use for single sentences or single paragraph, no formatting
            * triple_quotes: for long text, surround input with \"\"\"
            * text_prefix: for long text, triple_quote with `TEXT: ` prefix
            * Callable: user provided function
        encoder_kwargs: Keyword arguments to pass to the encoder class

    Returns:
        A langchain chain
    """
    if not isinstance(node, Object):
        raise ValueError(f"node must be an Object got {type(node)}")
    encoder = initialize_encoder(encoder_or_encoder_class, node, **encoder_kwargs)
    type_descriptor_to_use = initialize_type_descriptors(type_descriptor)
    return LLMChain(
        llm=llm,
        prompt=create_langchain_prompt(
            node,
            encoder,
            type_descriptor_to_use,
            validator,
            input_formatter=input_formatter,
        ),
    )
