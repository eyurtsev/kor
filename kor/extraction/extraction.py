import asyncio
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.docstore.document import Document
from langchain.schema import BaseLanguageModel
from typing import Any, Optional, Type, Union, List

from kor.encoders import Encoder, InputFormatter, initialize_encoder
from kor.extraction.typedefs import DocumentExtraction
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


async def extract_from_documents(
    chain: LLMChain,
    documents: List[Document],
    *,
    max_concurrency: int = 1,
    use_uid: bool = True,
) -> List[DocumentExtraction]:
    """Run extraction through all the given documents.

    If a `uid` field is found in the document metadata, it will be used as the
    `uid` field in the extraction result.

    Add a `uid` field to the document metadata to allow associate the extraction
    result with the source document.

    Args:
        chain: the extraction chain to use for extraction
        documents: the documents to run extraction on
        max_concurrency: the maximum number of concurrent requests to make,
                         uses a semaphore to limit concurrency
        use_uid: If True, will use a uid attribute in metadata if it exists
                          will raise error if attribute does not exist.
                 If False, will use the index of the document in the list as the uid

    Returns:
        A list of extraction results
    """
    semaphore = asyncio.Semaphore(value=max_concurrency)

    async with semaphore:
        tasks = []
        for idx, doc in enumerate(documents):
            if use_uid:
                source_uid = doc.metadata.get("uid")
                if source_uid is None:
                    raise ValueError(
                        f"uid not found in document metadata for document {idx}"
                    )
            else:
                source_uid = str(idx)

            tasks.append((source_uid, chain.apredict_and_parse(text=doc.page_content)))

    results = await asyncio.gather(*tasks)

    extraction_results: List[DocumentExtraction] = []

    for result in results:
        source_uid, data = result
        extraction_results.append(DocumentExtraction(uid=source_uid, **data))

    return extraction_results
