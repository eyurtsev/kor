"""Code to dynamically generate appropriate LLM prompts."""
from __future__ import annotations

from typing import Any, List, Literal, Tuple, Union, Optional
from pydantic import BaseModel

from langchain import BasePromptTemplate
from langchain.output_parsers import BaseOutputParser
from langchain.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    PromptValue,
    SystemMessage,
)
from pydantic import Extra

from kor.encoders import Encoder
from kor.encoders.encode import encode_examples
from kor.examples import generate_examples
from kor.nodes import AbstractInput
from kor.type_descriptors import TypeDescriptor

PromptFormat = Union[Literal["openai-chat"], Literal["string"]]


class ExtractionPromptValue(PromptValue):
    """Integration with langchain prompt format."""

    text: str
    encoder: Encoder
    type_descriptor: TypeDescriptor
    prefix: str = (
        "Your goal is to extract structured information from the user's input that"
        " matches the form described below. When extracting information please make"
        " sure it matches the type information exactly. Do not add any attributes that"
        " do not appear in the schema shown below."
    )

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def to_string(self) -> str:
        """Format the template to a string."""
        node = self.encoder.node
        instruction_segment = self.generate_instruction_segment(node)
        encoded_examples = self.generate_encoded_examples(node)
        formatted_examples: List[str] = []

        for in_example, output in encoded_examples:
            formatted_examples.extend(
                [
                    f"Input: {in_example}",
                    f"Output: {output}",
                ]
            )

        formatted_examples.append(f"Input: {self.text}\nOutput:")
        input_output_block = "\n".join(formatted_examples)
        return f"{instruction_segment}\n\n{input_output_block}"

    def to_messages(self) -> List[BaseMessage]:
        """Format the template to chat messages."""
        node = self.encoder.node
        instruction_segment = self.generate_instruction_segment(node)

        messages: List[BaseMessage] = [SystemMessage(content=instruction_segment)]
        encoded_examples = self.generate_encoded_examples(node)

        for example_input, example_output in encoded_examples:
            messages.extend(
                [
                    HumanMessage(content=example_input),
                    AIMessage(content=example_output),
                ]
            )

        messages.append(HumanMessage(content=self.text))
        return messages

    def generate_encoded_examples(self, node: AbstractInput) -> List[Tuple[str, str]]:
        """Generate encoded examples."""
        examples = generate_examples(node)
        return encode_examples(examples, self.encoder)

    def generate_instruction_segment(self, node: AbstractInput) -> str:
        """Generate the instruction segment of the extraction."""
        type_description = self.type_descriptor.describe(node)
        instruction_segment = self.encoder.get_instruction_segment()
        return f"{self.prefix}\n\n{type_description}\n\n{instruction_segment}"


class ExtractionPromptTemplate(BasePromptTemplate):
    """Extraction prompt template."""

    encoder: Encoder
    type_descriptor: TypeDescriptor

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def format_prompt(self, text: str) -> PromptValue:
        """Format the prompt."""
        return ExtractionPromptValue(
            text=text,
            encoder=self.encoder,
            type_descriptor=self.type_descriptor,
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


def create_langchain_prompt(
    encoder: Encoder, type_descriptor: TypeDescriptor
) -> ExtractionPromptTemplate:
    """Create a langchain style prompt with specified encoder."""
    return ExtractionPromptTemplate(
        input_variables=["text"],
        output_parser=KorParser(encoder=encoder),
        encoder=encoder,
        type_descriptor=type_descriptor,
    )
