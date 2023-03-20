from typing import Any, Type, Union

from langchain.chains import LLMChain
from langchain.schema import BaseLanguageModel

from kor.encoders import Encoder, initialize_encoder
from kor.nodes import AbstractSchemaNode
from kor.prompts import create_langchain_prompt
from kor.type_descriptors import TypeDescriptor

# PUBLIC API


def create_extraction_chain(
    llm: BaseLanguageModel,
    schema: AbstractSchemaNode,
    encoder_or_encoder_class: Union[Type[Encoder], Encoder, str] = "json",
    type_descriptor: Union[TypeDescriptor, str] = "typescript",
    **encoder_kwargs: Any,
) -> LLMChain:
    """Create an extraction chain."""
    encoder = initialize_encoder(encoder_or_encoder_class, schema, **encoder_kwargs)
    return LLMChain(llm=llm, prompt=create_langchain_prompt(encoder, type_descriptor))
