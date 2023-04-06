from typing import Any, Optional, Type, Union

from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import BaseLanguageModel

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
    instruction_template: Optional[PromptTemplate] = None,
    **encoder_kwargs: Any,
) -> LLMChain:
    """Create an extraction chain.
    
    Args:
        llm: the language model used for extraction
        node: the schematic description of what to extract from text
        encoder_or_encoder_class: Either an encoder instance, an encoder class
                                  or a string representing the encoder class
        type_descriptor: either a TypeDescriptor or a string representing the type \
                         descriptor name
        validator: optional validator to use for validation
        input_formatter: the formatter to use for encoding the input. Used for \
                         both input examples and the text to be analyzed.
            * `None`: use for single sentences or single paragraph, no formatting
            * `triple_quotes`: for long text, surround input with \"\"\"
            * `text_prefix`: for long text, triple_quote with `TEXT: ` prefix
            * `Callable`: user provided function
        instruction_template: optional prompt template to use, use to over-ride prompt
             used for generating the instruction section of the prompt.
             It accepts 2 optional input variables:
             * "type_description": type description of the node (from TypeDescriptor)
             * "format_instructions": information on how to format the output
               (from Encoder)
        encoder_kwargs: Keyword arguments to pass to the encoder class

    Returns:
        A langchain chain
        
        
    Examples:
    
    .. code-block:: python
  
        # For CSV encoding
        chain = create_extraction_chain(llm, node, encoder_or_encoder_class="csv")
    
        # For JSON encoding
        chain = create_extraction_chain(llm, node, encoder_or_encoder_class="JSON",
                                        input_formatter="triple_quotes")
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
            validator=validator,
            instruction_template=instruction_template,
            input_formatter=input_formatter,
        ),
    )
