from typing import Any

from langchain import BasePromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import BaseOutputParser
from langchain.schema import BaseLanguageModel, PromptValue
from pydantic import Extra

from kor.encoders import Encoder
from kor.nodes import AbstractInput
from kor.prompts import (
    STANDARD_EXTRACTION_TEMPLATE,
    ExtractionPromptValue,
)


class ExtractionPromptTemplate(BasePromptTemplate):
    """Extraction prompt template."""

    node: AbstractInput

    def format_prompt(self, text: str) -> PromptValue:
        """Format the prompt."""
        return ExtractionPromptValue(
            template=STANDARD_EXTRACTION_TEMPLATE, user_input=text, node=self.node
        )

    def format(self, **kwargs: Any) -> str:
        """Implementation of deprecated format method."""
        raise NotImplementedError()

    @property
    def _prompt_type(self) -> str:
        """Prompt type."""
        return "ExtractionPromptTemplate"


class KorParser(BaseOutputParser):
    """A Kor langchain parser integration.

    This parser can use any of Kor's encoders to support encoding/decoding
    different data formats.
    """

    encoder: Encoder

    @property
    def _type(self) -> str:
        """Declare the type property."""
        return "KorEncoder"

    def parse(self, text: str) -> Any:
        """Parse the text."""
        return self.encoder.decode(text)

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True


# PUBLIC API


def create_langchain_prompt(encoder: Encoder) -> ExtractionPromptTemplate:
    """Create a langchain style prompt with specified encoder."""
    return ExtractionPromptTemplate(
        input_variables=["text"],
        node=encoder.node,
        output_parser=KorParser(encoder=encoder),
    )


def create_extraction_chain(llm: BaseLanguageModel, encoder: Encoder) -> LLMChain:
    """Creat an extraction chain."""
    return LLMChain(llm=llm, prompt=create_langchain_prompt(encoder))
