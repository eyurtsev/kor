"""Kor API for extraction related functionality."""
import asyncio
from typing import Any, Callable, List, Optional, Sequence, Type, Union, cast

from langchain.chains import LLMChain
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate

from kor.extraction.parser import KorParser

try:  # Handle breaking change in langchain
    from langchain.base_language import BaseLanguageModel
except ImportError:
    from langchain.schema import BaseLanguageModel  # type: ignore

from kor.encoders import Encoder, InputFormatter, initialize_encoder
from kor.extraction.typedefs import DocumentExtraction, Extraction
from kor.nodes import Object
from kor.prompts import create_langchain_prompt
from kor.type_descriptors import TypeDescriptor, initialize_type_descriptors
from kor.validators import Validator


async def _extract_from_document_with_semaphore(
    semaphore: asyncio.Semaphore,
    chain: LLMChain,
    document: Document,
    uid: str,
    source_uid: str,
) -> DocumentExtraction:
    """Extract from document with a semaphore to limit concurrency."""
    async with semaphore:
        extraction_result: Extraction = cast(
            Extraction, await chain.arun(document.page_content)
        )
        return {
            "uid": uid,
            "source_uid": source_uid,
            "data": extraction_result["data"],
            "raw": extraction_result["raw"],
            "validated_data": extraction_result["validated_data"],
            "errors": extraction_result["errors"],
        }


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
    verbose: Optional[bool] = None,
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
        verbose: if provided, sets the verbosity on the chain, otherwise default
                 verbosity of the chain will be used
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

    chain_kwargs = {}
    if verbose is not None:
        chain_kwargs["verbose"] = verbose

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
        output_parser=KorParser(encoder=encoder, validator=validator, schema_=node),
        **chain_kwargs,
    )


async def extract_from_documents(
    chain: LLMChain,
    documents: Sequence[Document],
    *,
    max_concurrency: int = 1,
    use_uid: bool = False,
    extraction_uid_function: Optional[Callable[[Document], str]] = None,
    return_exceptions: bool = False,
) -> List[Union[DocumentExtraction, Exception]]:
    """Run extraction through all the given documents.

    Attention: When using this function with a large number of documents, mind the bill
               since this can use a lot of tokens!

    Concurrency is currently limited using a semaphore. This is a temporary
    and can be changed to a queue implementation to support a non-materialized stream
    of documents.

    Args:
        chain: the extraction chain to use for extraction
        documents: the documents to run extraction on
        max_concurrency: the maximum number of concurrent requests to make,
                         uses a semaphore to limit concurrency
        use_uid: If True, will use a uid attribute in metadata if it exists
                          will raise error if attribute does not exist.
                 If False, will use the index of the document in the list as the uid
        extraction_uid_function: Optional function to use to generate the uid for
             a given DocumentExtraction. If not provided, will use the uid
             of the document.
        return_exceptions: named argument passed to asyncio.gather

    Returns:
        A list of extraction results
        if return_exceptions = True, the exceptions may be returned as well.
    """
    semaphore = asyncio.Semaphore(value=max_concurrency)

    tasks = []
    for idx, doc in enumerate(documents):
        if use_uid:
            source_uid = doc.metadata.get("uid")
            if source_uid is None:
                raise ValueError(
                    f"uid not found in document metadata for document {idx}"
                )
            # C
            source_uid = str(source_uid)
        else:
            source_uid = str(idx)

        extraction_uid = (
            extraction_uid_function(doc) if extraction_uid_function else source_uid
        )

        tasks.append(
            asyncio.ensure_future(
                _extract_from_document_with_semaphore(
                    semaphore, chain, doc, extraction_uid, source_uid
                )
            )
        )

    results = await asyncio.gather(*tasks, return_exceptions=return_exceptions)
    return results
