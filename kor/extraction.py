from typing import Any, Type, Union

from langchain.chains import LLMChain
from langchain.schema import BaseLanguageModel

from kor.encoders import Encoder, initialize_encoder
from kor.nodes import AbstractSchemaNode
from kor.prompts import create_langchain_prompt
from kor.type_descriptors import TypeDescriptor, initialize_type_descriptors

# PUBLIC API


def create_extraction_chain(
    llm: BaseLanguageModel,
    node: AbstractSchemaNode,
    *,
    encoder_or_encoder_class: Union[Type[Encoder], Encoder, str] = "csv",
    type_descriptor: Union[TypeDescriptor, str] = "typescript",
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
        encoder_kwargs: Keyword arguments to pass to the encoder class

    Returns:
        A langchain chain
    """
    encoder = initialize_encoder(encoder_or_encoder_class, node, **encoder_kwargs)
    type_descriptor_to_use = initialize_type_descriptors(type_descriptor)
    return LLMChain(
        llm=llm, prompt=create_langchain_prompt(node, encoder, type_descriptor_to_use)
    )
